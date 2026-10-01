#!/usr/bin/env python3
"""Gera mockups das telas de um app Power Apps com a API de imagens da OpenAI.

Entrada: `mockups.json` (molde em `assets/mockups-molde.json`), escrito na etapa `/pp:mockups` pelo
`pp:agente-mockups`. Ele traz a paleta e a fonte do design system, a moldura do app (header,
navegação, notificações, pop-ups, loading) e uma entrada por tela ou estado de tela.

Saída: `<id>.png` por tela e `mockups.md` (galeria, "gerado — não editar"), na pasta do spec ou
em `mockups.pasta` do config. Imagem que já existe é pulada, salvo `--sobrescrever`.

Variáveis de ambiente:
  OPENAI_API_KEY      obrigatória para gerar; nunca em arquivo nem no chat
  OPENAI_IMAGE_MODEL  modelo de imagem (default gpt-image-2)
  OPENAI_BASE_URL     endpoint compatível com a API da OpenAI (default https://api.openai.com/v1;
                      exige https, salvo localhost)

Precedência: opção da linha de comando > variável de ambiente (só o modelo) > bloco `mockups` do
power-platform.config.json > default.

Erros da API: 429 e 5xx tentam de novo (com espera); 3xx, 400, 401, 403, 404, falha de rede e
falha de gravação interrompem a execução, porque se repetiriam em todas as telas. A galeria é
escrita mesmo assim, com as imagens que existem.

Saída: `caminho:lugar: ERRO|AVISO Mnnn mensagem`. Última linha: `N erro(s), M aviso(s)`.
Exit: 0 sem erro, 1 com erro (spec ou API), 2 uso incorreto (arquivo, config, chave, URL, teto).
"""
from __future__ import annotations

import argparse
import base64
import http.client
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

