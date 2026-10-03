"""Skill `power-automate` do plugin en-US: cada componente passa no verificador en-US, o .md traz o mesmo
JSON, o índice lista tudo, e cada JSON en-US tem o mesmo código do pt-BR (muda só texto)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fluxo import diferencas  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PT = RAIZ / "skills" / "power-automate"
EN = RAIZ / "en" / "skills" / "power-automate"
SCRIPT_EN = EN / "scripts" / "verificar-fluxo.py"
PASTA = EN / "assets" / "components"
MAPA = json.loads((RAIZ / "i18n" / "mapa.json").read_text(encoding="utf-8"))["arquivos"]
PARES_JSON = sorted((RAIZ / pt, RAIZ / e["en"]) for pt, e in MAPA.items()
                    if pt.startswith("skills/power-automate/assets/") and pt.endswith(".json"))
JSONS = sorted(PASTA.glob("*.json"))
DESCRITIVOS = {"trigger-power-apps-v2", "trigger-http-inbound"}
SECOES = ("Purpose", "When to use / when not to use", "Where to paste", "Inputs and outputs", "JSON",
          "Parameters to change", "runAfter", "Pitfalls", "Variations")
RE_BLOCO_JSON = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
RE_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
# literal de uma palavra que é texto visível e ninguém compara: traduzido de propósito, conferido à mão
PALAVRAS_TRADUZIDAS: dict[str, str] = {"Arquivado": "Archived"}  # derive-value-switch: rótulo de status exibido


def _verificar(*args) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PP_LANG"}
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, str(SCRIPT_EN), *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8", cwd=RAIZ, env=env, check=False)


def test_mesmos_componentes_do_pt():
    pt = {Path(MAPA[f"skills/power-automate/assets/componentes/{p.name}"]["en"]).name
          for p in (PT / "assets" / "componentes").glob("*.json")}
    assert {p.name for p in JSONS} == pt


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_componente_passa_no_verificador_en(caminho):
    r = _verificar(caminho)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 error(s)" in r.stdout.strip().splitlines()[-1]


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_md_tem_o_mesmo_json_e_as_secoes(caminho):
    texto = caminho.with_suffix(".md").read_text(encoding="utf-8")
    blocos = RE_BLOCO_JSON.findall(texto)
    assert blocos and json.loads(blocos[0]) == json.loads(caminho.read_text(encoding="utf-8"))
    for secao in SECOES:
        assert f"## {secao}" in texto, f"falta a seção {secao}"
    assert "..." not in blocos[0]


def test_indice_lista_todos_os_componentes():
    indice = (PASTA / "INDEX.md").read_text(encoding="utf-8")
    for nome in sorted({p.stem for p in JSONS} | DESCRITIVOS):
        assert f"[{nome}](./{nome}.md)" in indice, f"{nome} fora do índice"
        assert (PASTA / f"{nome}.md").is_file()
    for palavra in ("Frequency", "Maturity", "Assembly order"):
        assert palavra in indice


def test_pasta_inteira_e_molde_passam_no_verificador_en():
    assert _verificar(PASTA).returncode == 0
    r = _verificar(EN / "assets" / "flow-write-template.json")
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1] == "0 error(s), 0 warning(s)", r.stdout


@pytest.mark.parametrize("pt, en", PARES_JSON, ids=lambda p: p.stem)
def test_json_en_tem_o_codigo_do_pt(pt, en):
    texto_pt, texto_en = pt.read_text(encoding="utf-8"), en.read_text(encoding="utf-8")
    assert diferencas(json.loads(texto_pt), json.loads(texto_en), PALAVRAS_TRADUZIDAS) == []
    assert sorted(RE_GUID.findall(texto_en)) == sorted(RE_GUID.findall(texto_pt))
