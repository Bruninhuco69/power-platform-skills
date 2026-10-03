"""Skills `sql-procedures` e `dataverse` do plugin en-US: o SQL passa no lint en-US como o pt-BR passa no
pt-BR, cada arquivo tem o mesmo SQL do pt-BR (muda só comentário e texto), a fórmula do Dataverse está em
en-US e o molde de nomes as-built traz o cabeçalho que o script gera."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sql import blocos_sql, codigo  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
MAPA = json.loads((RAIZ / "i18n" / "mapa.json").read_text(encoding="utf-8"))["arquivos"]
SQL_PT = RAIZ / "skills" / "sql-procedures"
SQL_EN = RAIZ / "en" / "skills" / "sql-procedures"
DV_EN = RAIZ / "en" / "skills" / "dataverse"
PARES = sorted((RAIZ / pt, RAIZ / e["en"]) for pt, e in MAPA.items()
               if pt.startswith(("skills/sql-procedures/", "skills/dataverse/")) and pt.endswith((".md", ".sql")))
EXTRAIR = {"pt": RAIZ / "skills" / "dataverse" / "scripts" / "extrair-nomes-as-built.py",
           "en": DV_EN / "scripts" / "extrair-nomes-as-built.py"}
MOLDE_AS_BUILT = {"pt": RAIZ / "skills" / "dataverse" / "assets" / "nomes-as-built-molde.md",
                  "en": DV_EN / "assets" / "as-built-names-template.md"}
FIXTURE = RAIZ / "tests" / "dataverse" / "fixtures" / "entitydefinitions-ok.json"
CONTAGEM = re.compile(r"(\d+) \S+\(s\), (\d+) \S+\(s\)")
ARGUMENTO_PT = re.compile(r"\w\([^()]*;")  # `Filter(T; …`: no en-US o `;` só encadeia
BLOCO_FORMULA = re.compile(r"^```(?:powerfx)?\n(.*?)^```", re.M | re.S)


def _rodar(script: Path, *args) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PP_LANG"}
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8", cwd=RAIZ, env=env, check=False)


def _blocos_de_formula(texto: str) -> list[str]:
    """Blocos ``` sem linguagem ou ```powerfx: onde o kit põe a fórmula da barra de fórmulas."""
    blocos, aberto, formula, atual = [], False, False, []
    for linha in texto.splitlines():
        if not linha.startswith("```"):
            atual.append(linha)
        elif not aberto:
            aberto, formula, atual = True, linha[3:].strip() in ("", "powerfx"), []
        else:
            if formula:
                blocos.append("\n".join(atual))
            aberto = False
    return blocos


def _lint(raiz: Path) -> subprocess.CompletedProcess:
    return _rodar(raiz / "scripts" / "lint-procedure.py", raiz / "SKILL.md", raiz / "references", raiz / "assets")


@pytest.mark.parametrize("molde", ["write-procedure-template.sql", "read-function-template.sql"])
def test_molde_sql_en_passa_limpo(molde):
    r = _rodar(SQL_EN / "scripts" / "lint-procedure.py", SQL_EN / "assets" / molde)
    assert r.returncode == 0 and r.stdout.strip().splitlines()[-1] == "0 error(s), 0 warning(s)", r.stdout


def test_skill_sql_inteira_passa_no_lint_en_com_os_mesmos_objetos_do_pt():
    pt, en = _lint(SQL_PT), _lint(SQL_EN)
    assert pt.stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)", pt.stdout
    assert en.returncode == 0 and en.stdout.strip().splitlines()[-1] == "0 error(s), 0 warning(s)", en.stdout
    assert CONTAGEM.search(en.stdout).groups() == CONTAGEM.search(pt.stdout).groups()


@pytest.mark.parametrize("pt, en", PARES, ids=lambda p: p.name)
def test_sql_en_e_o_do_pt(pt, en):
    texto_pt, texto_en = pt.read_text(encoding="utf-8"), en.read_text(encoding="utf-8")
    if pt.suffix == ".sql":
        assert codigo(texto_en) == codigo(texto_pt)
        return
    blocos_pt, blocos_en = blocos_sql(texto_pt), blocos_sql(texto_en)
    assert len(blocos_en) == len(blocos_pt)
    for i, (a, b) in enumerate(zip(blocos_pt, blocos_en), start=1):
        assert codigo(b) == codigo(a), f"{en.name}: bloco sql {i}"


@pytest.mark.parametrize("arquivo", sorted(DV_EN.rglob("*.md")), ids=lambda p: p.name)
def test_formula_do_dataverse_em_en_us(arquivo):
    for bloco in _blocos_de_formula(arquivo.read_text(encoding="utf-8")):
        assert ";;" not in bloco and "pt-BR: ;" not in bloco, f"{arquivo.name}: fórmula em sintaxe pt-BR"
        for linha in bloco.splitlines():
            assert not ARGUMENTO_PT.search(linha.split("//")[0]), f"{arquivo.name}: `;` separa argumento: {linha}"


@pytest.mark.parametrize("idioma", ["pt", "en"])
def test_molde_as_built_tem_o_cabecalho_que_o_script_gera(idioma):
    r = _rodar(EXTRAIR[idioma], FIXTURE, "--saida", "-")
    assert r.returncode == 0, r.stderr
    linhas = r.stdout.splitlines()
    cabecalhos = {a for a, b in zip(linhas, linhas[1:]) if b.startswith("|---")}
    assert len(cabecalhos) == 2
    assert cabecalhos <= set(MOLDE_AS_BUILT[idioma].read_text(encoding="utf-8").splitlines())
