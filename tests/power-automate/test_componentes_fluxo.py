"""Catálogo de componentes: todo .json passa no verificador com 0 erro, o bloco do .md é o mesmo JSON e o índice lista tudo."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-automate" / "scripts" / "verificar-fluxo.py"
PASTA = RAIZ / "skills" / "power-automate" / "assets" / "componentes"
JSONS = sorted(PASTA.glob("*.json"))
DESCRITIVOS = {"trigger-power-apps-v2", "trigger-http-recebimento"}
SECOES = ("Propósito", "Quando usar / quando não usar", "Onde colar", "Entradas e saídas", "JSON",
          "Parâmetros a trocar", "runAfter", "Armadilhas", "Variações")
RE_BLOCO_JSON = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
RE_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


def _verificar(caminho: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(caminho)], capture_output=True, text=True,
                          encoding="utf-8", cwd=RAIZ, check=False)


def test_pasta_tem_componentes():
    assert len(JSONS) >= 30, "catálogo incompleto"


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_componente_passa_no_verificador(caminho):
    r = _verificar(caminho)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 erro(s)" in r.stdout.strip().splitlines()[-1]


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_componente_tem_envelope_de_escopo(caminho):
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert set(dados) == {"nodeId", "serializedValue", "allConnectionData", "staticResults", "isScopeNode", "mslaNode"}
    assert dados["isScopeNode"] is True and dados["mslaNode"] is True
    assert dados["serializedValue"]["type"] in {"Scope", "If", "Switch", "Foreach"}


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_md_tem_o_mesmo_json_e_as_secoes(caminho):
    md = caminho.with_suffix(".md")
    assert md.is_file(), f"falta {md.name}"
    texto = md.read_text(encoding="utf-8")
    blocos = RE_BLOCO_JSON.findall(texto)
    assert blocos, "sem bloco ```json no .md"
    assert json.loads(blocos[0]) == json.loads(caminho.read_text(encoding="utf-8"))
    for secao in SECOES:
        assert f"## {secao}" in texto, f"falta a seção {secao}"
    assert "..." not in blocos[0], "bloco colável não pode ter reticências"


@pytest.mark.parametrize("caminho", JSONS, ids=lambda p: p.stem)
def test_guids_ficticios(caminho):
    for guid in RE_GUID.findall(caminho.read_text(encoding="utf-8")):
        assert guid.startswith("00000000-0000-0000-"), guid


def test_guids_unicos_entre_componentes():
    vistos: dict[str, str] = {}
    for caminho in JSONS:
        for guid in set(RE_GUID.findall(caminho.read_text(encoding="utf-8"))):
            assert guid not in vistos, f"{guid} em {caminho.name} e {vistos[guid]}"
            vistos[guid] = caminho.name


def test_indice_lista_todos_os_componentes():
    indice = (PASTA / "INDICE.md").read_text(encoding="utf-8")
    esperados = {p.stem for p in JSONS} | DESCRITIVOS
    for nome in sorted(esperados):
        assert f"[{nome}](./{nome}.md)" in indice, f"{nome} fora do índice"
    for nome in DESCRITIVOS:
        assert (PASTA / f"{nome}.md").is_file()
    for secao in ("Frequência", "Maturidade", "Ordem de montagem"):
        assert secao in indice


def test_pasta_inteira_passa_no_verificador():
    r = _verificar(PASTA)
    assert r.returncode == 0, r.stdout + r.stderr