NOME_CONFIG = "power-platform.config.json"
MODELO_PADRAO = "gpt-image-2"
TAMANHO_PADRAO = "1536x1024"
QUALIDADE_PADRAO = "high"
URL_PADRAO = "https://api.openai.com/v1"
MAX_IMAGENS_PADRAO = 20
TIMEOUT_PADRAO = 300
TENTATIVAS_EXTRAS = 2
ESPERA_MAX = 30
LIMITE_RESPOSTA = 50_000_000
ASSINATURA_PNG = b"\x89PNG\r\n\x1a\n"
TAMANHOS_SEGUROS = {"1024x1024", "1536x1024", "1024x1536", "auto"}
QUALIDADES = {"low", "medium", "high", "xhigh", "max", "auto"}
ARESTA_MAX = 3840
PIXELS_MIN, PIXELS_MAX = 655_360, 8_294_400
HEX = re.compile(r"#[0-9A-Fa-f]{6}")
ID_TELA = re.compile(r"[a-z0-9][a-z0-9-]*")
RESERVADOS_WINDOWS = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
EMAIL = re.compile(r"\b[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
DOMINIOS_FICTICIOS = {"contoso.com", "fabrikam.com", "example.com", "exemplo.com", "exemplo.com.br"}
CHAVE_VALIDA = re.compile(r"[\x21-\x7e]+")
SEGREDOS = re.compile(r"Bearer\s+\S+|sk-[\w-]+")
CONTROLES = re.compile(r"[\x00-\x1f\x7f]+")
HOSTS_LOCAIS = {"localhost", "127.0.0.1", "::1"}
CAMPOS_TEXTO_CONFIG = ("modelo", "tamanho", "qualidade", "pasta")
MOLDURA = (
    ("header", "Header"),
    ("navegacao", "Navigation"),
    ("notificacoes", "Notifications"),
    ("popups", "Pop-ups and modals"),
    ("carregando", "Loading"),
    ("estados", "Empty and no-access states"),
    ("rodape", "Footer"),
)
HTTP_QUE_REPETE = {429, 500, 502, 503, 504}
HTTP_QUE_ABORTA = {400, 401, 403, 404}
CODIGO_MODERACAO = "moderation_blocked"  # recusa de um prompt só: segue para a próxima tela
DICAS_HTTP = {
    400: "parâmetro recusado: confira --tamanho e --qualidade para este modelo",
    401: "confira OPENAI_API_KEY",
    403: "a organização pode precisar da Organization Verification para usar modelos GPT Image",
    404: "modelo inexistente para esta conta: confira OPENAI_IMAGE_MODEL ou --modelo",
    429: "limite de taxa ou de crédito: espere ou confira o faturamento da conta",
}


@dataclass(frozen=True)
class Achado:
    arquivo: str
    lugar: str
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        return f"{self.arquivo}:{self.lugar}: {self.nivel} {self.codigo} {self.mensagem}"


@dataclass(frozen=True)
class Parametros:
    modelo: str
    tamanho: str
    qualidade: str


class Interromper(Exception):
    """Erro que se repetiria em todas as telas: a execução para depois de registrá-lo."""

    def __init__(self, achado: Achado):
        super().__init__(achado.mensagem)
        self.achado = achado


# ---------- validação ----------

def _textos(valor: Any, caminho: str) -> Iterator[tuple[str, str]]:
    if isinstance(valor, str):
        yield caminho, valor
    elif isinstance(valor, dict):
        for chave, item in valor.items():
            yield from _textos(item, f"{caminho}.{chave}" if caminho else str(chave))
    elif isinstance(valor, list):
        for i, item in enumerate(valor):
            yield from _textos(item, f"{caminho}[{i}]")


def _preenchido(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def _validar_id(ident: Any, vistos: set[str]) -> str | None:
    if not isinstance(ident, str) or not ID_TELA.fullmatch(ident):
        return f"id `{ident!r}` fora do padrão (minúsculas, dígitos e hífen)"
    if ident in RESERVADOS_WINDOWS:
        return f"id `{ident}` é nome reservado do Windows"
    if ident in vistos:
        return f"id `{ident}` repetido"
    vistos.add(ident)
    return None


def validar_spec(spec: Any, rotulo: str) -> list[Achado]:
    def erro(lugar: str, codigo: str, msg: str) -> Achado:
        return Achado(rotulo, lugar, "ERRO", codigo, msg)

    if not isinstance(spec, dict):
        return [erro("raiz", "M001", "o spec precisa ser um objeto JSON")]
    achados: list[Achado] = []
    if not _preenchido(spec.get("app")):
        achados.append(erro("app", "M002", "falta `app` (nome do aplicativo)"))

    ds = spec.get("design_system")
    paleta = ds.get("paleta") if isinstance(ds, dict) else None
    if not isinstance(paleta, dict) or not paleta:
        achados.append(erro("design_system.paleta", "M002", "falta a paleta do design system (nome -> #RRGGBB)"))
    else:
        for nome, cor in paleta.items():
            if not isinstance(cor, str) or not HEX.fullmatch(cor):
                achados.append(erro(f"design_system.paleta.{nome}", "M003", f"`{cor!r}` não é #RRGGBB"))

    moldura = spec.get("moldura")
    if not isinstance(moldura, dict):
        achados.append(erro("moldura", "M002", "falta `moldura` (header, navegação, notificações, pop-ups)"))
    elif not _preenchido(moldura.get("header")):
        achados.append(erro("moldura.header", "M002", "falta `moldura.header`"))

    telas = spec.get("telas")
    if not isinstance(telas, list) or not telas:
        achados.append(erro("telas", "M002", "falta a lista `telas`"))
        telas = []
    vistos: set[str] = set()
    for i, tela in enumerate(telas):
        if not isinstance(tela, dict):
            achados.append(erro(f"telas[{i}]", "M002", "cada tela é um objeto"))
            continue
        ident = tela.get("id")
        lugar = ident.strip() if isinstance(ident, str) and ident.strip() else f"telas[{i}]"
        problema = _validar_id(ident, vistos)
        if problema:
            achados.append(erro(lugar, "M004", problema))
        for campo in ("nome", "descricao"):
            if not _preenchido(tela.get(campo)):
                achados.append(erro(lugar, "M002", f"falta `{campo}`"))

    for lugar, texto in _textos(spec, ""):
        for email in EMAIL.findall(texto):
            if email.split("@", 1)[1].lower() not in DOMINIOS_FICTICIOS:
                achados.append(erro(lugar, "M006", f"e-mail real `{email}` iria para a API externa (use @contoso.com)"))
    return achados


def validar_parametros(p: Parametros) -> list[Achado]:
    def achado(nivel: str, msg: str, codigo: str = "M005", lugar: str = "--tamanho") -> Achado:
        return Achado("parametros", lugar, nivel, codigo, msg)

    achados: list[Achado] = []
    if p.qualidade not in QUALIDADES:
        achados.append(achado("ERRO", f"qualidade `{p.qualidade}` fora de {sorted(QUALIDADES)}", "M007", "--qualidade"))
    if p.tamanho in TAMANHOS_SEGUROS:
        return achados
    m = re.fullmatch(r"(\d+)x(\d+)", p.tamanho)
    if not m:
        return achados + [achado("ERRO", f"tamanho `{p.tamanho}` fora do formato LARGURAxALTURA")]
    largura, altura = int(m.group(1)), int(m.group(2))
    if largura % 16 or altura % 16:
        achados.append(achado("ERRO", "largura e altura precisam ser múltiplos de 16"))
    elif max(largura, altura) > 3 * min(largura, altura):
        achados.append(achado("ERRO", "proporção acima de 3:1"))
    elif max(largura, altura) > ARESTA_MAX or not PIXELS_MIN <= largura * altura <= PIXELS_MAX:
        achados.append(achado("ERRO", f"fora dos limites (aresta até {ARESTA_MAX}, {PIXELS_MIN} a {PIXELS_MAX} pixels)"))
    else:
        achados.append(achado("AVISO", "tamanho personalizado: nem todo modelo aceita; os seguros são "
                                       "1024x1024, 1536x1024 e 1024x1536"))
    return achados


# ---------- prompt ----------

def montar_prompt(spec: dict, tela: dict) -> str:
    ds = spec.get("design_system") or {}
    moldura = spec.get("moldura") or {}
    linhas = [
        "High-fidelity UI mockup of one screen of a desktop business application built with Microsoft "
        "Power Apps (canvas app). Flat screenshot of the app canvas only: no device frame, no browser "
        f"window, no OS taskbar. Landscape layout designed for a {spec.get('canvas', '1920x1080')} canvas.",
        "",
        f"App: {spec['app']}",
        f"Screen: {tela['nome']}" + (f" - goal: {tela['objetivo']}" if _preenchido(tela.get("objetivo")) else ""),
    ]
    if _preenchido(tela.get("perfil")):
        linhas.append(f"Signed-in user role: {tela['perfil']}")
    linhas += ["", "Design system (use exactly these colors):"]
    linhas += [f"- {nome}: {cor}" for nome, cor in (ds.get("paleta") or {}).items()]
    detalhes = []
    if _preenchido(ds.get("fonte")):
        detalhes.append(f"Font: {ds['fonte']}.")
    if ds.get("raio") is not None:
        detalhes.append(f"Corner radius: {ds['raio']} px.")
    if _preenchido(ds.get("estilo")):
        detalhes.append(f"Style: {ds['estilo']}.")
    if detalhes:
        linhas.append("- " + " ".join(detalhes))
    linhas += ["", "App frame (identical on every screen):"]
    linhas += [f"- {rotulo}: {moldura[chave]}" for chave, rotulo in MOLDURA if _preenchido(moldura.get(chave))]
    linhas += ["", f"Screen content: {tela['descricao']}"]
    componentes = tela.get("componentes")
    if isinstance(componentes, list) and componentes:
        linhas.append("Components on this screen: " + ", ".join(map(str, componentes)))
    if _preenchido(tela.get("estado")):
        linhas.append(f"State shown: {tela['estado']}")
    linhas += [
        "",
        f"All visible UI text must be in {spec.get('idioma', 'pt-BR')}. Use realistic but fictitious sample "
        "data (unit codes like AAA, BBB). No real people, logos or brand names. Keep labels short and legible.",
    ]
    return "\n".join(linhas)


# ---------- API ----------

class _SemRedirecionar(urllib.request.HTTPRedirectHandler):
    """Redirecionamento levaria o cabeçalho Authorization para outro host: vira erro HTTP 3xx."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401 - assinatura do urllib
        return None


_ABRIDOR = urllib.request.build_opener(_SemRedirecionar)


def _urlopen(req: urllib.request.Request, timeout: float):  # trocado nos testes
    return _ABRIDOR.open(req, timeout=timeout)


def _dormir(segundos: float) -> None:  # trocado nos testes
    time.sleep(segundos)


def gerar_imagem(prompt: str, p: Parametros, chave: str, url: str, timeout: float) -> bytes:
    corpo = {"model": p.modelo, "prompt": prompt, "size": p.tamanho, "quality": p.qualidade, "n": 1}
    req = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        method="POST",
    )
    with _urlopen(req, timeout) as resp:
        bruto = resp.read(LIMITE_RESPOSTA + 1)
    if len(bruto) > LIMITE_RESPOSTA:
        raise LookupError("resposta acima de 50 MB")
    try:
        dados = json.loads(bruto.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as erro:
        raise LookupError("resposta não é JSON (proxy ou página de erro no caminho?)") from erro
    try:
        item = dados["data"][0]
    except (KeyError, IndexError, TypeError) as erro:
        raise LookupError("resposta sem `data[0]`") from erro
    b64 = item.get("b64_json") if isinstance(item, dict) else None
    if not b64:
        if isinstance(item, dict) and item.get("url"):
            raise LookupError("a API devolveu `url`, não `b64_json`: o modelo não é da família GPT Image")
        raise LookupError("resposta sem `data[0].b64_json`")
    try:
        imagem = base64.b64decode(b64, validate=True)
    except ValueError as erro:
        raise LookupError("`b64_json` não é base64 válido") from erro
    if not imagem.startswith(ASSINATURA_PNG):
        raise LookupError("o conteúdo devolvido não é PNG")
    return imagem


def _espera(erro: urllib.error.HTTPError, tentativa: int) -> float:
    pedido = erro.headers.get("Retry-After") if erro.headers is not None else None
    try:
        segundos = float(pedido) if pedido is not None else 2.0 ** (tentativa + 1)
    except ValueError:
        segundos = 2.0 ** (tentativa + 1)
    return max(0.0, min(segundos, ESPERA_MAX))


def gerar_com_tentativas(prompt: str, p: Parametros, chave: str, url: str, timeout: float) -> bytes:
    for tentativa in range(TENTATIVAS_EXTRAS + 1):
        try:
            return gerar_imagem(prompt, p, chave, url, timeout)
        except urllib.error.HTTPError as erro:
            if erro.code not in HTTP_QUE_REPETE or tentativa == TENTATIVAS_EXTRAS:
                raise
            _dormir(_espera(erro, tentativa))
    raise AssertionError("inalcançável")


def _limpar(texto: str, chave: str) -> str:
    if chave:
        texto = texto.replace(chave, "***")
    texto = SEGREDOS.sub("***", texto)
    return CONTROLES.sub(" ", texto).strip()[:300]


def _detalhe_http(erro: urllib.error.HTTPError, chave: str) -> tuple[str, str]:
    """Devolve (mensagem já limpa, código de erro da API)."""
    codigo_api = ""
    try:
        corpo = json.loads(erro.read().decode("utf-8"))
        erro_api = corpo.get("error") if isinstance(corpo, dict) else None
        if isinstance(erro_api, dict):
            msg = erro_api.get("message") or str(erro_api)
            codigo_api = str(erro_api.get("code") or "")
        else:
            msg = str(erro_api or corpo)
    except (ValueError, AttributeError, OSError):
        msg = str(erro.reason or "")
    if 300 <= erro.code < 400:
        dica = "redirecionamento recusado: confira OPENAI_BASE_URL"
    else:
        dica = DICAS_HTTP.get(erro.code)
    texto = f"HTTP {erro.code}: {_limpar(msg, chave)}" + (f" ({dica})" if dica else "")
    return texto, codigo_api


# ---------- arquivos ----------

def gravar_atomico(destino: Path, dados: bytes) -> None:
    """Grava num .tmp e troca: interrupção no meio nunca deixa PNG truncado com o nome final."""
    temporario = destino.with_name(destino.name + ".tmp")
    try:
        temporario.write_bytes(dados)
        os.replace(temporario, destino)
    finally:
        temporario.unlink(missing_ok=True)


def _cerca(texto: str) -> str:
    maior = max((len(m) for m in re.findall(r"`+", texto)), default=0)
    return "`" * max(3, maior + 1)


def escrever_galeria(spec: dict, saida: Path, p: Parametros) -> Path:
    linhas = [
        f"# Mockups — {spec['app']}",
        "",
        f"> gerado — não editar · `desenhar-mockups.py` · modelo `{p.modelo}` · tamanho `{p.tamanho}` · "
        f"qualidade `{p.qualidade}`",
        "> Referência visual para aprovar com o dono do processo. Não é fonte: a tela real sai do catálogo",
        "> de componentes e dos tokens `fx*` (skill `powerapps-canvas`).",
    ]
    for tela in spec["telas"]:
        imagem = saida / f"{tela['id']}.png"
        if not imagem.exists():
            continue
        estado = f" — {tela['estado']}" if _preenchido(tela.get("estado")) else ""
        prompt = montar_prompt(spec, tela)
        cerca = _cerca(prompt)
        linhas += [
            "", f"## {tela['nome']}{estado} (`{tela['id']}`)", "",
            f"![{tela['nome']}]({imagem.name})", "",
            "<details><summary>Prompt do spec atual (a imagem pode ser anterior)</summary>", "",
            f"{cerca}text", prompt, cerca, "", "</details>",
        ]
    galeria = saida / "mockups.md"
    gravar_atomico(galeria, ("\n".join(linhas) + "\n").encode("utf-8"))
    return galeria


# ---------- CLI ----------

def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_CONFIG
        if candidato.is_file():
            return candidato
    return None


def _rotulo(caminho: Path) -> str:
    try:
        return caminho.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return caminho.as_posix()


def _saida_utf8() -> None:
    """Saída redirecionada no Windows usa cp1252: o prompt conferido no --simular sairia diferente."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _uso(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 2


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Gera mockups das telas (/pp:mockups) com a API de imagens da OpenAI a partir do design system.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Variáveis de ambiente:\n"
            "  OPENAI_API_KEY      obrigatória para gerar (nunca em arquivo nem no chat)\n"
            f"  OPENAI_IMAGE_MODEL  modelo de imagem (default {MODELO_PADRAO})\n"
            f"  OPENAI_BASE_URL     endpoint compatível (default {URL_PADRAO}; https, salvo localhost)\n\n"
            "Códigos: M001 JSON, M002 campo obrigatório, M003 cor, M004 id de tela, M005 tamanho,\n"
            "M006 e-mail real, M007 qualidade, M101 erro HTTP ou de rede, M102 resposta sem PNG,\n"
            "M103 falha ao gravar.\n"
            "Rode primeiro com --simular: valida, mostra os prompts e conta as imagens, sem chave e sem rede."
        ),
    )
    ap.add_argument("spec", type=Path, help="mockups.json (molde em assets/mockups-molde.json)")
    ap.add_argument("--config", type=Path, help=f"caminho do {NOME_CONFIG} (default: procura para cima)")
    ap.add_argument("--modelo", help=f"modelo de imagem (sobrepõe OPENAI_IMAGE_MODEL e o config; default {MODELO_PADRAO})")
    ap.add_argument("--tamanho", help=f"LARGURAxALTURA ou auto (default {TAMANHO_PADRAO})")
    ap.add_argument("--qualidade", help=f"low, medium, high, auto... (default {QUALIDADE_PADRAO})")
    ap.add_argument("--saida", type=Path, help="pasta das imagens (default: mockups.pasta do config ou a pasta do spec)")
    ap.add_argument("--telas", help="ids separados por vírgula (default: todas)")
    ap.add_argument("--simular", action="store_true", help="valida e mostra os prompts, sem chamar a API")
    ap.add_argument("--sobrescrever", action="store_true", help="gera de novo imagens que já existem")
    ap.add_argument("--max-imagens", type=int, default=MAX_IMAGENS_PADRAO,
                    help=f"teto de imagens novas por execução (default {MAX_IMAGENS_PADRAO})")
    ap.add_argument("--timeout", type=float, default=TIMEOUT_PADRAO, help=f"segundos por imagem (default {TIMEOUT_PADRAO})")
    return ap.parse_args(argv)


