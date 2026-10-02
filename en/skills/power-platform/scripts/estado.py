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

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

NOME_ARQUIVO = tr("ESTADO.md", "STATE.md")
NOME_CONFIG = "power-platform.config.json"
PREFIXO_COMANDO = tr("/pp:", "/pp-en:")
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
    id_en: str = ""  # id da etapa no plugin en-US; o dado gravado usa sempre `id`


ETAPAS: tuple[Etapa, ...] = (
    Etapa("novo", tr("Início", "Start"), tr("Início do projeto", "Project start"),
          tr("Orquestrador", "Orchestrator"),
          tr("pasta, git, config e ESTADO.md", "folder, git, config and STATE.md"), "new"),
    Etapa("brainstorm", tr("1. Definição do produto", "1. Product definition"),
          tr("Brainstorm e requisitos", "Brainstorm and requirements"),
          tr("Agente Brainstorm", "Brainstorm Agent"),
          tr("requisitos, funcionalidades e escopo do MVP", "requirements, features and MVP scope"),
          "brainstorm"),
    Etapa("design", tr("2. Identidade e experiência", "2. Identity and experience"),
          tr("Identidade visual", "Visual identity"),
          tr("Agente Designer Branding", "Branding Designer Agent"),
          tr("cores, fontes, componentes e identidade visual",
             "colors, fonts, components and visual identity"), "design"),
    Etapa("mockups", tr("2. Identidade e experiência", "2. Identity and experience"),
          tr("Mockups em imagem", "Image mockups"),
          tr("Agente de Mockups em Imagem", "Image Mockups Agent"),
          tr("telas, navegação, loading, erros e estados vazios",
             "screens, navigation, loading, errors and empty states"), "mockups"),
    Etapa("prototipo", tr("2. Identidade e experiência", "2. Identity and experience"),
          tr("Protótipo navegável", "Clickable prototype"),
          tr("Agente Gerador de Mockup HTML", "HTML Mockup Generator Agent"),
          tr("protótipo navegável aprovado pelo usuário", "clickable prototype approved by the user"),
          "prototype"),
    Etapa("arquitetura", tr("3. Construção na Power Platform", "3. Build on the Power Platform"),
          tr("Arquitetura", "Architecture"),
          tr("Agente de Arquitetura", "Architecture Agent"),
          tr("modelo de dados, permissões, integrações e fila de construção",
             "data model, permissions, integrations and build queue"), "architecture"),
    Etapa("construir", tr("3. Construção na Power Platform", "3. Build on the Power Platform"),
          tr("Construção", "Build"),
          tr("Agentes Power Apps Canvas e Power Automate",
             "Power Apps Canvas and Power Automate Agents"),
          tr("telas, fórmulas Power Fx, fluxos e app integrado às automações",
             "screens, Power Fx formulas, flows and the app wired to the automations"), "build"),
    Etapa("testar", tr("4. Validação e entrega", "4. Validation and delivery"),
          tr("Testes e qualidade", "Tests and quality"),
          tr("Agente de Testes e Qualidade", "Testing and Quality Agent"),
          tr("validadores, testes de negação e ciclo completo no dado",
             "validators, denial tests and the full cycle on real data"), "test"),
    Etapa("homologar", tr("4. Validação e entrega", "4. Validation and delivery"),
          tr("Homologação", "User acceptance"),
          tr("Orquestrador, com o usuário", "Orchestrator, with the user"),
          tr("aceite dos usuários reais no ambiente de homologação",
             "acceptance by real users in the UAT environment"), "uat"),
    Etapa("publicar", tr("4. Validação e entrega", "4. Validation and delivery"),
          tr("Publicação e documentação", "Publishing and documentation"),
          tr("Orquestrador", "Orchestrator"),
          tr("app em produção, manual do usuário e guia técnico",
             "app in production, user manual and technical guide"), "publish"),
)
IDS = tuple(e.id for e in ETAPAS)
POR_ID = {e.id: e for e in ETAPAS}
IDS_EN = tuple(e.id_en for e in ETAPAS)
ID_PARA_PT = {**{e.id_en: e.id for e in ETAPAS}, **{e.id: e.id for e in ETAPAS}}
IDS_IDIOMA = tuple(tr(e.id, e.id_en) for e in ETAPAS)  # os ids que o usuário vê

