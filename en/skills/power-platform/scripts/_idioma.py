"""Idioma das mensagens dos scripts do kit: pt-BR (plugin `pp`) ou en-US (plugin `pp-en`).

O código é um só: `tools/sincronizar_en.py` copia cada script, idêntico, para a pasta en-US de cada
skill. O idioma sai da variável PP_LANG (`pt` ou `en`) ou, sem ela, do `.claude-plugin/plugin.json`
mais próximo acima do script: `pp-en` → en-US; qualquer outro, ou nenhum, → pt-BR.

Uso, no topo de cada script (a pasta do script entra no sys.path para o import funcionar também
quando o teste carrega o script pelo caminho):

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _idioma import tradutor  # noqa: E402
    tr = tradutor(__file__)
    print(tr("0 erro(s)", "0 error(s)"))
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

VARIAVEL = "PP_LANG"
PLUGIN_EN = "pp-en"


def idioma_de(script: str | Path) -> str:
    """`en` ou `pt` para o script no caminho dado."""
    escolhido = os.environ.get(VARIAVEL, "").strip().lower()
    if escolhido.startswith("en"):
        return "en"
    if escolhido.startswith("pt"):
        return "pt"
    for pasta in Path(script).resolve().parents:
        manifesto = pasta / ".claude-plugin" / "plugin.json"
        if manifesto.is_file():
            try:
                nome = json.loads(manifesto.read_text(encoding="utf-8-sig")).get("name")
            except (OSError, ValueError, AttributeError):
                return "pt"
            return "en" if nome == PLUGIN_EN else "pt"
    return "pt"


def tradutor(script: str | Path) -> Callable[[str, str], str]:
    """`tr("texto pt-BR", "English text")` devolve o texto no idioma do script."""
    em_ingles = idioma_de(script) == "en"

    def tr(pt: str, en: str) -> str:
        return en if em_ingles else pt

    return tr
