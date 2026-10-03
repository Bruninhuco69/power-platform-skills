"""Cada script copiado para o plugin en-US (`en/skills/*/scripts/`) fala inglês sozinho, pelo plugin.json."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
EN = RAIZ / "en" / "skills"
SCRIPTS_EN = sorted(p for p in EN.glob("*/scripts/*.py") if not p.name.startswith("_"))
FIXTURES = RAIZ / "tests"
# palavras e letras que só aparecem em texto pt-BR; o --help en-US não pode ter nenhuma
# chave de config (`mockups.pasta`) e a lista de tipos do spec (`Types: texto, ...`) são código: ficam iguais
CODIGO_NO_HELP = re.compile(r"\b\w+\.\w+\b|^Types: .*$", re.MULTILINE)
PORTUGUES = re.compile(r"[ãõçÃÕÇ]|\b(?:não|arquivo|pasta|etapa|erro\(s\)|aviso\(s\)|usuário|só)\b", re.IGNORECASE)


def _rodar(script: Path, *args: str, cwd: Path | None = None, lang: str | None = None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PP_LANG"}
    if lang:
        env["PP_LANG"] = lang
    env["PYTHONIOENCODING"] = "utf-8"
    env["COLUMNS"] = "200"  # o argparse não quebra `mockups.pasta` em duas linhas
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8",
                          cwd=cwd, env=env, timeout=120)


def _en(skill: str, nome: str) -> Path:
    return EN / skill / "scripts" / nome


def test_ha_copia_en_de_cada_script():
    assert {p.name for p in SCRIPTS_EN} == {p.name for p in RAIZ.glob("skills/*/scripts/*.py")
                                           if not p.name.startswith("_")}


@pytest.mark.parametrize("script", SCRIPTS_EN, ids=lambda p: p.name)
def test_help_em_ingles(script):
    r = _rodar(script, "--help")
    assert r.returncode == 0, r.stderr
    texto = CODIGO_NO_HELP.sub("", r.stdout)
    achados = sorted({m.group(0) for m in PORTUGUES.finditer(texto)})
    assert not achados, f"pt-BR no --help en-US: {achados}"


@pytest.mark.parametrize("skill, script, fixture", [
    ("powerapps-canvas", "validar-telas.py", "powerapps-canvas/fixtures/erro-sem-igual.md"),
    ("power-automate", "verificar-fluxo.py", "power-automate/fixtures/F001-json-invalido.json"),
    ("sql-procedures", "lint-procedure.py", "sql-procedures/fixtures/p001_sem_nocount.sql"),
])
def test_validador_en_resume_em_ingles(skill, script, fixture):
    r = _rodar(_en(skill, script), str(FIXTURES / fixture))
    saida = r.stdout + r.stderr
    assert r.returncode == 1, saida
    assert re.search(r"\d+ error\(s\), \d+ warning\(s\)", saida), saida
    assert "erro(s)" not in saida and "aviso(s)" not in saida


def test_pp_lang_pt_faz_a_copia_en_falar_portugues():
    r = _rodar(_en("powerapps-canvas", "validar-telas.py"), str(FIXTURES / "powerapps-canvas/fixtures/erro-sem-igual.md"),
               lang="pt")
    assert re.search(r"\d+ erro\(s\), \d+ aviso\(s\)", r.stdout + r.stderr)


def test_estado_en_cria_state_md_com_comandos_pp_en(tmp_path):
    script = _en("power-platform", "estado.py")
    r = _rodar(script, "iniciar", "--projeto", "Demo", "--ideia", "track orders", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    estado = (tmp_path / "STATE.md").read_text(encoding="utf-8")
    assert not (tmp_path / "ESTADO.md").exists()
    assert "/pp-en:brainstorm" in estado and "Next step" in estado and "/pp:" not in estado
    assert _rodar(script, "comecar", "brainstorm", cwd=tmp_path).returncode == 0
    assert _rodar(script, "concluir", "brainstorm", "--nota", "ok", cwd=tmp_path).returncode == 0
    painel = _rodar(script, "mostrar", cwd=tmp_path).stdout
    assert "/pp-en:design" in painel and not PORTUGUES.search(painel.replace("track orders", ""))


def test_estado_en_aceita_id_en_da_etapa(tmp_path):
    script = _en("power-platform", "estado.py")
    _rodar(script, "iniciar", "--projeto", "Demo", cwd=tmp_path)
    assert _rodar(script, "comecar", "brainstorm", cwd=tmp_path).returncode == 0
    r = _rodar(script, "checar", "prototype", cwd=tmp_path)
    assert r.returncode == 1 and "/pp-en:brainstorm" in r.stdout


def test_montar_carga_mockup_en_grava_mockup_load(tmp_path):
    molde = RAIZ / "skills" / "power-platform" / "assets" / "carga-mockup-molde.json"
    r = _rodar(_en("power-platform", "montar-carga-mockup.py"), str(molde), "--trilha", "sql-server",
               "--saida", str(tmp_path), cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert {p.name for p in tmp_path.iterdir()} >= {"mockup-load.sql", "mockup-load.xlsx"}
    assert not list(tmp_path.glob("carga-mockup*"))
    assert re.search(r"\d+ error\(s\), \d+ warning\(s\)", r.stdout + r.stderr)


def test_extrair_nomes_as_built_en():
    r = _rodar(_en("dataverse", "extrair-nomes-as-built.py"), str(FIXTURES / "dataverse/fixtures/entitydefinitions-ok.json"),
               "--prefixo", "abc_", "--saida", "-")
    assert r.returncode == 0, r.stderr
    assert r.stdout.startswith("# Dataverse as-built names") and "Nomes as-built" not in r.stdout
    assert "0 error(s), 0 warning(s)" in r.stderr
