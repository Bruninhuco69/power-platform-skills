"""Testes de `skills/power-platform/scripts/modelos.py` (quem pensa e quem executa no projeto)."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "modelos.py"


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar("modelos", SCRIPT)
estado = _carregar("estado_para_modelos", SCRIPT.with_name("estado.py"))


@pytest.fixture
def projeto(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "power-platform.config.json").write_text(
        json.dumps({"projeto": "Pedidos", "git_commit_por_etapa": True}), encoding="utf-8")
    (tmp_path / ".gitignore").write_text("dist/\n.env", encoding="utf-8")
    return tmp_path


def _config(pasta: Path) -> dict:
    return json.loads((pasta / "power-platform.config.json").read_text(encoding="utf-8"))


def _settings(pasta: Path) -> dict:
    return json.loads((pasta / ".claude" / "settings.local.json").read_text(encoding="utf-8"))


def test_todo_agente_do_plugin_tem_papel_e_todo_papel_existe():
    arquivos = {p.stem for p in (RAIZ / "agents").glob("*.md")}
    assert set(mod.AGENTES) == arquivos
    assert set(mod.AGENTES.values()) <= set(mod.PAPEIS)
    for perfil in mod.PERFIS:
        assert set(perfil.papeis) == set(mod.PAPEIS)


def test_perfis_lista_os_quatro_com_o_recomendado(capsys):
    assert mod.main(["perfis"]) == 0
    saida = capsys.readouterr().out
    for perfil in ("equilibrado", "maximo", "economico", "herdar"):
        assert f"{perfil} — " in saida
    assert "Equilibrado (Recomendado)" in saida
    assert "best = Fable" in saida


def test_aplicar_equilibrado_grava_config_settings_e_gitignore(projeto, capsys):
    assert mod.main(["aplicar", "equilibrado"]) == 0
    modelos = _config(projeto)["modelos"]
    assert modelos["perfil"] == "equilibrado" and modelos["sessao"] == "opus"
    assert modelos["agentes"]["agente-canvas"] == "sonnet"
    assert modelos["agentes"]["agente-qa"] == "opus"
    assert _config(projeto)["git_commit_por_etapa"] is True
    assert _settings(projeto) == {"model": "opus"}
    assert (projeto / ".gitignore").read_text(encoding="utf-8") == "dist/\n.env\n.claude/settings.local.json\n"
    assert mod.main(["aplicar", "equilibrado"]) == 0
    assert (projeto / ".gitignore").read_text(encoding="utf-8").count("settings.local.json") == 1


def test_aplicar_preserva_o_settings_existente_e_herdar_tira_so_o_model_do_kit(projeto):
    (projeto / ".claude").mkdir()
    (projeto / ".claude" / "settings.local.json").write_text('{"permissions": {"allow": []}}', encoding="utf-8")
    assert mod.main(["aplicar", "maximo"]) == 0
    assert _settings(projeto) == {"permissions": {"allow": []}, "model": "best"}
    assert mod.main(["aplicar", "herdar"]) == 0
    assert _settings(projeto) == {"permissions": {"allow": []}}
    assert _config(projeto)["modelos"]["agentes"]["agente-canvas"] == ""


def test_herdar_nao_apaga_model_que_o_usuario_pos_a_mao(projeto):
    (projeto / ".claude").mkdir()
    (projeto / ".claude" / "settings.local.json").write_text('{"model": "sonnet"}', encoding="utf-8")
    assert mod.main(["aplicar", "herdar"]) == 0
    assert _settings(projeto) == {"model": "sonnet"}


def test_troca_avulsa_por_cima_do_perfil(projeto):
    assert mod.main(["aplicar", "equilibrado", "--execucao", "opus"]) == 0
    modelos = _config(projeto)["modelos"]
    assert modelos["perfil"] == "equilibrado (ajustado)"
    assert modelos["agentes"]["agente-canvas"] == "opus"


@pytest.mark.parametrize("args", [["aplicar", "equilibrado", "--execucao", "best"],
                                  ["aplicar", "equilibrado", "--sessao", "gpt"]])
def test_modelo_invalido_da_exit_2(projeto, args):
    assert mod.main(args) == 2


def test_de_devolve_o_modelo_ou_vazio(projeto, capsys):
    assert mod.main(["de", "agente-canvas"]) == 0
    assert capsys.readouterr().out == "\n"
    mod.main(["aplicar", "equilibrado"])
    capsys.readouterr()
    assert mod.main(["de", "pp:agente-canvas"]) == 0
    assert capsys.readouterr().out == "sonnet\n"
    assert mod.main(["de", "agente-inventado"]) == 2


def test_de_sem_config_herda(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert mod.main(["de", "agente-qa"]) == 0
    assert capsys.readouterr().out == "\n"


def test_config_com_modelo_invalido_da_exit_2(projeto):
    (projeto / "power-platform.config.json").write_text(
        json.dumps({"modelos": {"sessao": "opus", "agentes": {"agente-canvas": "gpt-5"}}}), encoding="utf-8")
    assert mod.main(["de", "agente-canvas"]) == 2
    assert mod.main(["mostrar"]) == 2


def test_mostrar_avisa_quando_o_settings_diverge(projeto, capsys):
    mod.main(["aplicar", "equilibrado"])
    (projeto / ".claude" / "settings.local.json").write_text('{"model": "haiku"}', encoding="utf-8")
    capsys.readouterr()
    assert mod.main(["mostrar"]) == 0
    saida = capsys.readouterr().out
    assert "agente-qa" in saida and "effort high" in saida
    assert "model: haiku" in saida


def test_sem_config_aplicar_da_exit_2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert mod.main(["aplicar", "equilibrado"]) == 2


def test_proximo_passo_mostra_o_modelo_da_sessao(projeto, capsys):
    mod.main(["aplicar", "equilibrado"])
    assert estado.main(["iniciar", "--projeto", "Pedidos"]) == 0
    saida = capsys.readouterr().out
    assert "Modelo desta sessão: **opus**" in saida and "/model opus" in saida
    mod.main(["aplicar", "herdar"])
    capsys.readouterr()
    estado.main(["proximo"])
    assert "Modelo desta sessão" not in capsys.readouterr().out


def test_help_pela_linha_de_comando():
    ok = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, encoding="utf-8")
    assert ok.returncode == 0 and "aplicar" in ok.stdout


def test_settings_invalido_nao_deixa_o_config_pela_metade(projeto):
    (projeto / ".claude").mkdir()
    (projeto / ".claude" / "settings.local.json").write_text('{"model": "opus", // comentário\n}', encoding="utf-8")
    assert mod.main(["aplicar", "maximo"]) == 2
    assert "modelos" not in _config(projeto)


def test_avisa_quando_troca_model_posto_fora_do_kit(projeto, capsys):
    (projeto / ".claude").mkdir()
    (projeto / ".claude" / "settings.local.json").write_text('{"model": "haiku"}', encoding="utf-8")
    assert mod.main(["aplicar", "equilibrado"]) == 0
    assert "era `haiku`, posto fora do kit" in capsys.readouterr().out


def test_de_com_raiz_sem_config_da_exit_2(tmp_path):
    assert mod.main(["--raiz", str(tmp_path), "de", "agente-qa"]) == 2
