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

NOME_CONFIG = "power-platform.config.json"
SETTINGS = Path(".claude") / "settings.local.json"
LINHA_GITIGNORE = ".claude/settings.local.json"
PASTA_AGENTES = Path(__file__).resolve().parents[3] / "agents"

MODELOS_SESSAO = ("best", "fable", "opus", "sonnet", "haiku")  # best: Fable se a conta tem, senão Opus
MODELOS_AGENTE = ("fable", "opus", "sonnet", "haiku")

PAPEIS = {
    "sessao": "Sessão de cada etapa: conversa, decide, julga",
    "planejamento": "Arquitetura e QA: planejam e julgam",
    "execucao": "Mockups, protótipo, telas e fluxos",
    "pesquisa": "Pesquisa: lê o projeto e a documentação",
}
AGENTES = {
    "agente-arquitetura": "planejamento",
    "agente-qa": "planejamento",
    "agente-mockups": "execucao",
    "agente-prototipo": "execucao",
    "agente-canvas": "execucao",
    "agente-automate": "execucao",
    "agente-pesquisa": "pesquisa",
}


@dataclass(frozen=True)
class Perfil:
    id: str
    rotulo: str
    quando: str
    papeis: dict[str, str]


PERFIS = (
    Perfil("equilibrado", "Equilibrado", "o modelo forte pensa e julga; o rápido executa",
           {"sessao": "opus", "planejamento": "opus", "execucao": "sonnet", "pesquisa": "sonnet"}),
    Perfil("maximo", "Máximo", "o mais forte em tudo o que decide; custa mais",
           {"sessao": "best", "planejamento": "opus", "execucao": "opus", "pesquisa": "sonnet"}),
    Perfil("economico", "Econômico", "Sonnet em tudo, Haiku na pesquisa; espere mais revisões",
           {"sessao": "sonnet", "planejamento": "sonnet", "execucao": "sonnet", "pesquisa": "haiku"}),
    Perfil("herdar", "Herdar", "não força nada: tudo no modelo em que a sessão abrir",
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
    return modelo or "herda a sessão"


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
        raise ErroUso(f"{nome} inválido ({caminho}): {erro}") from erro
    if not isinstance(dados, dict):
        raise ErroUso(f"{nome} inválido ({caminho}): a raiz precisa ser um objeto")
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
        raise ErroUso("config inválida: `modelos` precisa ser um objeto")
    sessao = bloco.get("sessao", "")
    if sessao not in ("", *MODELOS_SESSAO):
        raise ErroUso(f"config inválida: `modelos.sessao` = {sessao!r} (use {', '.join(MODELOS_SESSAO)} ou vazio)")
    agentes = bloco.get("agentes", {})
    if not isinstance(agentes, dict):
        raise ErroUso("config inválida: `modelos.agentes` precisa ser um objeto")
    for agente, modelo in agentes.items():
        if modelo not in ("", *MODELOS_AGENTE):
            raise ErroUso(f"config inválida: `modelos.agentes.{agente}` = {modelo!r} "
                          f"(use {', '.join(MODELOS_AGENTE)} ou vazio)")
    return {"perfil": bloco.get("perfil", ""), "sessao": sessao, "agentes": agentes}


def montar_modelos(perfil: Perfil, trocas: dict[str, str]) -> dict:
    papeis = {**perfil.papeis, **{p: m for p, m in trocas.items() if m is not None}}
    for papel, modelo in papeis.items():
        validos = MODELOS_SESSAO if papel == "sessao" else MODELOS_AGENTE
        if modelo not in ("", *validos):
            raise ErroUso(f"modelo inválido para {papel}: {modelo!r} (use {', '.join(validos)})")
    rotulo = perfil.id + (" (ajustado)" if any(trocas.get(p) not in (None, perfil.papeis[p]) for p in PAPEIS) else "")
    return {"perfil": rotulo, "sessao": papeis["sessao"],
            "agentes": {agente: papeis[papel] for agente, papel in AGENTES.items()}}


def effort_do_agente(agente: str) -> str:
    arquivo = PASTA_AGENTES / f"{agente}.md"
    if not arquivo.is_file():
        return ""
    cabecalho = arquivo.read_text(encoding="utf-8").split("---", 2)
    achado = re.search(r"^effort:\s*(\S+)", cabecalho[1] if len(cabecalho) > 2 else "", re.MULTILINE)
    return achado.group(1) if achado else ""


# ---------------------------------------------------------------- comandos

def texto_perfis() -> str:
    linhas = []
    for perfil in PERFIS:
        marca = " (Recomendado)" if perfil.id == RECOMENDADO else ""
        linhas.append(f"{perfil.id} — {perfil.rotulo}{marca}: {perfil.quando}")
        linhas += [_linha(descricao, _rotulo_modelo(perfil.papeis[papel])) for papel, descricao in PAPEIS.items()]
        linhas.append("")
    linhas.append("best = Fable se a conta tem acesso, senão Opus (só para a sessão).")
    return "\n".join(linhas)


def texto_mostrar(raiz: Path, modelos: dict) -> str:
    linhas = [f"Perfil: {modelos['perfil'] or 'nenhum (herda a sessão em tudo)'}",
              _linha("Sessão de cada etapa", _rotulo_modelo(modelos["sessao"]))]
    for agente in AGENTES:
        effort = effort_do_agente(agente)
        valor = _rotulo_modelo(modelos["agentes"].get(agente, "")) + (f" · effort {effort}" if effort else "")
        linhas.append(_linha(agente, valor))
    settings = raiz / SETTINGS
    if settings.is_file():
        model = _ler_json(settings, "settings.local.json").get("model", "")
        if model and model != modelos["sessao"]:
            linhas.append(f"⚠ {SETTINGS.as_posix()} diz `model: {model}`: é nele que a sessão abre.")
    return "\n".join(linhas)


def _garantir_gitignore(raiz: Path) -> bool:
    caminho = raiz / ".gitignore"
    atual = caminho.read_text(encoding="utf-8") if caminho.is_file() else ""
    if LINHA_GITIGNORE in atual.splitlines():
        return False
    with open(caminho, "a", encoding="utf-8", newline="\n") as f:
        f.write(("" if not atual or atual.endswith("\n") else "\n") + LINHA_GITIGNORE + "\n")
    return True


def _aplicar_sessao(raiz: Path, novo: str, anterior: str) -> str:
    caminho = raiz / SETTINGS
    settings = _ler_json(caminho, "settings.local.json") if caminho.is_file() else {}
    if novo:
        if settings.get("model") == novo:
            return f"{SETTINGS.as_posix()} já abre a sessão em `{novo}`"
        _gravar_json(caminho, {**settings, "model": novo})
        return f"{SETTINGS.as_posix()}: sessão abre em `{novo}`"
    if "model" in settings and settings["model"] == anterior:
        _gravar_json(caminho, {k: v for k, v in settings.items() if k != "model"})
        return f"{SETTINGS.as_posix()}: `model` removido (a sessão abre no modelo padrão da conta)"
    return "sessão: nada forçado"


def cmd_aplicar(raiz: Path, args: argparse.Namespace) -> int:
    caminho = raiz / NOME_CONFIG
    config = _ler_json(caminho, NOME_CONFIG)
    anterior = ler_modelos(config)
    trocas = {"sessao": args.sessao, "planejamento": args.planejamento, "execucao": args.execucao,
              "pesquisa": args.pesquisa}
    modelos = montar_modelos(POR_ID[args.perfil], trocas)
    _gravar_json(caminho, {**config, "modelos": modelos})
    print(f"✓ {NOME_CONFIG}: perfil {modelos['perfil']}")
    print(f"✓ {_aplicar_sessao(raiz, modelos['sessao'], anterior['sessao'])}")
    if _garantir_gitignore(raiz):
        print(f"✓ .gitignore: {LINHA_GITIGNORE}")
    print()
    print(texto_mostrar(raiz, modelos))
    return 0


def cmd_mostrar(raiz: Path, _: argparse.Namespace) -> int:
    print(texto_mostrar(raiz, ler_modelos(_ler_json(raiz / NOME_CONFIG, NOME_CONFIG))))
    return 0


def cmd_de(raiz: Path | None, args: argparse.Namespace) -> int:
    agente = args.agente.removeprefix("pp:")
    if agente not in AGENTES:
        raise ErroUso(f"agente desconhecido: {args.agente} (conhecidos: {', '.join(AGENTES)})")
    modelos = ler_modelos(_ler_json(raiz / NOME_CONFIG, NOME_CONFIG)) if raiz else {"agentes": {}}
    print(modelos["agentes"].get(agente, ""))
    return 0


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Modelos do projeto: sessão (quem pensa) e agentes (quem executa).",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="Exit: 0 ok, 2 uso incorreto.")
    ap.add_argument("--raiz", type=Path, help=f"pasta do projeto (default: procura {NOME_CONFIG} para cima)")
    sub = ap.add_subparsers(dest="comando", required=True)
    sub.add_parser("perfis", help="os perfis e o modelo de cada papel")
    p = sub.add_parser("aplicar", help="grava o perfil no config e no settings.local.json")
    p.add_argument("perfil", choices=list(POR_ID))
    p.add_argument("--sessao", help=f"troca a sessão ({', '.join(MODELOS_SESSAO)})")
    p.add_argument("--planejamento", help=f"troca arquitetura e QA ({', '.join(MODELOS_AGENTE)})")
    p.add_argument("--execucao", help=f"troca quem executa ({', '.join(MODELOS_AGENTE)})")
    p.add_argument("--pesquisa", help=f"troca a pesquisa ({', '.join(MODELOS_AGENTE)})")
    sub.add_parser("mostrar", help="o que o projeto usa hoje")
    p = sub.add_parser("de", help="o modelo de um agente (vazio = herda a sessão)")
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
            return cmd_de(config.parent if config and config.is_file() else None, args)
        if config is None or not config.is_file():
            raise ErroUso(f"nenhum {NOME_CONFIG} aqui nem nas pastas acima: rode da raiz do projeto")
        return {"aplicar": cmd_aplicar, "mostrar": cmd_mostrar}[args.comando](config.parent, args)
    except ErroUso as erro:
        print(f"ERRO {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
