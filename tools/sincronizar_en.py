#!/usr/bin/env python3
"""Copia os scripts das skills pt-BR, idênticos, para a pasta en-US de cada skill (plugin `pp-en`).

O código é um só e o pt-BR é a fonte: cada `skills/<skill>/scripts/*.py` vai para o caminho en-US do
`i18n/mapa.json` (a pasta da skill en-US sai da entrada do `SKILL.md`), a entrada vira "feito", e
cópia en-US sem fonte pt-BR é apagada. O idioma das mensagens cada script escolhe sozinho
(`_idioma.py`).

Uso:
    python tools/sincronizar_en.py              # copia, atualiza o mapa e apaga órfãos
    python tools/sincronizar_en.py --conferir   # só confere; exit 1 se algo está fora de sincronia

Exit: 0 em sincronia (ou sincronizado), 1 fora de sincronia (--conferir), 2 mapa ausente ou ilegível.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ_PADRAO = Path(__file__).resolve().parent.parent
MAPA = Path("i18n/mapa.json")
PADRAO_SCRIPTS = "skills/*/scripts/*.py"
PADRAO_SCRIPTS_EN = "en/skills/*/scripts/*.py"


class ErroMapa(Exception):
    """Mapa ausente, ilegível ou sem a skill do script (exit 2)."""


@dataclass(frozen=True)
class Par:
    pt: str
    en: str


def _conteudo(caminho: Path) -> bytes:
    """Bytes com fim de linha LF: o Git normaliza, e a cópia não pode acusar diferença só de CRLF."""
    return caminho.read_bytes().replace(b"\r\n", b"\n")


def ler_mapa(raiz: Path) -> dict:
    arquivo = raiz / MAPA
    if not arquivo.is_file():
        raise ErroMapa(f"falta {MAPA.as_posix()}")
    try:
        mapa = json.loads(arquivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ErroMapa(f"{MAPA.as_posix()} não é JSON válido: {erro}") from erro
    if not isinstance(mapa.get("arquivos"), dict):
        raise ErroMapa(f"{MAPA.as_posix()} sem o objeto `arquivos`")
    return mapa


def gravar_mapa(raiz: Path, mapa: dict) -> None:
    mapa["arquivos"] = dict(sorted(mapa["arquivos"].items()))
    (raiz / MAPA).write_text(json.dumps(mapa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
                             newline="\n")


def _destino(mapa: dict, pt: str) -> str:
    """Caminho en-US do script: o do mapa ou, se novo, a pasta en-US da skill + o mesmo nome."""
    entrada = mapa["arquivos"].get(pt)
    if isinstance(entrada, dict) and entrada.get("en"):
        return entrada["en"]
    skill = Path(pt).parts[1]
    skill_md = mapa["arquivos"].get(f"skills/{skill}/SKILL.md")
    if not isinstance(skill_md, dict) or not skill_md.get("en"):
        raise ErroMapa(f"`skills/{skill}/SKILL.md` sem caminho en-US no mapa: não sei onde pôr `{pt}`")
    return (Path(skill_md["en"]).parent / "scripts" / Path(pt).name).as_posix()


def pares(raiz: Path, mapa: dict) -> list[Par]:
    scripts = sorted(p for p in raiz.glob(PADRAO_SCRIPTS) if "__pycache__" not in p.parts)
    return [Par(rel, _destino(mapa, rel)) for rel in (p.relative_to(raiz).as_posix() for p in scripts)]


def _orfaos(raiz: Path, destinos: set[str]) -> list[str]:
    return sorted(rel for rel in (p.relative_to(raiz).as_posix() for p in raiz.glob(PADRAO_SCRIPTS_EN))
                  if rel not in destinos)


def _entradas_sem_fonte(raiz: Path, mapa: dict) -> list[str]:
    return sorted(pt for pt in mapa["arquivos"]
                  if Path(pt).match(PADRAO_SCRIPTS) and not (raiz / pt).is_file())


def problemas(raiz: Path) -> list[str]:
    """O que está fora de sincronia, uma linha por problema (vazio = em sincronia)."""
    mapa = ler_mapa(raiz)
    lista = pares(raiz, mapa)
    saida = []
    for par in lista:
        entrada = mapa["arquivos"].get(par.pt)
        en = raiz / par.en
        if not en.is_file():
            saida.append(f"{par.en}: falta a cópia de {par.pt}")
        elif _conteudo(en) != _conteudo(raiz / par.pt):
            saida.append(f"{par.en}: diferente de {par.pt}")
        if not isinstance(entrada, dict) or entrada.get("situacao") != "feito" or entrada.get("en") != par.en:
            saida.append(f"{MAPA.as_posix()}: `{par.pt}` precisa de \"en\": \"{par.en}\" e \"situacao\": \"feito\"")
    saida += [f"{rel}: cópia en-US sem script pt-BR" for rel in _orfaos(raiz, {p.en for p in lista})]
    saida += [f"{MAPA.as_posix()}: `{pt}` não existe mais" for pt in _entradas_sem_fonte(raiz, mapa)]
    return saida


def sincronizar(raiz: Path) -> list[str]:
    """Copia, atualiza o mapa e apaga órfãos; devolve o que fez."""
    mapa = ler_mapa(raiz)
    lista = pares(raiz, mapa)
    feito = []
    for par in lista:
        origem, destino = raiz / par.pt, raiz / par.en
        if not destino.is_file() or _conteudo(destino) != _conteudo(origem):
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origem, destino)
            feito.append(f"copiado {par.pt} -> {par.en}")
        mapa["arquivos"][par.pt] = {"en": par.en, "situacao": "feito"}
    for rel in _orfaos(raiz, {p.en for p in lista}):
        (raiz / rel).unlink()
        feito.append(f"apagado {rel} (sem script pt-BR)")
    for pt in _entradas_sem_fonte(raiz, mapa):
        del mapa["arquivos"][pt]
        feito.append(f"tirado do mapa {pt}")
    gravar_mapa(raiz, mapa)
    return feito


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Copia os scripts pt-BR, idênticos, para o plugin en-US (pp-en).")
    ap.add_argument("--conferir", action="store_true", help="só confere; exit 1 se algo está fora de sincronia")
    ap.add_argument("--raiz", type=Path, default=RAIZ_PADRAO, help="raiz do repositório")
    args = ap.parse_args(argv)
    raiz = args.raiz.resolve()
    try:
        if args.conferir:
            lista = problemas(raiz)
            for linha in lista:
                print(linha)
            print(f"{len(lista)} problema(s) de sincronia")
            return 1 if lista else 0
        for linha in sincronizar(raiz):
            print(linha)
        print(f"{len(pares(raiz, ler_mapa(raiz)))} script(s) em sincronia")
        return 0
    except ErroMapa as erro:
        print(f"ERRO {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
