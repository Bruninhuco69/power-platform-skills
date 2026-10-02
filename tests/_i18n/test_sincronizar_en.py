"""Scripts pt-BR e en-US: o mesmo código, copiado por `tools/sincronizar_en.py`, e o idioma por plugin."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


sinc = _carregar("sincronizar_en", RAIZ / "tools" / "sincronizar_en.py")
idioma = _carregar("idioma_teste", RAIZ / "skills" / "power-platform" / "scripts" / "_idioma.py")


# ---------------------------------------------------------------- o repositório de verdade

def test_copias_en_sao_identicas_ao_pt_e_o_mapa_marca_feito():
    assert sinc.problemas(RAIZ) == [], "rode `python tools/sincronizar_en.py`"


def test_idioma_py_e_igual_em_todas_as_skills():
    copias = sorted(RAIZ.glob("skills/*/scripts/_idioma.py"))
    assert len(copias) == len(list(RAIZ.glob("skills/*/scripts"))) >= 5
    assert len({c.read_bytes().replace(b"\r\n", b"\n") for c in copias}) == 1


def test_script_do_plugin_pt_e_pt_e_a_copia_en_e_en(monkeypatch):
    monkeypatch.delenv("PP_LANG", raising=False)
    assert idioma.idioma_de(RAIZ / "skills" / "power-platform" / "scripts" / "estado.py") == "pt"
    assert idioma.idioma_de(RAIZ / "en" / "skills" / "power-platform" / "scripts" / "estado.py") == "en"


# ---------------------------------------------------------------- _idioma.py

def _plugin(pasta: Path, nome: str | None, conteudo: str | None = None) -> Path:
    (pasta / ".claude-plugin").mkdir(parents=True)
    texto = conteudo if conteudo is not None else json.dumps({"name": nome})
    (pasta / ".claude-plugin" / "plugin.json").write_text(texto, encoding="utf-8")
    script = pasta / "skills" / "x" / "scripts" / "s.py"
    script.parent.mkdir(parents=True)
    script.write_text("", encoding="utf-8")
    return script


@pytest.mark.parametrize("nome, esperado", [("pp-en", "en"), ("pp", "pt"), ("outro", "pt")])
def test_idioma_pelo_plugin_json_mais_proximo(tmp_path, monkeypatch, nome, esperado):
    monkeypatch.delenv("PP_LANG", raising=False)
    assert idioma.idioma_de(_plugin(tmp_path, nome)) == esperado


@pytest.mark.parametrize("valor, esperado", [("en", "en"), ("en-US", "en"), ("EN", "en"), ("pt", "pt"),
                                             ("pt-BR", "pt")])
def test_pp_lang_vence_o_plugin_json(tmp_path, monkeypatch, valor, esperado):
    script = _plugin(tmp_path, "pp-en" if esperado == "pt" else "pp")
    monkeypatch.setenv("PP_LANG", valor)
    assert idioma.idioma_de(script) == esperado


def test_sem_plugin_json_ou_ilegivel_cai_no_pt(tmp_path, monkeypatch):
    monkeypatch.delenv("PP_LANG", raising=False)
    solto = tmp_path / "solto" / "s.py"
    solto.parent.mkdir()
    solto.write_text("", encoding="utf-8")
    assert idioma.idioma_de(solto) == "pt"
    assert idioma.idioma_de(_plugin(tmp_path / "quebrado", None, conteudo="{")) == "pt"


def test_tradutor_escolhe_o_texto(tmp_path, monkeypatch):
    monkeypatch.delenv("PP_LANG", raising=False)
    tr_en = idioma.tradutor(_plugin(tmp_path / "a", "pp-en"))
    tr_pt = idioma.tradutor(_plugin(tmp_path / "b", "pp"))
    assert tr_en("0 erro(s)", "0 error(s)") == "0 error(s)"
    assert tr_pt("0 erro(s)", "0 error(s)") == "0 erro(s)"


# ---------------------------------------------------------------- sincronizar_en.py

def _repo(tmp_path: Path) -> Path:
    for rel, texto in {"skills/um/SKILL.md": "# um\n", "skills/um/scripts/a.py": "print('a')\n",
                       "skills/um/scripts/_b.py": "B = 1\n"}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(texto, encoding="utf-8")
    (tmp_path / "i18n").mkdir()
    mapa = {"arquivos": {"skills/um/SKILL.md": {"en": "en/skills/one/SKILL.md", "situacao": "pendente"}}}
    (tmp_path / "i18n" / "mapa.json").write_text(json.dumps(mapa), encoding="utf-8")
    return tmp_path


def _mapa(raiz: Path) -> dict:
    return json.loads((raiz / "i18n" / "mapa.json").read_text(encoding="utf-8"))["arquivos"]


def test_sincronizar_copia_identico_e_marca_feito(tmp_path):
    raiz = _repo(tmp_path)
    assert len(sinc.problemas(raiz)) >= 2
    sinc.sincronizar(raiz)
    assert (raiz / "en/skills/one/scripts/a.py").read_bytes() == (raiz / "skills/um/scripts/a.py").read_bytes()
    assert (raiz / "en/skills/one/scripts/_b.py").is_file()
    assert _mapa(raiz)["skills/um/scripts/a.py"] == {"en": "en/skills/one/scripts/a.py", "situacao": "feito"}
    assert sinc.problemas(raiz) == []


def test_conferir_acusa_copia_diferente_e_o_sincronizar_corrige(tmp_path):
    raiz = _repo(tmp_path)
    sinc.sincronizar(raiz)
    (raiz / "skills/um/scripts/a.py").write_text("print('mudou')\n", encoding="utf-8")
    assert any("diferente" in p for p in sinc.problemas(raiz))
    assert sinc.main(["--raiz", str(raiz), "--conferir"]) == 1
    assert sinc.main(["--raiz", str(raiz)]) == 0
    assert sinc.main(["--raiz", str(raiz), "--conferir"]) == 0


def test_so_fim_de_linha_diferente_nao_conta(tmp_path):
    raiz = _repo(tmp_path)
    sinc.sincronizar(raiz)
    (raiz / "en/skills/one/scripts/a.py").write_bytes(b"print('a')\r\n")
    assert sinc.problemas(raiz) == []


def test_orfao_en_e_entrada_sem_fonte_saem(tmp_path):
    raiz = _repo(tmp_path)
    sinc.sincronizar(raiz)
    (raiz / "skills/um/scripts/a.py").unlink()
    problemas = sinc.problemas(raiz)
    assert any("sem script pt-BR" in p for p in problemas) and any("não existe mais" in p for p in problemas)
    sinc.sincronizar(raiz)
    assert not (raiz / "en/skills/one/scripts/a.py").exists()
    assert "skills/um/scripts/a.py" not in _mapa(raiz)


def test_skill_sem_caminho_en_no_mapa_e_erro_de_uso(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "skills/dois/scripts").mkdir(parents=True)
    (raiz / "skills/dois/scripts/c.py").write_text("", encoding="utf-8")
    assert sinc.main(["--raiz", str(raiz)]) == 2
