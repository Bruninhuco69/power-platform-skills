#!/usr/bin/env python3
"""Estado do pipeline do projeto: o que já foi feito e qual é o próximo comando.

Cada etapa do kit (`/pp:novo` → `/pp:brainstorm` → ... → `/pp:publicar`) chama este script no
começo (`comecar`) e no fim (`concluir`). O estado fica num bloco JSON no fim do `ESTADO.md` da
raiz do projeto; a parte legível (progresso, tabela, próximo passo, histórico) é reescrita a cada
mudança. O próximo passo sai sempre daqui, igual para todas as etapas.

Comandos:
  iniciar   --projeto NOME --ideia "..."   cria o ESTADO.md na pasta atual (recusa se já existe)
  mostrar                                  painel: progresso, tabela das etapas e próximo passo
  checar    ETAPA                          exit 0 se as etapas anteriores estão feitas; senão diz o caminho
  comecar   ETAPA                          checar + marca a etapa "em andamento"
  concluir  ETAPA [--nota "..."]           marca concluída e mostra o próximo passo
  dispensar ETAPA --motivo "..."           conta como feita, com o motivo (ex.: mockups sem chave)
  reabrir   ETAPA --motivo "..." [--argumento X]
                                           reabre a etapa e as seguintes (ajuste do protótipo,
                                           falha de teste); --argumento entra no comando sugerido
  proximo                                  só o bloco "Próximo passo"
  veredito  ETAPA --agente NOME --resultado aceito|revisao|escalado [--motivo "..."]
                                           julgamento da entrega de um agente (conta na tabela)

Exit: 0 ok · 1 etapa anterior não concluída (checar, comecar, concluir) · 2 uso incorreto,
ESTADO.md ausente ou corrompido.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

NOME_ARQUIVO = "ESTADO.md"
PREFIXO_COMANDO = "/pp:"
MARCA_INICIO = "<!-- pp:estado"
MARCA_FIM = "-->"
VERSAO_ESTADO = 1
LARGURA_BARRA = 10
HISTORICO_VISIVEL = 20
LINHA = "─" * 63
BANNER = "━" * 55


@dataclass(frozen=True)
class Etapa:
    id: str
    bloco: str
    titulo: str
    agente: str
    entrega: str


ETAPAS: tuple[Etapa, ...] = (
    Etapa("novo", "Início", "Início do projeto", "Orquestrador",
          "pasta, git, config e ESTADO.md"),
    Etapa("brainstorm", "1. Definição do produto", "Brainstorm e requisitos", "Agente Brainstorm",
          "requisitos, funcionalidades e escopo do MVP"),
    Etapa("design", "2. Identidade e experiência", "Identidade visual", "Agente Designer Branding",
          "cores, fontes, componentes e identidade visual"),
    Etapa("mockups", "2. Identidade e experiência", "Mockups em imagem", "Agente de Mockups em Imagem",
          "telas, navegação, loading, erros e estados vazios"),
    Etapa("prototipo", "2. Identidade e experiência", "Protótipo navegável", "Agente Gerador de Mockup HTML",
          "protótipo navegável aprovado pelo usuário"),
    Etapa("arquitetura", "3. Construção na Power Platform", "Arquitetura", "Agente de Arquitetura",
          "modelo de dados, permissões, integrações e fila de construção"),
    Etapa("construir", "3. Construção na Power Platform", "Construção",
          "Agentes Power Apps Canvas e Power Automate",
          "telas, fórmulas Power Fx, fluxos e app integrado às automações"),
    Etapa("testar", "4. Validação e entrega", "Testes e qualidade", "Agente de Testes e Qualidade",
          "validadores, testes de negação e ciclo completo no dado"),
    Etapa("homologar", "4. Validação e entrega", "Homologação", "Orquestrador, com o usuário",
          "aceite dos usuários reais no ambiente de homologação"),
    Etapa("publicar", "4. Validação e entrega", "Publicação e documentação", "Orquestrador",
          "app em produção, manual do usuário e guia técnico"),
)
IDS = tuple(e.id for e in ETAPAS)
POR_ID = {e.id: e for e in ETAPAS}

FEITAS = {"concluida", "dispensada"}
SITUACOES = {"pendente", "andamento", "concluida", "dispensada", "reaberta"}
SIMBOLO = {"concluida": "✓ concluída", "dispensada": "⊘ dispensada", "andamento": "◆ em andamento",
           "reaberta": "↺ reaberta", "pendente": "○ pendente"}
VEREDITOS = {"aceito": ("✓", "aceito"), "revisao": ("↻", "revisão"), "escalado": ("⚠", "escalado")}

ALTERNATIVAS = {
    "construir": [("/pp:construir app", "só as telas (Agente Power Apps Canvas)"),
                  ("/pp:construir flows", "só os fluxos (Agente Power Automate)")],
    "prototipo": [("/pp:design", "voltar para a identidade visual")],
}


class ErroEstado(Exception):
    """ESTADO.md ausente, corrompido ou uso incorreto (exit 2)."""


# ---------------------------------------------------------------- utilidades

def _hoje() -> str:
    return os.environ.get("PP_DATA_HOJE") or date.today().isoformat()


def _saida_utf8() -> None:
    """Console do Windows usa cp1252; os símbolos do painel sairiam quebrados."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _texto_limpo(valor: str) -> str:
    """Uma linha, sem `|` (quebraria a tabela) e sem a marca de fim do bloco de dados."""
    return " ".join(str(valor).replace("|", "/").replace(MARCA_FIM, "->").split())