def _carregar_config(caminho: Path | None) -> tuple[dict, Path] | str:
    """Devolve (bloco mockups, pasta base) ou a mensagem de erro de uso."""
    caminho = caminho or achar_config(Path.cwd())
    if caminho is None:
        print("# config: nenhuma encontrada -- defaults genéricos")
        return {}, Path.cwd()
    if not caminho.is_file():
        return f"config inexistente: {caminho}"
    try:
        config = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as erro:
        return f"config inválida ({caminho}): {erro}"
    if not isinstance(config, dict):
        return f"config inválida ({caminho}): a raiz precisa ser um objeto"
    cfg = config.get("mockups", {})
    if not isinstance(cfg, dict):
        return f"config inválida ({caminho}): `mockups` precisa ser um objeto"
    for chave in CAMPOS_TEXTO_CONFIG:
        if chave in cfg and not _preenchido(cfg[chave]):
            return f"config inválida ({caminho}): `mockups.{chave}` precisa ser texto"
    print(f"# config: {caminho.name}")
    return cfg, caminho.parent


def _url_da_api() -> str | None:
    base = os.environ.get("OPENAI_BASE_URL", URL_PADRAO).strip() or URL_PADRAO
    partes = urllib.parse.urlsplit(base)
    if partes.scheme == "https" or (partes.scheme == "http" and partes.hostname in HOSTS_LOCAIS):
        return base.rstrip("/") + "/images/generations"
    return None


