#!/usr/bin/env python3
"""Verificador do protótipo HTML da etapa /pp:prototipo (somente leitura).

O protótipo é construído em cima dos mockups aprovados (`desenhar-mockups.py`): cada tela
reproduz os PNGs de origem com os componentes do catálogo Canvas e os tokens `fx*`. Este
script confere o contrato do molde `assets/prototipo-molde.html`:

  - marca de protótipo fora do canvas e `<main data-canvas="LxA">`;
  - cada `<section data-tela>` com id, título, perfis e `data-mockups` (a origem nas imagens);
  - cada `data-componente` no catálogo Canvas (`novo:` vira aviso);
  - nenhum recurso externo (abre por `file://`, offline);
  - cor literal só em `:root` (fora dele, `var(--fx...)`).

Com `--mockups <spec>`, confere também a ida e a volta com o spec dos mockups: id que não
existe no spec, mockup do spec sem tela e PNG que ainda não foi gerado.

Saída: `caminho:linha: ERRO|AVISO Vnnn mensagem`. Última linha: `N erro(s), M aviso(s)`.
Exit: 0 sem erro, 1 com erro, 2 uso incorreto.

Configuração: `power-platform.config.json` (procurado do diretório atual para cima, ou
`--config`): `pastas.prototipo` (onde procurar quando nenhum caminho é dado), `mockups.pasta`
(onde estão os PNGs) e `ignorar` (globs).
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Iterator

NOME_CONFIG = "power-platform.config.json"
PASTA_PADRAO = "docs/planejamento/prototipo"

CATALOGO_CANVAS = (
    "abas", "badge-status", "barra-filtros", "botoes", "cabecalho-tela", "card-kpi", "estado-vazio",
    "exportar", "galeria-tabela", "linha-expansivel", "menu-lateral", "modal-confirmacao",
    "modal-destrutivo-motivo", "modal-formulario", "modal-informativo", "ordenacao-coluna",
    "overlay-loading", "paginacao-cursor", "painel-sem-acesso", "rodape-contagem", "selecao-em-lote",
    "seletor-unidade", "toast",
)

CODIGOS = {
    "V001": ("ERRO", "data-componente vazio ou fora do catálogo Canvas"),
    "V002": ("AVISO", "componente novo (novo:x): crie a entrada no catálogo antes de construir a tela"),
    "V003": ("ERRO", "recurso externo (http, https ou //) ou @import: o protótipo tem de abrir offline"),
    "V004": ("ERRO", "nenhuma tela (<section data-tela>)"),
    "V005": ("ERRO", "id de tela inválido (tela-xxx), repetido ou fora de <section>"),
    "V006": ("AVISO", "tela sem data-titulo ou data-perfis"),
    "V007": ("AVISO", "cor literal fora do :root (CSS, style, SVG ou script): use var(--fx...)"),
    "V008": ("ERRO", "marca de protótipo ausente ou dentro do canvas (data-prototipo, -controles, -aviso)"),
    "V009": ("ERRO", "canvas ausente ou inválido (<main data-canvas=\"1920x1080\">)"),
    "V010": ("ERRO", "tela sem mockup de origem (data-mockups) ou id de mockup inválido"),
    "V011": ("ERRO", "data-mockups cita id que não existe no spec (--mockups)"),
    "V012": ("ERRO", "mockup do spec sem tela no protótipo (--mockups)"),
    "V013": ("AVISO", "PNG do mockup não encontrado: o protótipo não foi feito em cima da imagem (--mockups)"),
}

RE_TELA = re.compile(r"tela-[a-z0-9]+(?:-[a-z0-9]+)*")
RE_MOCKUP = re.compile(r"[a-z0-9][a-z0-9-]*")
RE_CANVAS = re.compile(r"[1-9]\d{2,4}x[1-9]\d{2,4}")
RE_EXTERNO = re.compile(r"\s*(?:[a-z][a-z0-9+.-]*:)?//", re.IGNORECASE)
RE_URL_EXTERNA = re.compile(r"\burl\(\s*['\"]?\s*(?:[a-z][a-z0-9+.-]*:)?//", re.IGNORECASE)
RE_IMPORT = re.compile(r"@import\b", re.IGNORECASE)
RE_COMENTARIO_CSS = re.compile(r"/\*.*?\*/", re.DOTALL)
RE_STRING_CSS = re.compile(r"\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'")
RE_VAR = re.compile(r"\bvar\([^()]*\)", re.IGNORECASE)
RE_URL = re.compile(r"\burl\([^)]*\)", re.IGNORECASE)
RE_HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
RE_FUNCAO_COR = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(", re.IGNORECASE)
RE_PALAVRA = re.compile(r"[A-Za-z]+")
RE_COR_JS = re.compile(
    r"""(['"`])\s*(#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})|(?:rgba?|hsla?)\([^'"`]*\))\s*\1""")

CORES_NOMEADAS = frozenset("""
aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet brown
burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid
darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet
deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro
ghostwhite gold goldenrod gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan lightgoldenrodyellow
lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen lightskyblue lightslategray
lightslategrey lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine
mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen mediumturquoise
mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite navy oldlace olive olivedrab
orange orangered orchid palegoldenrod palegreen paleturquoise palevioletred papayawhip peachpuff peru
pink plum powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown
seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
teal thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen
""".split())

# atributos que carregam recurso: um valor externo quebra o `file://` offline
ATRIBUTOS_RECURSO = {
    "script": ("src",), "link": ("href",), "img": ("src", "srcset"), "iframe": ("src",),
    "source": ("src", "srcset"), "video": ("src", "poster"), "audio": ("src",), "embed": ("src",),
    "object": ("data",), "track": ("src",), "input": ("src",), "image": ("href", "xlink:href"),
}
ATRIBUTOS_COR = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color", "bgcolor")


@dataclass(frozen=True)
class Achado:
    caminho: str
    linha: int
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        return f"{self.caminho}:{self.linha}: {self.nivel} {self.codigo} {self.mensagem}"


@dataclass(frozen=True)
class Tela:
    id: str
    titulo: str
    perfis: tuple[str, ...]
    mockups: tuple[str, ...]
    linha: int
    componentes: tuple[str, ...]


@dataclass(frozen=True)
class Resultado:
    rotulo: str
    telas: tuple[Tela, ...]
    globais: tuple[str, ...]
    achados: tuple[Achado, ...]

    def componentes(self) -> list[str]:
        return [c for t in self.telas for c in t.componentes] + list(self.globais)


# ------------------------------------------------------------------ cor e CSS

def _apagar(m: re.Match) -> str:
    """Troca o trecho por espaços, mantendo as quebras de linha (a linha do achado não muda)."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _apagar_miolo(m: re.Match) -> str:
    texto = m.group(0)
    return texto[0] + re.sub(r"[^\n]", " ", texto[1:-1]) + texto[-1]


def cor_literal(valor: str) -> str | None:
    """Primeira cor literal do valor, ignorando o que está em var(...) e url(...)."""
    v = RE_URL.sub(" ", valor)
    anterior = None
    while anterior != v:
        anterior, v = v, RE_VAR.sub(" ", v)
    m = RE_HEX.search(v) or RE_FUNCAO_COR.search(v)
    if m:
        return m.group(0)
    return next((p for p in RE_PALAVRA.findall(v) if p.lower() in CORES_NOMEADAS), None)


def _blocos_css(css: str) -> Iterator[tuple[str, str, int]]:
    """(seletor, corpo, posição do corpo) de cada bloco sem bloco dentro."""
    pilha: list[tuple[str, int]] = []
    inicio = 0
    for i, ch in enumerate(css):
        if ch == "{":
            pilha.append((css[inicio:i].strip(), i + 1))
            inicio = i + 1
        elif ch == "}":
            if pilha:
                seletor, ini = pilha.pop()
                corpo = css[ini:i]
                if "{" not in corpo:
                    yield seletor, corpo, ini
            inicio = i + 1
        elif ch == ";":
            inicio = i + 1


def _declaracoes(corpo: str) -> Iterator[tuple[int, str, str]]:
    for m in re.finditer(r"[^;]+", corpo):
        texto = m.group(0)
        if ":" not in texto:
            continue
        prop, valor = texto.split(":", 1)
        yield m.start() + len(texto) - len(texto.lstrip()), prop.strip(), valor


def _e_raiz(seletor: str) -> bool:
    partes = [p.strip() for p in seletor.split(",")]
    return bool(partes) and all(p.startswith(":root") for p in partes)


Anotar = Callable[[int, str, str], None]


def analisar_css(css: str, linha0: int, anotar: Anotar) -> None:
    css = RE_COMENTARIO_CSS.sub(_apagar, css)

    def linha(pos: int) -> int:
        return linha0 + css.count("\n", 0, pos)

    for m in RE_URL_EXTERNA.finditer(css):
        anotar(linha(m.start()), "V003", "url() externa no CSS: embuta o recurso ou use SVG inline")
    for m in RE_IMPORT.finditer(css):
        anotar(linha(m.start()), "V003", "@import no CSS: o protótipo é um arquivo só")
    css = RE_STRING_CSS.sub(_apagar_miolo, css)
    for seletor, corpo, ini in _blocos_css(css):
        if _e_raiz(seletor):
            continue
        for pos, prop, valor in _declaracoes(corpo):
            literal = cor_literal(valor)
            if literal:
                anotar(linha(ini + pos), "V007", f"cor literal `{literal}` em `{prop}` fora do :root: "
                                                 "use var(--fx...)")


def analisar_style(valor: str, linha: int, anotar: Anotar) -> None:
    if RE_URL_EXTERNA.search(valor):
        anotar(linha, "V003", "url() externa no atributo style")
    for _, prop, v in _declaracoes(RE_STRING_CSS.sub(_apagar_miolo, valor)):
        literal = cor_literal(v)
        if literal:
            anotar(linha, "V007", f"cor literal `{literal}` em style=\"{prop}: ...\": use var(--fx...)")


def analisar_script(js: str, linha0: int, anotar: Anotar) -> None:
    for m in RE_COR_JS.finditer(js):
        anotar(linha0 + js.count("\n", 0, m.start()), "V007",
               f"cor montada no script (`{m.group(2)}`): troque classes, não cor")


# ------------------------------------------------------------------ HTML

class _Leitor(HTMLParser):
    def __init__(self, rotulo: str, catalogo: frozenset[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.rotulo = rotulo
        self.catalogo = catalogo
        self.achados: list[Achado] = []
        self.telas: dict[str, dict] = {}
        self.globais: list[str] = []
        self.secoes: list[str | None] = []
        self.dentro_main = 0
        self.marcas = {"html": False, "controles": False, "aviso": False}
        self.marca_no_canvas: dict[str, int] = {}
        self.canvas_ok = False
        self.canvas_linha: int | None = None
        self.bloco: tuple[str, list[int], list[str]] | None = None

    def anotar(self, linha: int, codigo: str, mensagem: str) -> None:
        self.achados.append(Achado(self.rotulo, linha, CODIGOS[codigo][0], codigo, mensagem))

    # -- elementos

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        linha = self.getpos()[0]
        if tag in ("style", "script"):
            self.bloco = (tag, [], [])
        if tag == "html" and "data-prototipo" in a:
            self.marcas["html"] = True
        if tag == "main":
            self.dentro_main += 1
            self._canvas(a, linha)
        for marca, attr in (("controles", "data-prototipo-controles"), ("aviso", "data-prototipo-aviso")):
            if attr in a:
                if self.dentro_main:
                    self.marca_no_canvas.setdefault(marca, linha)
                else:
                    self.marcas[marca] = True
        self._recursos(tag, a, linha)
        self._cores(a, linha)
        if tag == "section" or "data-tela" in a:
            self._tela(tag, a, linha)
        if "data-componente" in a:
            self._componente(a["data-componente"].strip(), linha)

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.secoes:
            self.secoes.pop()
        elif tag == "main" and self.dentro_main:
            self.dentro_main -= 1
        elif self.bloco and tag == self.bloco[0]:
            tipo, inicio, partes = self.bloco
            self.bloco = None
            texto = "".join(partes)
            if texto.strip():
                (analisar_css if tipo == "style" else analisar_script)(texto, inicio[0], self.anotar)

    def handle_data(self, data: str) -> None:
        if self.bloco:
            if not self.bloco[1]:
                self.bloco[1].append(self.getpos()[0])
            self.bloco[2].append(data)

    # -- regras por elemento

    def _canvas(self, a: dict[str, str], linha: int) -> None:
        if RE_CANVAS.fullmatch(a.get("data-canvas", "").strip()):
            self.canvas_ok = True
        elif self.canvas_linha is None:
            self.canvas_linha = linha

    def _recursos(self, tag: str, a: dict[str, str], linha: int) -> None:
        for attr in ATRIBUTOS_RECURSO.get(tag, ()):
            valor = a.get(attr, "")
            partes = valor.split(",") if attr == "srcset" else [valor]
            if valor and any(RE_EXTERNO.match(p) for p in partes):
                self.anotar(linha, "V003", f"<{tag} {attr}> externo (`{valor.strip()[:80]}`): "
                                           "embuta o recurso ou use SVG inline")

    def _cores(self, a: dict[str, str], linha: int) -> None:
        if a.get("style"):
            analisar_style(a["style"], linha, self.anotar)
        for attr in ATRIBUTOS_COR:
            literal = cor_literal(a.get(attr, ""))
            if literal:
                self.anotar(linha, "V007", f"cor literal `{literal}` em {attr}=: use currentColor ou var(--fx...)")

    def _tela(self, tag: str, a: dict[str, str], linha: int) -> None:
        if "data-tela" not in a:
            self.secoes.append(None)
            return
        ident = a["data-tela"].strip()
        valido = bool(RE_TELA.fullmatch(ident))
        if tag != "section":
            self.anotar(linha, "V005", f"data-tela=\"{ident}\" em <{tag}>: use <section data-tela>")
        elif not valido:
            self.anotar(linha, "V005", f"id de tela inválido `{ident}`: use tela-xxx (minúsculas, dígitos, hífen)")
        elif ident in self.telas:
            self.anotar(linha, "V005", f"tela `{ident}` repetida (a primeira está na linha "
                                       f"{self.telas[ident]['linha']})")
        else:
            self._registrar_tela(ident, a, linha)
        if tag == "section":
            self.secoes.append(ident if valido else None)

    def _registrar_tela(self, ident: str, a: dict[str, str], linha: int) -> None:
        perfis = tuple(p.strip() for p in a.get("data-perfis", "").split(",") if p.strip())
        mockups = tuple(m.strip() for m in a.get("data-mockups", "").split(",") if m.strip())
        faltam = [attr for attr, valor in (("data-titulo", a.get("data-titulo", "").strip()),
                                          ("data-perfis", perfis)) if not valor]
        if faltam:
            self.anotar(linha, "V006", f"tela `{ident}` sem {' e '.join(faltam)}")
        if not mockups:
            self.anotar(linha, "V010", f"tela `{ident}` sem mockup de origem: o protótipo é feito em cima "
                                       "das imagens aprovadas (data-mockups=\"tl-...\")")
        for m in mockups:
            if not RE_MOCKUP.fullmatch(m):
                self.anotar(linha, "V010", f"id de mockup inválido `{m}` em `{ident}`: use o id do spec "
                                           "(minúsculas, dígitos, hífen)")
        self.telas[ident] = {"titulo": a.get("data-titulo", "").strip(), "perfis": perfis,
                             "mockups": mockups, "linha": linha, "componentes": []}

    def _componente(self, nome: str, linha: int) -> None:
        if not nome:
            self.anotar(linha, "V001", "data-componente vazio: use um nome do catálogo Canvas")
            return
        if nome.startswith("novo:"):
            self.anotar(linha, "V002", f"componente novo `{nome[5:]}`: crie a entrada no catálogo antes "
                                       "de construir a tela")
        elif nome not in self.catalogo:
            self.anotar(linha, "V001", f"`{nome}` não está no catálogo Canvas "
                                       "(powerapps-canvas/assets/componentes/)")
            return
        tela = next((s for s in reversed(self.secoes) if s), None)
        destino = self.telas[tela]["componentes"] if tela in self.telas else self.globais
        destino.append(nome)

    # -- fechamento

    def fechar(self) -> Resultado:
        self.close()
        textos = {"html": "<html data-prototipo=\"v1\">", "controles": "barra data-prototipo-controles",
                  "aviso": "aviso data-prototipo-aviso (\"Protótipo para validação — não é o app\")"}
        for marca, presente in self.marcas.items():
            if not presente:
                no_canvas = self.marca_no_canvas.get(marca)
                onde = "está dentro do canvas: mova para fora do <main>" if no_canvas else "ausente"
                self.anotar(no_canvas or 1, "V008", f"{textos[marca]} {onde}")
        if not self.canvas_ok:
            self.anotar(self.canvas_linha or 1, "V009",
                        "canvas ausente ou inválido: use <main data-canvas=\"1920x1080\">")
        if not self.telas:
            self.anotar(1, "V004", "nenhuma tela: cada tela é uma <section data-tela=\"tela-xxx\">")
        telas = tuple(Tela(i, d["titulo"], d["perfis"], d["mockups"], d["linha"], tuple(d["componentes"]))
                      for i, d in self.telas.items())
        return Resultado(self.rotulo, telas, tuple(self.globais),
                         tuple(sorted(self.achados, key=lambda x: (x.linha, x.codigo))))


def analisar(texto: str, rotulo: str, catalogo: frozenset[str] = frozenset(CATALOGO_CANVAS)) -> Resultado:
    leitor = _Leitor(rotulo, catalogo)
    leitor.feed(texto)
    return leitor.fechar()


def conferir_mockups(r: Resultado, ids_spec: tuple[str, ...], pasta_imagens: Path) -> list[Achado]:
    """Ida e volta com o spec: id inexistente, mockup sem tela e PNG ausente."""
    achados: list[Achado] = []
    citados: set[str] = set()
    for tela in r.telas:
        for m in tela.mockups:
            citados.add(m)
            if m not in ids_spec:
                achados.append(Achado(r.rotulo, tela.linha, "ERRO", "V011",
                                      f"`{tela.id}` cita o mockup `{m}`, que não existe no spec"))
            elif not (pasta_imagens / f"{m}.png").is_file():
                achados.append(Achado(r.rotulo, tela.linha, "AVISO", "V013",
                                      f"mockup `{m}` sem PNG em `{(pasta_imagens / (m + '.png')).as_posix()}`: "
                                      "gere e aprove a imagem antes de construir a tela"))
    for m in ids_spec:
        if m not in citados:
            achados.append(Achado(r.rotulo, 1, "ERRO", "V012",
                                  f"mockup `{m}` do spec sem tela no protótipo: cite-o em data-mockups"))
    return achados


def inventario(r: Resultado) -> list[str]:
    def lista(itens) -> str:
        unicos = sorted(set(itens))
        return ", ".join(f"`{i}`" for i in unicos) if unicos else "—"

    linhas = [f"## {r.rotulo}", "", "| Tela | Título | Perfis | Componentes | Mockups |", "|---|---|---|---|---|"]
    linhas += [f"| `{t.id}` | {t.titulo or '—'} | {', '.join(t.perfis) or '—'} | {lista(t.componentes)} | "
               f"{', '.join(f'`{m}`' for m in t.mockups) or '—'} |" for t in r.telas]
    if r.globais:
        linhas.append(f"| (global) | — | — | {lista(r.globais)} | — |")
    return linhas + [""]


# ------------------------------------------------------------------ config e arquivos

def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_CONFIG
        if candidato.is_file():
            return candidato
    return None


def glob_para_regex(padrao: str) -> re.Pattern:
    saida, i = [], 0
    while i < len(padrao):
        if padrao.startswith("**/", i):
            saida.append("(?:.*/)?")
            i += 3
        elif padrao.startswith("**", i):
            saida.append(".*")
            i += 2
        elif padrao[i] == "*":
            saida.append("[^/]*")
            i += 1
        elif padrao[i] == "?":
            saida.append("[^/]")
            i += 1
        else:
            saida.append(re.escape(padrao[i]))
            i += 1
    return re.compile("^" + "".join(saida) + "$")


def descobrir(alvos: list[Path], base: Path, ignorar: list[re.Pattern]) -> list[Path]:
    saida: list[Path] = []
    for alvo in alvos:
        if alvo.is_file():
            saida.append(alvo)
            continue
        for p in sorted(alvo.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in (".html", ".htm"):
                continue
            if any(parte in ("__pycache__", ".git", "node_modules") for parte in p.parts):
                continue
            try:
                rel = p.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                rel = p.as_posix()
            if not any(r.match(rel) for r in ignorar):
                saida.append(p)
    return saida


def _rotulo(caminho: Path) -> str:
    try:
        return caminho.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return caminho.as_posix()


def _carregar_config(caminho: Path | None) -> tuple[dict, Path] | str:
    if caminho is None:
        return {}, Path.cwd()
    try:
        config = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erro:
        return f"config inválida ({caminho}): {erro}"
    if not isinstance(config, dict):
        return f"config inválida ({caminho}): a raiz tem de ser um objeto"
    for chave in ("pastas", "mockups"):
        if not isinstance(config.get(chave, {}), dict):
            return f"config inválida ({caminho}): `{chave}` tem de ser um objeto"
    return config, caminho.parent


def _ids_do_spec(caminho: Path) -> tuple[str, ...] | str:
    if not caminho.is_file():
        return f"spec de mockups inexistente: {caminho}"
    try:
        spec = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erro:
        return f"spec de mockups inválido ({caminho}): {erro}"
    telas = spec.get("telas") if isinstance(spec, dict) else None
    if not isinstance(telas, list) or not telas:
        return f"spec de mockups inválido ({caminho}): `telas` tem de ser uma lista não vazia"
    if not all(isinstance(t, dict) and isinstance(t.get("id"), str) and t["id"] for t in telas):
        return f"spec de mockups inválido ({caminho}): toda tela precisa de `id` texto"
    return tuple(t["id"] for t in telas)


def _catalogo(pasta: Path | None) -> frozenset[str] | str:
    if pasta is None:
        return frozenset(CATALOGO_CANVAS)
    nomes = frozenset(p.stem for p in pasta.glob("*.md") if p.name != "INDICE.md") if pasta.is_dir() else frozenset()
    return nomes or f"catálogo vazio ou inexistente: {pasta}"


def _saida_utf8() -> None:
    """Saída redirecionada no Windows usa cp1252: acento e travessão sairiam trocados."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _uso(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    ap = argparse.ArgumentParser(
        description="Verifica o protótipo HTML da etapa /pp:prototipo, feito em cima dos mockups aprovados. Só lê.",
        epilog="Códigos: " + ", ".join(f"{c} {d.split(':')[0].split(' (')[0]}" for c, (_, d) in CODIGOS.items())
               + ". Detalhe: --codigos.")
    ap.add_argument("caminhos", nargs="*", type=Path,
                    help=f"arquivos .html ou pastas (default: pastas.prototipo da config ou {PASTA_PADRAO})")
    ap.add_argument("--mockups", type=Path, help="spec dos mockups (mockups.json): confere a origem nas imagens")
    ap.add_argument("--catalogo", type=Path, help="pasta do catálogo Canvas (default: o catálogo do kit)")
    ap.add_argument("--inventario", action="store_true", help="imprime a tabela tela × componentes × mockups")
    ap.add_argument("--codigos", action="store_true", help="lista os códigos e sai")
    ap.add_argument("--config", type=Path, help=f"caminho do {NOME_CONFIG}")
    args = ap.parse_args(argv)

    if args.codigos:
        for codigo, (nivel, descricao) in CODIGOS.items():
            print(f"{codigo} {nivel:5} {descricao}")
        return 0
    if args.config and not args.config.is_file():
        return _uso(f"config inexistente: {args.config}")
    config_path = args.config or achar_config(Path.cwd())
    carregado = _carregar_config(config_path)
    if isinstance(carregado, str):
        return _uso(carregado)
    config, base = carregado
    catalogo = _catalogo(args.catalogo)
    if isinstance(catalogo, str):
        return _uso(catalogo)
    ids_spec: tuple[str, ...] = ()
    pasta_imagens = Path()
    if args.mockups:
        lido = _ids_do_spec(args.mockups)
        if isinstance(lido, str):
            return _uso(lido)
        ids_spec = lido
        pasta_cfg = config.get("mockups", {}).get("pasta")
        pasta_imagens = base / pasta_cfg if isinstance(pasta_cfg, str) and pasta_cfg else args.mockups.parent

    pastas = config.get("pastas", {}).get("prototipo", [PASTA_PADRAO])
    alvos = args.caminhos or [base / p for p in ([pastas] if isinstance(pastas, str) else pastas)]
    inexistentes = [a for a in alvos if not a.exists()]
    if inexistentes:
        return _uso(f"caminho inexistente: {inexistentes[0]}")
    ignorar = [glob_para_regex(g) for g in config.get("ignorar", []) if isinstance(g, str)]
    arquivos = descobrir(alvos, base, ignorar)

    print(f"# config: {config_path.name if config_path else 'nenhuma encontrada -- defaults genéricos'}")
    achados: list[Achado] = []
    for caminho in arquivos:
        try:
            texto = caminho.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as erro:
            return _uso(f"não li {caminho}: {erro}")
        r = analisar(texto, _rotulo(caminho), catalogo)
        if args.inventario:
            print("\n".join(inventario(r)))
        extras = conferir_mockups(r, ids_spec, pasta_imagens) if args.mockups else []
        achados += sorted(r.achados + tuple(extras), key=lambda x: (x.linha, x.codigo))
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(f"# {len(arquivos)} arquivo(s) analisado(s)")
    print(f"{erros} erro(s), {len(achados) - erros} aviso(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