def _comando(etapa_id: str, argumento: str = "") -> str:
    return f"{PREFIXO_COMANDO}{etapa_id}" + (f" {argumento}" if argumento else "")


def achar_estado(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_ARQUIVO
        if candidato.is_file():
            return candidato
    return None


# ---------------------------------------------------------------- modelo

def estado_novo(projeto: str, ideia: str) -> dict:
    etapas = {e: {"situacao": "pendente", "data": "", "nota": "", "argumento": ""} for e in IDS}
    return {"versao": VERSAO_ESTADO, "projeto": _texto_limpo(projeto), "ideia": _texto_limpo(ideia),
            "criado": _hoje(), "etapas": etapas, "historico": []}


def validar_estado(dados: object) -> dict:
    if not isinstance(dados, dict) or not isinstance(dados.get("etapas"), dict):
        raise ErroEstado("bloco de dados sem `etapas`")
    for etapa_id in IDS:
        registro = dados["etapas"].get(etapa_id)
        if not isinstance(registro, dict) or registro.get("situacao") not in SITUACOES:
            raise ErroEstado(f"etapa `{etapa_id}` ausente ou com situação inválida no bloco de dados")
        for campo in ("data", "nota", "argumento"):
            registro.setdefault(campo, "")
        if not _vereditos_validos(registro.get("vereditos", {})):
            raise ErroEstado(f"etapa `{etapa_id}`: `vereditos` inválido no bloco de dados")
    dados.setdefault("historico", [])
    dados.setdefault("projeto", "projeto")
    dados.setdefault("ideia", "")
    return dados


def _vereditos_validos(vereditos: object) -> bool:
    """`{agente: {aceito|revisao|escalado: n}}`; ausente em projeto antigo."""
    return isinstance(vereditos, dict) and all(
        isinstance(contagem, dict) and all(r in VEREDITOS and isinstance(n, int) and n >= 0
                                           for r, n in contagem.items())
        for contagem in vereditos.values())


def ler_estado(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    inicio = texto.rfind(MARCA_INICIO)
    if inicio < 0:
        raise ErroEstado(f"{caminho.name} sem o bloco `{MARCA_INICIO}` (foi editado à mão?)")
    fim = texto.find(MARCA_FIM, inicio + len(MARCA_INICIO))
    if fim < 0:
        raise ErroEstado(f"{caminho.name}: bloco de dados sem `{MARCA_FIM}` de fechamento")
    try:
        dados = json.loads(texto[inicio + len(MARCA_INICIO):fim])
    except json.JSONDecodeError as erro:
        raise ErroEstado(f"{caminho.name}: bloco de dados não é JSON válido ({erro})") from erro
    return validar_estado(dados)


def feita(dados: dict, etapa_id: str) -> bool:
    return dados["etapas"][etapa_id]["situacao"] in FEITAS


def bloqueio(dados: dict, etapa_id: str) -> str | None:
    """A primeira etapa anterior que ainda não foi feita, ou None."""
    for anterior in IDS[:IDS.index(etapa_id)]:
        if not feita(dados, anterior):
            return anterior
    return None


def proxima(dados: dict) -> str | None:
    return next((e for e in IDS if not feita(dados, e)), None)


def _registrar(dados: dict, evento: str) -> None:
    dados["historico"].append({"data": _hoje(), "evento": _texto_limpo(evento)})


def marcar(dados: dict, etapa_id: str, situacao: str, nota: str = "") -> None:
    registro = dados["etapas"][etapa_id]
    registro["situacao"] = situacao
    registro["data"] = _hoje()
    if nota or situacao in FEITAS:
        registro["nota"] = _texto_limpo(nota)
    if situacao in FEITAS:
        registro["argumento"] = ""


def julgar(dados: dict, etapa_id: str, agente: str, resultado: str) -> int:
    """Conta o veredito do agente na etapa; devolve quantos desse resultado ele já tem."""
    contagem = dados["etapas"][etapa_id].setdefault("vereditos", {}).setdefault(agente, {})
    contagem[resultado] = contagem.get(resultado, 0) + 1
    return contagem[resultado]


def resumo_vereditos(registro: dict) -> str:
    """`3✓ 1↻` somando os agentes da etapa; vazio se ninguém foi julgado."""
    totais = {r: sum(c.get(r, 0) for c in registro.get("vereditos", {}).values()) for r in VEREDITOS}
    return " ".join(f"{n}{VEREDITOS[r][0]}" for r, n in totais.items() if n)


def reabrir(dados: dict, etapa_id: str, motivo: str, argumento: str = "") -> list[str]:
    reabertas = []
    for posterior in IDS[IDS.index(etapa_id):]:
        registro = dados["etapas"][posterior]
        if posterior == etapa_id or registro["situacao"] != "pendente":
            nota = motivo if posterior == etapa_id else f"reaberta junto com {etapa_id}"
            marcar(dados, posterior, "reaberta", nota)
            registro["argumento"] = _texto_limpo(argumento) if posterior == etapa_id else ""
            reabertas.append(posterior)
    return reabertas


# ---------------------------------------------------------------- texto

def barra(dados: dict) -> str:
    total = len(IDS)
    feitas = sum(feita(dados, e) for e in IDS)
    cheios = round(LARGURA_BARRA * feitas / total)
    return f"{'█' * cheios}{'░' * (LARGURA_BARRA - cheios)} {round(100 * feitas / total)}% ({feitas} de {total} etapas)"


def bloco_proximo(dados: dict) -> str:
    etapa_id = proxima(dados)
    if etapa_id is None:
        return "\n".join([
            LINHA, "", "## 🎉 App publicado", "",
            "Todas as etapas estão concluídas. Mudança nova no app: descreva o que quer e o orquestrador",
            "(skill `power-platform`) escolhe o caminho; para ver o histórico, `/pp:progresso`.", "", LINHA,
        ])
    etapa = POR_ID[etapa_id]
    registro = dados["etapas"][etapa_id]
    linhas = [LINHA, "", "## ▶ Próximo passo", "",
              f"**Etapa {IDS.index(etapa_id) + 1} de {len(IDS)} · {etapa.titulo}** — {etapa.agente}: {etapa.entrega}"]
    if registro["situacao"] == "reaberta":
        linhas.append(f"<sub>↺ Reaberta: {registro['nota']}</sub>")
    elif registro["situacao"] == "andamento":
        linhas.append(f"<sub>◆ Em andamento desde {registro['data']}: rodar de novo retoma de onde parou.</sub>")
    linhas += ["", f"`{_comando(etapa_id, registro['argumento'])}`", "",
               "<sub>Abra uma nova sessão antes: digite `/clear` (ou feche e abra o Claude Code na pasta do "
               "projeto). Cada etapa começa limpa e lê tudo do disco.</sub>", "", LINHA, "", "**Também disponível:**"]
    for comando, descricao in ALTERNATIVAS.get(etapa_id, []):
        if comando != _comando(etapa_id, registro["argumento"]):
            linhas.append(f"- `{comando}` — {descricao}")
    linhas += ["- `/pp:progresso` — ver o painel do projeto", "", LINHA]
    return "\n".join(linhas)


def tabela(dados: dict) -> str:
    linhas = ["| # | Bloco | Etapa | Comando | Quem executa | Situação | Data | Julgamento | Observação |",
              "|---|---|---|---|---|---|---|---|---|"]
    for numero, etapa in enumerate(ETAPAS, start=1):
        registro = dados["etapas"][etapa.id]
        linhas.append(f"| {numero} | {etapa.bloco} | {etapa.titulo} | `{_comando(etapa.id)}` | {etapa.agente} | "
                      f"{SIMBOLO[registro['situacao']]} | {registro['data']} | {resumo_vereditos(registro)} | "
                      f"{registro['nota']} |")
    return "\n".join(linhas)


def renderizar(dados: dict) -> str:
    historico = [f"- {h['data']} — {h['evento']}" for h in reversed(dados["historico"][-HISTORICO_VISIVEL:])]
    partes = [
        f"# Estado do projeto — {dados['projeto']}", "",
        "> Atualizado pelos comandos `/pp:*` (script `estado.py` da skill `power-platform`). Não edite à mão:",
        "> cada atualização reescreve este arquivo a partir do bloco de dados no fim.", "",
        f"**Ideia:** {dados['ideia'] or '—'}  ",
        f"**Início:** {dados.get('criado', '')} · **Progresso:** {barra(dados)}", "",
        "## Etapas", "", tabela(dados), "",
        bloco_proximo(dados), "",
        f"## Histórico (últimos {HISTORICO_VISIVEL}, mais recente primeiro)", "",
        *(historico or ["- (vazio)"]), "",
        MARCA_INICIO, json.dumps(dados, ensure_ascii=False, indent=1), MARCA_FIM, "",
    ]
    return "\n".join(partes)


def gravar(caminho: Path, dados: dict) -> None:
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(renderizar(dados), encoding="utf-8")
    os.replace(temporario, caminho)


def caixa_erro(titulo: str, corpo: str) -> str:
    largura = 62
    return "\n".join(["╔" + "═" * largura + "╗", f"║  {titulo:<{largura - 2}}║", "╚" + "═" * largura + "╝", "", corpo])


def banner(titulo: str) -> str:
    return "\n".join([BANNER, f" PP ► {titulo.upper()}", BANNER])


# ---------------------------------------------------------------- comandos

def _exigir_ordem(dados: dict, etapa_id: str) -> int:
    anterior = bloqueio(dados, etapa_id)
    if anterior is None:
        return 0
    situacao = SIMBOLO[dados["etapas"][anterior]["situacao"]]
    print(caixa_erro(f"ETAPA FORA DE ORDEM: {POR_ID[etapa_id].titulo}",
                     f"`{_comando(etapa_id)}` depende de **{POR_ID[anterior].titulo}** ({situacao}).\n"
                     f"**Para seguir:** rode a etapa que falta, numa nova sessão."))
    print()
    print(bloco_proximo(dados))
    return 1


def cmd_iniciar(args: argparse.Namespace) -> int:
    raiz = (args.raiz or Path.cwd()).resolve()
    caminho = raiz / NOME_ARQUIVO
    if caminho.exists():
        raise ErroEstado(f"{caminho} já existe: este projeto já foi iniciado (use `mostrar`)")
    if not args.projeto.strip():
        raise ErroEstado("--projeto vazio")
    dados = estado_novo(args.projeto, args.ideia or "")
    marcar(dados, "novo", "concluida", "projeto iniciado")
    _registrar(dados, "início do projeto")
    gravar(caminho, dados)
    print(f"✓ {NOME_ARQUIVO} criado em {caminho.parent.name}/")
    print()
    print(bloco_proximo(dados))
    return 0


def cmd_mostrar(caminho: Path, dados: dict, _: argparse.Namespace) -> int:
    print(banner(f"progresso — {dados['projeto']}"))
    print()
    print(f"**Progresso:** {barra(dados)}")
    print()
    print(tabela(dados))
    print()
    print(bloco_proximo(dados))
    return 0


def cmd_checar(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    codigo = _exigir_ordem(dados, args.etapa)
    if codigo == 0 and feita(dados, args.etapa):
        print(f"⚠ {POR_ID[args.etapa].titulo} já foi feita em {dados['etapas'][args.etapa]['data']}: "
              "rodar de novo refaz a etapa.")
    return codigo


def cmd_comecar(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    codigo = cmd_checar(caminho, dados, args)
    if codigo:
        return codigo
    registro = dados["etapas"][args.etapa]
    if registro["situacao"] != "andamento":
        argumento = registro["argumento"]
        marcar(dados, args.etapa, "andamento", registro["nota"] if registro["situacao"] == "reaberta" else "")
        registro["argumento"] = argumento
        _registrar(dados, f"{args.etapa}: começou")
        gravar(caminho, dados)
    print(banner(POR_ID[args.etapa].titulo))
    return 0


def cmd_concluir(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    codigo = _exigir_ordem(dados, args.etapa)
    if codigo:
        return codigo
    marcar(dados, args.etapa, "concluida", args.nota or "")
    _registrar(dados, f"{args.etapa}: concluída" + (f" — {args.nota}" if args.nota else ""))
    gravar(caminho, dados)
    print(f"✓ {POR_ID[args.etapa].titulo} concluída · progresso {barra(dados)}")
    print()
    print(bloco_proximo(dados))
    return 0


def cmd_dispensar(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    if args.etapa == "novo":
        raise ErroEstado("a etapa `novo` não se dispensa")
    marcar(dados, args.etapa, "dispensada", args.motivo)
    _registrar(dados, f"{args.etapa}: dispensada — {args.motivo}")
    gravar(caminho, dados)
    print(f"⊘ {POR_ID[args.etapa].titulo} dispensada: {_texto_limpo(args.motivo)}")
    print()
    print(bloco_proximo(dados))
    return 0


def cmd_reabrir(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    if args.etapa == "novo":
        raise ErroEstado("a etapa `novo` não se reabre")
    reabertas = reabrir(dados, args.etapa, args.motivo, args.argumento or "")
    _registrar(dados, f"{args.etapa}: reaberta — {args.motivo}")
    gravar(caminho, dados)
    print(f"↺ Reabertas: {', '.join(POR_ID[e].titulo for e in reabertas)}")
    print()
    print(bloco_proximo(dados))
    return 0


def cmd_veredito(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    agente = _texto_limpo(args.agente)
    if not agente:
        raise ErroEstado("--agente vazio")
    simbolo, rotulo = VEREDITOS[args.resultado]
    vezes = julgar(dados, args.etapa, agente, args.resultado)
    motivo = f" — {_texto_limpo(args.motivo)}" if args.motivo.strip() else ""
    _registrar(dados, f"{args.etapa} · {agente}: {simbolo} {rotulo}{motivo}")
    gravar(caminho, dados)
    print(f"{simbolo} {agente}: {rotulo}{motivo} ({vezes} {rotulo} na etapa {POR_ID[args.etapa].titulo})")
    return 0


def cmd_proximo(caminho: Path, dados: dict, _: argparse.Namespace) -> int:
    print(bloco_proximo(dados))
    return 0


COMANDOS = {"mostrar": cmd_mostrar, "checar": cmd_checar, "comecar": cmd_comecar, "concluir": cmd_concluir,
            "dispensar": cmd_dispensar, "reabrir": cmd_reabrir, "proximo": cmd_proximo,
            "veredito": cmd_veredito}


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Estado do pipeline do projeto (ESTADO.md) e o próximo comando /pp:*.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Etapas, em ordem: " + " → ".join(IDS) + "\nExit: 0 ok, 1 etapa anterior pendente, 2 uso/arquivo.")
    ap.add_argument("--raiz", type=Path, help=f"pasta do projeto (default: procura {NOME_ARQUIVO} para cima)")
    sub = ap.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("iniciar", help="cria o ESTADO.md")
    p.add_argument("--projeto", required=True, help="nome do projeto")
    p.add_argument("--ideia", default="", help="a ideia do app em uma frase")
    sub.add_parser("mostrar", help="painel do projeto")
    sub.add_parser("proximo", help="só o bloco Próximo passo")
    for nome, ajuda in (("checar", "confere se as etapas anteriores estão feitas"),
                        ("comecar", "checar + marca em andamento")):
        sub.add_parser(nome, help=ajuda).add_argument("etapa", choices=IDS)
    p = sub.add_parser("concluir", help="marca a etapa concluída")
    p.add_argument("etapa", choices=IDS)
    p.add_argument("--nota", default="", help="o que ficou pronto (uma frase)")
    p = sub.add_parser("dispensar", help="conta a etapa como feita, com motivo")
    p.add_argument("etapa", choices=IDS)
    p.add_argument("--motivo", required=True)
    p = sub.add_parser("reabrir", help="reabre a etapa e as seguintes")
    p.add_argument("etapa", choices=IDS)
    p.add_argument("--motivo", required=True)
    p.add_argument("--argumento", default="", help="argumento do comando sugerido (ex.: app, flows)")
    p = sub.add_parser("veredito", help="registra o julgamento da entrega de um agente")
    p.add_argument("etapa", choices=IDS)
    p.add_argument("--agente", required=True, help="nome do agente (ex.: agente-canvas)")
    p.add_argument("--resultado", required=True, choices=list(VEREDITOS))
    p.add_argument("--motivo", default="", help="o que faltou ou o que foi escalado (uma frase)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    try:
        if args.comando == "iniciar":
            return cmd_iniciar(args)
        caminho = (args.raiz.resolve() / NOME_ARQUIVO) if args.raiz else achar_estado(Path.cwd().resolve())
        if caminho is None or not caminho.is_file():
            raise ErroEstado(f"nenhum {NOME_ARQUIVO} aqui nem nas pastas acima: comece com `/pp:novo`")
        return COMANDOS[args.comando](caminho, ler_estado(caminho), args)
    except ErroEstado as erro:
        print(f"ERRO {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