def _fechar(achados: list[Achado]) -> int:
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(f"{erros} erro(s), {len(achados) - erros} aviso(s)")
    return 1 if erros else 0


def _gerar_uma(spec: dict, tela: dict, destino: Path, p: Parametros, chave: str, url: str,
               timeout: float, rotulo: str) -> Achado | None:
    """Gera e grava uma tela. Devolve o achado de erro que não interrompe; levanta Interromper."""
    def achado(codigo: str, msg: str) -> Achado:
        return Achado(rotulo, tela["id"], "ERRO", codigo, msg)

    try:
        imagem = gerar_com_tentativas(montar_prompt(spec, tela), p, chave, url, timeout)
    except urllib.error.HTTPError as erro:
        texto, codigo_api = _detalhe_http(erro, chave)
        if codigo_api == CODIGO_MODERACAO:
            return achado("M101", texto)
        raise Interromper(achado("M101", texto)) from erro
    except urllib.error.URLError as erro:
        raise Interromper(achado("M101", f"sem conexão com a API: {_limpar(str(erro.reason), chave)}")) from erro
    except (OSError, http.client.HTTPException) as erro:
        raise Interromper(achado("M101", f"falha de rede: {type(erro).__name__}: {_limpar(str(erro), chave)}")) from erro
    except LookupError as erro:
        return achado("M102", str(erro))
    try:
        gravar_atomico(destino, imagem)
    except OSError as erro:
        raise Interromper(achado("M103", f"não gravou {destino.name}: {erro}")) from erro
    print(f"# {tela['id']}: gerada -> {_rotulo(destino)}")
    return None


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    if args.max_imagens < 1 or args.timeout <= 0:
        return _uso("--max-imagens precisa ser 1 ou mais e --timeout maior que zero")
    if not args.spec.is_file():
        return _uso(f"spec inexistente: {args.spec}")
    carregado = _carregar_config(args.config)
    if isinstance(carregado, str):
        return _uso(carregado)
    cfg, base = carregado

    rotulo = _rotulo(args.spec)
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError:
        return _fechar([Achado(rotulo, "raiz", "ERRO", "M001", "o spec não está em UTF-8")])
    except json.JSONDecodeError as erro:
        return _fechar([Achado(rotulo, f"linha {erro.lineno}", "ERRO", "M001", f"JSON inválido: {erro.msg}")])

    p = Parametros(
        modelo=args.modelo or os.environ.get("OPENAI_IMAGE_MODEL") or cfg.get("modelo") or MODELO_PADRAO,
        tamanho=args.tamanho or cfg.get("tamanho") or TAMANHO_PADRAO,
        qualidade=args.qualidade or cfg.get("qualidade") or QUALIDADE_PADRAO,
    )
    achados = validar_spec(spec, rotulo) + validar_parametros(p)
    if any(a.nivel == "ERRO" for a in achados):
        return _fechar(achados)

    telas = spec["telas"]
    if args.telas is not None:
        pedidas = [t.strip() for t in args.telas.split(",") if t.strip()]
        if not pedidas:
            return _uso("--telas vazio: passe ids separados por vírgula")
        faltam = sorted(set(pedidas) - {t["id"] for t in telas})
        if faltam:
            return _uso(f"tela inexistente no spec: {', '.join(faltam)}")
        telas = [t for t in telas if t["id"] in pedidas]

    saida = args.saida or (base / cfg["pasta"] if cfg.get("pasta") else args.spec.parent)
    plano = [(t, saida / f"{t['id']}.png") for t in telas]
    novas = [(t, destino) for t, destino in plano if args.sobrescrever or not destino.exists()]
    print(f"# modelo: {p.modelo} · tamanho: {p.tamanho} · qualidade: {p.qualidade}")
    print(f"# saída: {_rotulo(saida)}")
    print(f"# {len(novas)} imagem(ns) nova(s), {len(plano) - len(novas)} existente(s) pulada(s)")

    if args.simular:
        for tela, destino in plano:
            situacao = "nova" if (tela, destino) in novas else "existe, pulada"
            print(f"\n## {tela['id']} -> {_rotulo(destino)} ({situacao})")
            print(montar_prompt(spec, tela))
        if len(novas) > args.max_imagens:
            print(f"# atenção: {len(novas)} imagens novas passam de --max-imagens {args.max_imagens}")
        print()
        return _fechar(achados)

    if len(novas) > args.max_imagens:
        return _uso(f"{len(novas)} imagens novas passam de --max-imagens {args.max_imagens}: "
                    "use --telas ou aumente o teto")
    url = _url_da_api()
    if url is None:
        return _uso("OPENAI_BASE_URL precisa ser https (http só para localhost)")
    chave = os.environ.get("OPENAI_API_KEY", "").strip()
    if not chave:
        return _uso("defina OPENAI_API_KEY no ambiente antes de gerar (não cole a chave no chat nem em arquivo); "
                    "para só conferir, use --simular")
    if not CHAVE_VALIDA.fullmatch(chave):
        return _uso("OPENAI_API_KEY tem espaço ou caractere de controle no meio: defina de novo")
    try:
        saida.mkdir(parents=True, exist_ok=True)
    except OSError as erro:
        return _uso(f"não criou a pasta de saída {_rotulo(saida)}: {erro}")

    for tela, destino in novas:
        try:
            achado = _gerar_uma(spec, tela, destino, p, chave, url, args.timeout, rotulo)
        except Interromper as parada:
            achados.append(parada.achado)
            print("# execução interrompida: o mesmo erro se repetiria nas próximas telas")
            break
        if achado:
            achados.append(achado)
    try:
        print(f"# galeria: {_rotulo(escrever_galeria(spec, saida, p))}")
    except OSError as erro:
        achados.append(Achado(rotulo, "mockups.md", "ERRO", "M103", f"não gravou a galeria: {erro}"))
    return _fechar(achados)


if __name__ == "__main__":
    sys.exit(main())