FEITAS = {"concluida", "dispensada"}
SITUACOES = {"pendente", "andamento", "concluida", "dispensada", "reaberta"}
SIMBOLO = {"concluida": tr("✓ concluída", "✓ done"), "dispensada": tr("⊘ dispensada", "⊘ skipped"),
           "andamento": tr("◆ em andamento", "◆ in progress"),
           "reaberta": tr("↺ reaberta", "↺ reopened"), "pendente": tr("○ pendente", "○ pending")}
VEREDITOS = {"aceito": ("✓", tr("aceito", "accepted")), "revisao": ("↻", tr("revisão", "revision")),
             "escalado": ("⚠", tr("escalado", "escalated"))}

ALTERNATIVAS = {
    "construir": [(PREFIXO_COMANDO + tr("construir app", "build app"),
                   tr("só as telas (Agente Power Apps Canvas)", "only the screens (Power Apps Canvas Agent)")),
                  (PREFIXO_COMANDO + tr("construir flows", "build flows"),
                   tr("só os fluxos e as procedures (Agentes Power Automate e SQL)",
                      "only the flows and the procedures (Power Automate and SQL Agents)"))],
    "prototipo": [(PREFIXO_COMANDO + "design",
                   tr("voltar para a identidade visual", "go back to the visual identity"))],
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


def _id(etapa_id: str) -> str:
    """O id da etapa no idioma do script (o dado gravado usa sempre o id pt-BR)."""
    return tr(etapa_id, POR_ID[etapa_id].id_en)


def _comando(etapa_id: str, argumento: str = "") -> str:
    return f"{PREFIXO_COMANDO}{_id(etapa_id)}" + (f" {argumento}" if argumento else "")


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
        raise ErroEstado(tr("bloco de dados sem `etapas`", "data block without `etapas`"))
    for etapa_id in IDS:
        registro = dados["etapas"].get(etapa_id)
        if not isinstance(registro, dict) or registro.get("situacao") not in SITUACOES:
            raise ErroEstado(tr(f"etapa `{etapa_id}` ausente ou com situação inválida no bloco de dados",
                              f"stage `{etapa_id}` missing or with an invalid status in the data block"))
        for campo in ("data", "nota", "argumento"):
            registro.setdefault(campo, "")
        if not _vereditos_validos(registro.get("vereditos", {})):
            raise ErroEstado(tr(f"etapa `{etapa_id}`: `vereditos` inválido no bloco de dados",
                              f"stage `{etapa_id}`: invalid `vereditos` in the data block"))
    dados.setdefault("historico", [])
    dados.setdefault("projeto", tr("projeto", "project"))
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
        raise ErroEstado(tr(f"{caminho.name} sem o bloco `{MARCA_INICIO}` (foi editado à mão?)",
                          f"{caminho.name} has no `{MARCA_INICIO}` block (was it edited by hand?)"))
    fim = texto.find(MARCA_FIM, inicio + len(MARCA_INICIO))
    if fim < 0:
        raise ErroEstado(tr(f"{caminho.name}: bloco de dados sem `{MARCA_FIM}` de fechamento",
                          f"{caminho.name}: data block without the closing `{MARCA_FIM}`"))
    try:
        dados = json.loads(texto[inicio + len(MARCA_INICIO):fim])
    except json.JSONDecodeError as erro:
        raise ErroEstado(tr(f"{caminho.name}: bloco de dados não é JSON válido ({erro})",
                          f"{caminho.name}: data block is not valid JSON ({erro})")) from erro
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
            nota = motivo if posterior == etapa_id else tr(f"reaberta junto com {_id(etapa_id)}", f"reopened together with {_id(etapa_id)}")
            marcar(dados, posterior, "reaberta", nota)
            registro["argumento"] = _texto_limpo(argumento) if posterior == etapa_id else ""
            reabertas.append(posterior)
    return reabertas


# ---------------------------------------------------------------- texto

def barra(dados: dict) -> str:
    total = len(IDS)
    feitas = sum(feita(dados, e) for e in IDS)
    cheios = round(LARGURA_BARRA * feitas / total)
    return f"{'█' * cheios}{'░' * (LARGURA_BARRA - cheios)} {round(100 * feitas / total)}% " + tr(f"({feitas} de {total} etapas)", f"({feitas} of {total} stages)")


def modelo_da_sessao(raiz: Path | None) -> str:
    """`modelos.sessao` do config do projeto (escolhido no /pp:novo); vazio se não há."""
    if raiz is None or not (raiz / NOME_CONFIG).is_file():
        return ""
    try:
        config = json.loads((raiz / NOME_CONFIG).read_text(encoding="utf-8-sig"))
    except (ValueError, OSError):
        return ""
    modelos = config.get("modelos") if isinstance(config, dict) else None
    sessao = modelos.get("sessao", "") if isinstance(modelos, dict) else ""
    return _texto_limpo(sessao) if isinstance(sessao, str) else ""


def bloco_proximo(dados: dict, raiz: Path | None = None) -> str:
    etapa_id = proxima(dados)
    if etapa_id is None:
        return "\n".join([
            LINHA, "", tr("## 🎉 App publicado", "## 🎉 App published"), "",
            tr(f"Todas as etapas estão concluídas. Mudanças no app (corrigir, ajustar, acrescentar): `{PREFIXO_COMANDO}mudanca`",
               f"All stages are done. Changes to the app (fix, adjust, add): `{PREFIXO_COMANDO}change`"),
            tr(f"com a lista, numa sessão nova. Para ver o histórico, `{PREFIXO_COMANDO}progresso`.",
               f"with the list, in a new session. To see the history, `{PREFIXO_COMANDO}progress`."), "", LINHA,
        ])
    etapa = POR_ID[etapa_id]
    registro = dados["etapas"][etapa_id]
    linhas = [LINHA, "", tr("## ▶ Próximo passo", "## ▶ Next step"), "",
              tr(f"**Etapa {IDS.index(etapa_id) + 1} de {len(IDS)} · {etapa.titulo}** — {etapa.agente}: {etapa.entrega}",
                 f"**Stage {IDS.index(etapa_id) + 1} of {len(IDS)} · {etapa.titulo}** — {etapa.agente}: {etapa.entrega}")]
    if registro["situacao"] == "reaberta":
        linhas.append(tr(f"<sub>↺ Reaberta: {registro['nota']}</sub>", f"<sub>↺ Reopened: {registro['nota']}</sub>"))
    elif registro["situacao"] == "andamento":
        linhas.append(tr(f"<sub>◆ Em andamento desde {registro['data']}: rodar de novo retoma de onde parou.</sub>",
                         f"<sub>◆ In progress since {registro['data']}: running it again resumes where it stopped.</sub>"))
    linhas += ["", f"`{_comando(etapa_id, registro['argumento'])}`", "",
               tr("<sub>Abra uma nova sessão antes: digite `/clear` (ou feche e abra o Claude Code na pasta do "
                  "projeto). Cada etapa começa limpa e lê tudo do disco.</sub>",
                  "<sub>Open a new session first: type `/clear` (or close and reopen Claude Code in the project "
                  "folder). Each stage starts clean and reads everything from disk.</sub>")]
    sessao = modelo_da_sessao(raiz)
    if sessao:
        linhas.append(tr(f"<sub>Modelo desta sessão: **{sessao}** (escolhido no `{_comando('novo')}`). Se o Claude Code abrir "
                         f"em outro, digite `/model {sessao}`.</sub>",
                         f"<sub>Model for this session: **{sessao}** (chosen in `{_comando('novo')}`). If Claude Code opens "
                         f"on another one, type `/model {sessao}`.</sub>"))
    linhas += ["", LINHA, "", tr("**Também disponível:**", "**Also available:**")]
    for comando, descricao in ALTERNATIVAS.get(etapa_id, []):
        if comando != _comando(etapa_id, registro["argumento"]):
            linhas.append(f"- `{comando}` — {descricao}")
    linhas += [f"- `{PREFIXO_COMANDO}" + tr("progresso", "progress") + "` — "
               + tr("ver o painel do projeto", "see the project panel"), "", LINHA]
    return "\n".join(linhas)


def tabela(dados: dict) -> str:
    linhas = [tr("| # | Bloco | Etapa | Comando | Quem executa | Situação | Data | Julgamento | Observação |",
                 "| # | Block | Stage | Command | Who runs it | Status | Date | Verdict | Note |"),
              "|---|---|---|---|---|---|---|---|---|"]
    for numero, etapa in enumerate(ETAPAS, start=1):
        registro = dados["etapas"][etapa.id]
        linhas.append(f"| {numero} | {etapa.bloco} | {etapa.titulo} | `{_comando(etapa.id)}` | {etapa.agente} | "
                      f"{SIMBOLO[registro['situacao']]} | {registro['data']} | {resumo_vereditos(registro)} | "
                      f"{registro['nota']} |")
    return "\n".join(linhas)


def renderizar(dados: dict, raiz: Path | None = None) -> str:
    historico = [f"- {h['data']} — {h['evento']}" for h in reversed(dados["historico"][-HISTORICO_VISIVEL:])]
    partes = [
        tr(f"# Estado do projeto — {dados['projeto']}", f"# Project state — {dados['projeto']}"), "",
        tr(f"> Atualizado pelos comandos `{PREFIXO_COMANDO}*` (script `estado.py` da skill `power-platform`). Não edite à mão:",
           f"> Updated by the `{PREFIXO_COMANDO}*` commands (`estado.py` script of the `power-platform` skill). Do not edit by hand:"),
        tr("> cada atualização reescreve este arquivo a partir do bloco de dados no fim.",
           "> every update rewrites this file from the data block at the end."), "",
        tr(f"**Ideia:** {dados['ideia'] or '—'}  ", f"**Idea:** {dados['ideia'] or '—'}  "),
        tr(f"**Início:** {dados.get('criado', '')} · **Progresso:** {barra(dados)}",
           f"**Started:** {dados.get('criado', '')} · **Progress:** {barra(dados)}"), "",
        tr("## Etapas", "## Stages"), "", tabela(dados), "",
        bloco_proximo(dados, raiz), "",
        tr(f"## Histórico (últimos {HISTORICO_VISIVEL}, mais recente primeiro)",
           f"## History (last {HISTORICO_VISIVEL}, most recent first)"), "",
        *(historico or [tr("- (vazio)", "- (empty)")]), "",
        MARCA_INICIO, json.dumps(dados, ensure_ascii=False, indent=1), MARCA_FIM, "",
    ]
    return "\n".join(partes)


def gravar(caminho: Path, dados: dict) -> None:
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(renderizar(dados, caminho.parent), encoding="utf-8")
    os.replace(temporario, caminho)


def caixa_erro(titulo: str, corpo: str) -> str:
    largura = 62
    return "\n".join(["╔" + "═" * largura + "╗", f"║  {titulo:<{largura - 2}}║", "╚" + "═" * largura + "╝", "", corpo])


def banner(titulo: str) -> str:
    return "\n".join([BANNER, f" PP ► {titulo.upper()}", BANNER])


# ---------------------------------------------------------------- comandos

def _exigir_ordem(dados: dict, etapa_id: str, raiz: Path) -> int:
    anterior = bloqueio(dados, etapa_id)
    if anterior is None:
        return 0
    situacao = SIMBOLO[dados["etapas"][anterior]["situacao"]]
    print(caixa_erro(tr(f"ETAPA FORA DE ORDEM: {POR_ID[etapa_id].titulo}",
                        f"STAGE OUT OF ORDER: {POR_ID[etapa_id].titulo}"),
                     tr(f"`{_comando(etapa_id)}` depende de **{POR_ID[anterior].titulo}** ({situacao}).\n"
                        f"**Para seguir:** rode a etapa que falta, numa nova sessão.",
                        f"`{_comando(etapa_id)}` depends on **{POR_ID[anterior].titulo}** ({situacao}).\n"
                        f"**To continue:** run the missing stage, in a new session.")))
    print()
    print(bloco_proximo(dados, raiz))
    return 1


def cmd_iniciar(args: argparse.Namespace) -> int:
    raiz = (args.raiz or Path.cwd()).resolve()
    caminho = raiz / NOME_ARQUIVO
    if caminho.exists():
        raise ErroEstado(tr(f"{caminho} já existe: este projeto já foi iniciado (use `mostrar`)",
                        f"{caminho} already exists: this project was already started (use `mostrar`)"))
    if not args.projeto.strip():
        raise ErroEstado(tr("--projeto vazio", "--projeto is empty"))
    dados = estado_novo(args.projeto, args.ideia or "")
    marcar(dados, "novo", "concluida", tr("projeto iniciado", "project started"))
    _registrar(dados, tr("início do projeto", "project start"))
    gravar(caminho, dados)
    print(tr(f"✓ {NOME_ARQUIVO} criado em {caminho.parent.name}/", f"✓ {NOME_ARQUIVO} created in {caminho.parent.name}/"))
    print()
    print(bloco_proximo(dados, caminho.parent))
    return 0


def cmd_mostrar(caminho: Path, dados: dict, _: argparse.Namespace) -> int:
    print(banner(tr(f"progresso — {dados['projeto']}", f"progress — {dados['projeto']}")))
    print()
    print(tr(f"**Progresso:** {barra(dados)}", f"**Progress:** {barra(dados)}"))
    print()
    print(tabela(dados))
    print()
    print(bloco_proximo(dados, caminho.parent))
    return 0


def cmd_checar(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    codigo = _exigir_ordem(dados, args.etapa, caminho.parent)
    if codigo == 0 and feita(dados, args.etapa):
        print(tr(f"⚠ {POR_ID[args.etapa].titulo} já foi feita em {dados['etapas'][args.etapa]['data']}: "
                 "rodar de novo refaz a etapa.",
                 f"⚠ {POR_ID[args.etapa].titulo} was already done on {dados['etapas'][args.etapa]['data']}: "
                 "running it again redoes the stage."))
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
        _registrar(dados, tr(f"{args.etapa}: começou", f"{_id(args.etapa)}: started"))
        gravar(caminho, dados)
    print(banner(POR_ID[args.etapa].titulo))
    return 0


def cmd_concluir(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    codigo = _exigir_ordem(dados, args.etapa, caminho.parent)
    if codigo:
        return codigo
    marcar(dados, args.etapa, "concluida", args.nota or "")
    _registrar(dados, tr(f"{args.etapa}: concluída", f"{_id(args.etapa)}: done") + (f" — {args.nota}" if args.nota else ""))
    gravar(caminho, dados)
    print(tr(f"✓ {POR_ID[args.etapa].titulo} concluída · progresso {barra(dados)}",
               f"✓ {POR_ID[args.etapa].titulo} done · progress {barra(dados)}"))
    print()
    print(bloco_proximo(dados, caminho.parent))
    return 0


def cmd_dispensar(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    if args.etapa == "novo":
        raise ErroEstado(tr("a etapa `novo` não se dispensa", "the `new` stage cannot be skipped"))
    marcar(dados, args.etapa, "dispensada", args.motivo)
    _registrar(dados, tr(f"{args.etapa}: dispensada — {args.motivo}", f"{_id(args.etapa)}: skipped — {args.motivo}"))
    gravar(caminho, dados)
    print(tr(f"⊘ {POR_ID[args.etapa].titulo} dispensada: {_texto_limpo(args.motivo)}",
               f"⊘ {POR_ID[args.etapa].titulo} skipped: {_texto_limpo(args.motivo)}"))
    print()
    print(bloco_proximo(dados, caminho.parent))
    return 0


def cmd_reabrir(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    if args.etapa == "novo":
        raise ErroEstado(tr("a etapa `novo` não se reabre", "the `new` stage cannot be reopened"))
    reabertas = reabrir(dados, args.etapa, args.motivo, args.argumento or "")
    _registrar(dados, tr(f"{args.etapa}: reaberta — {args.motivo}", f"{_id(args.etapa)}: reopened — {args.motivo}"))
    gravar(caminho, dados)
    lista = ", ".join(POR_ID[e].titulo for e in reabertas)
    print(tr(f"↺ Reabertas: {lista}", f"↺ Reopened: {lista}"))
    print()
    print(bloco_proximo(dados, caminho.parent))
    return 0


def cmd_veredito(caminho: Path, dados: dict, args: argparse.Namespace) -> int:
    agente = _texto_limpo(args.agente)
    if not agente:
        raise ErroEstado(tr("--agente vazio", "--agente is empty"))
    simbolo, rotulo = VEREDITOS[args.resultado]
    vezes = julgar(dados, args.etapa, agente, args.resultado)
    motivo = f" — {_texto_limpo(args.motivo)}" if args.motivo.strip() else ""
    _registrar(dados, f"{_id(args.etapa)} · {agente}: {simbolo} {rotulo}{motivo}")
    gravar(caminho, dados)
    print(tr(f"{simbolo} {agente}: {rotulo}{motivo} ({vezes} {rotulo} na etapa {POR_ID[args.etapa].titulo})",
               f"{simbolo} {agente}: {rotulo}{motivo} ({vezes} {rotulo} in stage {POR_ID[args.etapa].titulo})"))
    return 0


def cmd_proximo(caminho: Path, dados: dict, _: argparse.Namespace) -> int:
    print(bloco_proximo(dados, caminho.parent))
    return 0


COMANDOS = {"mostrar": cmd_mostrar, "checar": cmd_checar, "comecar": cmd_comecar, "concluir": cmd_concluir,
            "dispensar": cmd_dispensar, "reabrir": cmd_reabrir, "proximo": cmd_proximo,
            "veredito": cmd_veredito}


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=tr(f"Estado do pipeline do projeto ({NOME_ARQUIVO}) e o próximo comando {PREFIXO_COMANDO}*.",
                       f"Project pipeline state ({NOME_ARQUIVO}) and the next {PREFIXO_COMANDO}* command."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=tr("Etapas, em ordem: ", "Stages, in order: ") + " → ".join(IDS_IDIOMA)
        + tr("\nExit: 0 ok, 1 etapa anterior pendente, 2 uso/arquivo.",
             "\nExit: 0 ok, 1 previous stage pending, 2 usage/file."))
    ap.add_argument("--raiz", type=Path,
                    help=tr(f"pasta do projeto (default: procura {NOME_ARQUIVO} para cima)",
                            f"project folder (default: searches upward for {NOME_ARQUIVO})"))
    sub = ap.add_subparsers(dest="comando", required=True)

    def etapa(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("etapa", choices=(*IDS, *IDS_EN), metavar="{" + ",".join(IDS_IDIOMA) + "}")

    p = sub.add_parser("iniciar", help=tr("cria o ESTADO.md", "creates STATE.md"))
    p.add_argument("--projeto", required=True, help=tr("nome do projeto", "project name"))
    p.add_argument("--ideia", default="", help=tr("a ideia do app em uma frase", "the app idea in one sentence"))
    sub.add_parser("mostrar", help=tr("painel do projeto", "project panel"))
    sub.add_parser("proximo", help=tr("só o bloco Próximo passo", "only the Next step block"))
    for nome, ajuda in (("checar", tr("confere se as etapas anteriores estão feitas", "checks that the previous stages are done")),
                        ("comecar", tr("checar + marca em andamento", "check + mark in progress"))):
        etapa(sub.add_parser(nome, help=ajuda))
    p = sub.add_parser("concluir", help=tr("marca a etapa concluída", "marks the stage done"))
    etapa(p)
    p.add_argument("--nota", default="", help=tr("o que ficou pronto (uma frase)", "what is ready (one sentence)"))
    p = sub.add_parser("dispensar", help=tr("conta a etapa como feita, com motivo", "counts the stage as done, with a reason"))
    etapa(p)
    p.add_argument("--motivo", required=True)
    p = sub.add_parser("reabrir", help=tr("reabre a etapa e as seguintes", "reopens the stage and the following ones"))
    etapa(p)
    p.add_argument("--motivo", required=True)
    p.add_argument("--argumento", default="",
                   help=tr("argumento do comando sugerido (ex.: app, flows)", "argument of the suggested command (e.g. app, flows)"))
    p = sub.add_parser("veredito", help=tr("registra o julgamento da entrega de um agente",
                                           "records the verdict on an agent's delivery"))
    etapa(p)
    p.add_argument("--agente", required=True,
                   help=tr("nome do agente (ex.: agente-canvas)", "agent name (e.g. canvas-agent)"))
    p.add_argument("--resultado", required=True, choices=list(VEREDITOS))
    p.add_argument("--motivo", default="",
                   help=tr("o que faltou ou o que foi escalado (uma frase)", "what was missing or escalated (one sentence)"))
    args = ap.parse_args(argv)
    if hasattr(args, "etapa"):
        args.etapa = ID_PARA_PT[args.etapa]
    return args


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    try:
        if args.comando == "iniciar":
            return cmd_iniciar(args)
        caminho = (args.raiz.resolve() / NOME_ARQUIVO) if args.raiz else achar_estado(Path.cwd().resolve())
        if caminho is None or not caminho.is_file():
            raise ErroEstado(tr(f"nenhum {NOME_ARQUIVO} aqui nem nas pastas acima: comece com `{_comando('novo')}`",
                              f"no {NOME_ARQUIVO} here or in the folders above: start with `{_comando('novo')}`"))
        return COMANDOS[args.comando](caminho, ler_estado(caminho), args)
    except ErroEstado as erro:
        print(tr("ERRO", "ERROR") + f" {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
