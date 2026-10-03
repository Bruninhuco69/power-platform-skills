#!/usr/bin/env python3
"""Modelos do projeto: quem pensa (a sessão de cada etapa) e quem executa (os agentes).

O perfil escolhido no `/pp:novo` vai para o `power-platform.config.json` (chave `modelos`) e o
modelo da sessão para o `.claude/settings.local.json` do projeto: o Claude Code lê esse arquivo ao
abrir uma sessão na pasta (`/model`, `--model` e a variável ANTHROPIC_MODEL passam por cima). Cada
etapa pergunta aqui o modelo do agente que vai chamar e o passa como `model` na chamada, que vence
o `model` do frontmatter do agente.

Comandos:
  perfis                                 os perfis, com o modelo de cada papel
  aplicar PERFIL [--sessao M] [--planejamento M] [--execucao M] [--pesquisa M]
                                         grava no config e no settings.local.json; as opções trocam
                                         um papel avulso por cima do perfil
  mostrar                                o que o projeto usa hoje, agente por agente
  de AGENTE                              o modelo do agente; linha vazia = herda o da sessão
                                         (não passe `model` na chamada)

Exit: 0 ok · 2 uso incorreto (perfil, modelo, agente, config ausente ou inválida).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

NOME_CONFIG = "power-platform.config.json"
SETTINGS = Path(".claude") / "settings.local.json"
LINHA_GITIGNORE = ".claude/settings.local.json"
PASTA_AGENTES = Path(__file__).resolve().parents[3] / "agents"

MODELOS_SESSAO = ("best", "fable", "opus", "sonnet", "haiku")  # best: Fable se a conta tem, senão Opus
MODELOS_AGENTE = ("fable", "opus", "sonnet", "haiku")

PAPEIS = {
    "sessao": tr("Sessão de cada etapa: conversa, decide, julga",
                 "Each stage's session: talks, decides, judges"),
    "planejamento": tr("Arquitetura e QA: planejam e julgam", "Architecture and QA: plan and judge"),
    "execucao": tr("Mockups, protótipo, telas, fluxos e SQL", "Mockups, prototype, screens, flows and SQL"),
    "pesquisa": tr("Pesquisa: lê o projeto e a documentação", "Research: reads the project and the documentation"),
}
AGENTES = {
    "agente-arquitetura": "planejamento",
    "agente-qa": "planejamento",
    "agente-mockups": "execucao",
    "agente-prototipo": "execucao",
    "agente-canvas": "execucao",
    "agente-automate": "execucao",
    "agente-sql": "execucao",
    "agente-pesquisa": "pesquisa",
}
# Nome do arquivo do agente no plugin en-US; as chaves do config ficam as de AGENTES nos dois idiomas.
AGENTES_EN = {
    "agente-arquitetura": "architecture-agent",
    "agente-qa": "qa-agent",
    "agente-mockups": "mockups-agent",
    "agente-prototipo": "prototype-agent",
    "agente-canvas": "canvas-agent",
    "agente-automate": "automate-agent",
    "agente-sql": "sql-agent",
    "agente-pesquisa": "research-agent",
}
AGENTE_PARA_PT = {**{en: pt for pt, en in AGENTES_EN.items()}, **{pt: pt for pt in AGENTES}}


def _nome_agente(agente: str) -> str:
    """O nome do agente (e do arquivo agents/<nome>.md) no idioma do script."""
    return tr(agente, AGENTES_EN[agente])


@dataclass(frozen=True)
class Perfil:
    id: str
    rotulo: str
    quando: str
    papeis: dict[str, str]


PERFIS = (
    Perfil("equilibrado", tr("Equilibrado", "Balanced"),
           tr("o modelo forte pensa e julga; o rápido executa", "the strong model thinks and judges; the fast one executes"),
           {"sessao": "opus", "planejamento": "opus", "execucao": "sonnet", "pesquisa": "sonnet"}),
    Perfil("maximo", tr("Máximo", "Maximum"),
           tr("o mais forte em tudo o que decide; custa mais", "the strongest on everything that decides; costs more"),
           {"sessao": "best", "planejamento": "opus", "execucao": "opus", "pesquisa": "sonnet"}),
    Perfil("economico", tr("Econômico", "Economical"),
           tr("Sonnet em tudo, Haiku na pesquisa; espere mais revisões",
              "Sonnet on everything, Haiku on research; expect more revisions"),
           {"sessao": "sonnet", "planejamento": "sonnet", "execucao": "sonnet", "pesquisa": "haiku"}),
    Perfil("herdar", tr("Herdar", "Inherit"),
           tr("não força nada: tudo no modelo em que a sessão abrir", "forces nothing: everything on the model the session opens with"),
           {papel: "" for papel in PAPEIS}),
)
POR_ID = {p.id: p for p in PERFIS}
RECOMENDADO = "equilibrado"


class ErroUso(Exception):
    """Perfil, modelo, agente ou config inválidos (exit 2)."""


def _saida_utf8() -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _rotulo_modelo(modelo: str) -> str:
    return modelo or tr("herda a sessão", "inherits the session")


def _perfil_visivel(perfil: str) -> str:
    """O rótulo gravado no config usa sempre `(ajustado)`; na tela vai no idioma do script."""
    return perfil.replace(" (ajustado)", tr(" (ajustado)", " (adjusted)"))


def _linha(rotulo: str, valor: str, largura: int = 46) -> str:
    return f"  {rotulo} {'.' * max(largura - len(rotulo), 3)} {valor}"


# ---------------------------------------------------------------- config

def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_CONFIG
        if candidato.is_file():
            return candidato
    return None


def _ler_json(caminho: Path, nome: str) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as erro:
        raise ErroUso(tr(f"{nome} inválido ({caminho}): {erro}", f"{nome} invalid ({caminho}): {erro}")) from erro
    if not isinstance(dados, dict):
        raise ErroUso(tr(f"{nome} inválido ({caminho}): a raiz precisa ser um objeto",
                       f"{nome} invalid ({caminho}): the root must be an object"))
    return dados


def _gravar_json(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_name(caminho.name + ".tmp")
    with open(temporario, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
    os.replace(temporario, caminho)


def ler_modelos(config: dict) -> dict:
    """O bloco `modelos` validado; ausente = herdar em tudo."""
    bloco = config.get("modelos", {})
    if not isinstance(bloco, dict):
        raise ErroUso(tr("config inválida: `modelos` precisa ser um objeto", "invalid config: `modelos` must be an object"))
    sessao = bloco.get("sessao", "")
    if sessao not in ("", *MODELOS_SESSAO):
        raise ErroUso(tr(f"config inválida: `modelos.sessao` = {sessao!r} (use {', '.join(MODELOS_SESSAO)} ou vazio)",
                       f"invalid config: `modelos.sessao` = {sessao!r} (use {', '.join(MODELOS_SESSAO)} or empty)"))
    agentes = bloco.get("agentes", {})
    if not isinstance(agentes, dict):
        raise ErroUso(tr("config inválida: `modelos.agentes` precisa ser um objeto", "invalid config: `modelos.agentes` must be an object"))
    for agente, modelo in agentes.items():
        if modelo not in ("", *MODELOS_AGENTE):
            raise ErroUso(tr(f"config inválida: `modelos.agentes.{agente}` = {modelo!r} "
                          f"(use {', '.join(MODELOS_AGENTE)} ou vazio)",
                          f"invalid config: `modelos.agentes.{agente}` = {modelo!r} "
                          f"(use {', '.join(MODELOS_AGENTE)} or empty)"))
    return {"perfil": bloco.get("perfil", ""), "sessao": sessao, "agentes": agentes}


def montar_modelos(perfil: Perfil, trocas: dict[str, str]) -> dict:
    papeis = {**perfil.papeis, **{p: m for p, m in trocas.items() if m is not None}}
    for papel, modelo in papeis.items():
        validos = MODELOS_SESSAO if papel == "sessao" else MODELOS_AGENTE
        if modelo not in ("", *validos):
            raise ErroUso(tr(f"modelo inválido para {papel}: {modelo!r} (use {', '.join(validos)})",
                          f"invalid model for {papel}: {modelo!r} (use {', '.join(validos)})"))
    rotulo = perfil.id + (" (ajustado)" if any(trocas.get(p) not in (None, perfil.papeis[p]) for p in PAPEIS) else "")
    return {"perfil": rotulo, "sessao": papeis["sessao"],
            "agentes": {agente: papeis[papel] for agente, papel in AGENTES.items()}}


def effort_do_agente(agente: str) -> str:
    arquivo = PASTA_AGENTES / f"{_nome_agente(agente)}.md"
    if not arquivo.is_file():
        return ""
    cabecalho = arquivo.read_text(encoding="utf-8").split("---", 2)
    achado = re.search(r"^effort:\s*(\S+)", cabecalho[1] if len(cabecalho) > 2 else "", re.MULTILINE)
    return achado.group(1) if achado else ""


# ---------------------------------------------------------------- comandos

def texto_perfis() -> str:
    linhas = []
    for perfil in PERFIS:
        marca = tr(" (Recomendado)", " (Recommended)") if perfil.id == RECOMENDADO else ""
        linhas.append(f"{perfil.id} — {perfil.rotulo}{marca}: {perfil.quando}")
        linhas += [_linha(descricao, _rotulo_modelo(perfil.papeis[papel])) for papel, descricao in PAPEIS.items()]
        linhas.append("")
    linhas.append(tr("best = Fable se a conta tem acesso, senão Opus (só para a sessão).",
                     "best = Fable if the account has access, otherwise Opus (session only)."))
    return "\n".join(linhas)


def texto_mostrar(raiz: Path, modelos: dict) -> str:
    nenhum = tr("nenhum (herda a sessão em tudo)", "none (inherits the session on everything)")
    linhas = [tr(f"Perfil: {_perfil_visivel(modelos['perfil']) or nenhum}", f"Profile: {_perfil_visivel(modelos['perfil']) or nenhum}"),
              _linha(tr("Sessão de cada etapa", "Each stage's session"), _rotulo_modelo(modelos["sessao"]))]
    for agente in AGENTES:
        effort = effort_do_agente(agente)
        valor = _rotulo_modelo(modelos["agentes"].get(agente, "")) + (f" · effort {effort}" if effort else "")
        linhas.append(_linha(_nome_agente(agente), valor))
    model = _ler_settings(raiz).get("model", "")
    if model and model != modelos["sessao"]:
        linhas.append(tr(f"⚠ {SETTINGS.as_posix()} diz `model: {model}`: é nele que a sessão abre.",
                         f"⚠ {SETTINGS.as_posix()} says `model: {model}`: that is where the session opens."))
    return "\n".join(linhas)


def _garantir_gitignore(raiz: Path) -> bool:
    caminho = raiz / ".gitignore"
    atual = caminho.read_text(encoding="utf-8") if caminho.is_file() else ""
    if LINHA_GITIGNORE in atual.splitlines():
        return False
    with open(caminho, "a", encoding="utf-8", newline="\n") as f:
        f.write(("" if not atual or atual.endswith("\n") else "\n") + LINHA_GITIGNORE + "\n")
    return True


def _ler_settings(raiz: Path) -> dict:
    caminho = raiz / SETTINGS
    return _ler_json(caminho, "settings.local.json") if caminho.is_file() else {}


def _aplicar_sessao(raiz: Path, settings: dict, novo: str, anterior: str) -> str:
    caminho = raiz / SETTINGS
    if novo:
        atual = settings.get("model")
        if atual == novo:
            return tr(f"{SETTINGS.as_posix()} já abre a sessão em `{novo}`",
                      f"{SETTINGS.as_posix()} already opens the session on `{novo}`")
        _gravar_json(caminho, {**settings, "model": novo})
        trocou = (tr(f" (era `{atual}`, posto fora do kit)", f" (was `{atual}`, set outside the kit)")
                  if atual and atual != anterior else "")
        return tr(f"{SETTINGS.as_posix()}: sessão abre em `{novo}`{trocou}",
                  f"{SETTINGS.as_posix()}: session opens on `{novo}`{trocou}")
    if "model" in settings and settings["model"] == anterior:
        _gravar_json(caminho, {k: v for k, v in settings.items() if k != "model"})
        return tr(f"{SETTINGS.as_posix()}: `model` removido (a sessão abre no modelo padrão da conta)",
                  f"{SETTINGS.as_posix()}: `model` removed (the session opens on the account default model)")
    return tr("sessão: nada forçado", "session: nothing forced")


def cmd_aplicar(raiz: Path, args: argparse.Namespace) -> int:
    caminho = raiz / NOME_CONFIG
    config = _ler_json(caminho, NOME_CONFIG)
    anterior = ler_modelos(config)
    trocas = {"sessao": args.sessao, "planejamento": args.planejamento, "execucao": args.execucao,
              "pesquisa": args.pesquisa}
    modelos = montar_modelos(POR_ID[args.perfil], trocas)
    settings = _ler_settings(raiz)  # inválido: para aqui, antes de gravar qualquer coisa
    _gravar_json(caminho, {**config, "modelos": modelos})
    print(tr(f"✓ {NOME_CONFIG}: perfil {_perfil_visivel(modelos['perfil'])}", f"✓ {NOME_CONFIG}: profile {_perfil_visivel(modelos['perfil'])}"))
    print(f"✓ {_aplicar_sessao(raiz, settings, modelos['sessao'], anterior['sessao'])}")
    if _garantir_gitignore(raiz):
        print(f"✓ .gitignore: {LINHA_GITIGNORE}")
    print()
    print(texto_mostrar(raiz, modelos))
    return 0


def cmd_mostrar(raiz: Path, _: argparse.Namespace) -> int:
    print(texto_mostrar(raiz, ler_modelos(_ler_json(raiz / NOME_CONFIG, NOME_CONFIG))))
    return 0


def cmd_de(raiz: Path | None, args: argparse.Namespace) -> int:
    agente = AGENTE_PARA_PT.get(args.agente.removeprefix("pp-en:").removeprefix("pp:"))
    if agente is None:
        conhecidos = ", ".join(_nome_agente(a) for a in AGENTES)
        raise ErroUso(tr(f"agente desconhecido: {args.agente} (conhecidos: {conhecidos})",
                         f"unknown agent: {args.agente} (known: {conhecidos})"))
    modelos = ler_modelos(_ler_json(raiz / NOME_CONFIG, NOME_CONFIG)) if raiz else {"agentes": {}}
    print(modelos["agentes"].get(agente, ""))
    return 0


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=tr("Modelos do projeto: sessão (quem pensa) e agentes (quem executa).",
                                                "Project models: session (who thinks) and agents (who executes)."),
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=tr("Exit: 0 ok, 2 uso incorreto.", "Exit: 0 ok, 2 incorrect usage."))
    ap.add_argument("--raiz", type=Path,
                    help=tr(f"pasta do projeto (default: procura {NOME_CONFIG} para cima)",
                            f"project folder (default: searches upward for {NOME_CONFIG})"))
    sub = ap.add_subparsers(dest="comando", required=True)
    sub.add_parser("perfis", help=tr("os perfis e o modelo de cada papel", "the profiles and the model of each role"))
    p = sub.add_parser("aplicar", help=tr("grava o perfil no config e no settings.local.json",
                                          "writes the profile to the config and to settings.local.json"))
    p.add_argument("perfil", choices=list(POR_ID))
    p.add_argument("--sessao", help=tr(f"troca a sessão ({', '.join(MODELOS_SESSAO)})",
                                       f"switches the session ({', '.join(MODELOS_SESSAO)})"))
    p.add_argument("--planejamento", help=tr(f"troca arquitetura e QA ({', '.join(MODELOS_AGENTE)})",
                                             f"switches architecture and QA ({', '.join(MODELOS_AGENTE)})"))
    p.add_argument("--execucao", help=tr(f"troca quem executa ({', '.join(MODELOS_AGENTE)})",
                                         f"switches who executes ({', '.join(MODELOS_AGENTE)})"))
    p.add_argument("--pesquisa", help=tr(f"troca a pesquisa ({', '.join(MODELOS_AGENTE)})",
                                         f"switches the research ({', '.join(MODELOS_AGENTE)})"))
    sub.add_parser("mostrar", help=tr("o que o projeto usa hoje", "what the project uses today"))
    p = sub.add_parser("de", help=tr("o modelo de um agente (vazio = herda a sessão)",
                                     "the model of an agent (empty = inherits the session)"))
    p.add_argument("agente")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    try:
        if args.comando == "perfis":
            print(texto_perfis())
            return 0
        config = (args.raiz.resolve() / NOME_CONFIG) if args.raiz else achar_config(Path.cwd().resolve())
        if args.comando == "de":
            if args.raiz and not config.is_file():
                raise ErroUso(tr(f"--raiz {args.raiz}: sem {NOME_CONFIG} nessa pasta",
                                 f"--raiz {args.raiz}: no {NOME_CONFIG} in that folder"))
            return cmd_de(config.parent if config and config.is_file() else None, args)
        if config is None or not config.is_file():
            raise ErroUso(tr(f"nenhum {NOME_CONFIG} aqui nem nas pastas acima: rode da raiz do projeto",
                             f"no {NOME_CONFIG} here or in the folders above: run from the project root"))
        return {"aplicar": cmd_aplicar, "mostrar": cmd_mostrar}[args.comando](config.parent, args)
    except ErroUso as erro:
        print(tr("ERRO", "ERROR") + f" {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
