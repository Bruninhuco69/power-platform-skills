"""Testes de `skills/power-platform/scripts/capturar-telas.py` (fotos para a verificação visual)."""
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "capturar-telas.py"
MOLDE = RAIZ / "skills" / "power-platform" / "assets" / "prototipo-molde.html"


def _carregar():
    spec = importlib.util.spec_from_file_location("capturar_telas", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["capturar_telas"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


@pytest.fixture
def prototipo(tmp_path):
    destino = tmp_path / "proto dir" / "index.html"
    destino.parent.mkdir()
    shutil.copy(MOLDE, destino)
    return destino


def test_le_as_telas_do_molde_na_ordem():
    assert mod.telas_do_html(MOLDE.read_text(encoding="utf-8")) == ["tela-inicio", "tela-pedidos", "tela-sem-acesso"]


def test_padroes_de_navegacao_batem_com_o_molde():
    texto = MOLDE.read_text(encoding="utf-8")
    for nav in mod.PADROES_NAV:
        assert f"id: '{nav}'" in texto
    assert "new URLSearchParams(location.search)" in texto


def test_url_leva_perfil_navegacao_e_tela(prototipo):
    url = mod.montar_url(prototipo, "gestor", "topo", "tela-pedidos")
    assert url.startswith("file:///") and "proto%20dir/index.html" in url
    assert url.endswith("?perfil=gestor&nav=topo#/tela-pedidos")
    assert mod.montar_url(prototipo).endswith("index.html")


def test_comando_usa_perfil_temporario_e_janela_sem_cabeca(prototipo, tmp_path):
    captura = mod.Captura("tela-inicio", mod.montar_url(prototipo, tela="tela-inicio"), tmp_path / "x.png")
    cmd = mod.comando(Path("chrome"), captura, (1920, 1160), tmp_path / "perfil")
    assert "--headless=new" in cmd and "--window-size=1920,1160" in cmd
    assert f"--user-data-dir={tmp_path / 'perfil'}" in cmd
    assert cmd[-1] == captura.url


def test_simular_lista_uma_por_tela_sem_abrir_navegador(prototipo, capsys, monkeypatch):
    monkeypatch.setattr(mod, "achar_navegador", lambda: pytest.fail("não deveria procurar navegador"))
    assert mod.main([str(prototipo), "--simular"]) == 0
    saida = capsys.readouterr().out
    assert saida.count("○ tela-") == 3 and "3 captura(s) planejada(s), 1920x1160" in saida


def test_navegacoes_fotografa_a_primeira_tela_nos_cinco_padroes(prototipo, capsys):
    assert mod.main([str(prototipo), "--navegacoes", "--simular"]) == 0
    saida = capsys.readouterr().out
    for nav in mod.PADROES_NAV:
        assert f"tela-inicio--{nav}.png" in saida


def test_pagina_sem_telas_vira_uma_captura(tmp_path, capsys):
    pagina = tmp_path / "identidade.html"
    pagina.write_text("<!doctype html><title>x</title><p>amostra</p>", encoding="utf-8")
    assert mod.main([str(pagina), "--simular"]) == 0
    saida = capsys.readouterr().out
    assert "identidade.png" in saida and "1440x2000" in saida


@pytest.mark.parametrize("args", [["--telas", "tela-inexistente"], ["--perfil", "x&y=1"]])
def test_uso_incorreto_da_exit_2(prototipo, args):
    assert mod.main([str(prototipo), "--simular", *args]) == 2


def test_arquivo_ausente_da_exit_2(tmp_path):
    assert mod.main([str(tmp_path / "nada.html")]) == 2


def test_sem_navegador_da_exit_2_e_diz_nao_verificado(prototipo, capsys, monkeypatch):
    monkeypatch.setattr(mod, "achar_navegador", lambda: None)
    assert mod.main([str(prototipo)]) == 2
    assert "não verificado" in capsys.readouterr().err


def test_pp_navegador_inexistente_nao_e_aceito(monkeypatch, tmp_path):
    monkeypatch.setenv("PP_NAVEGADOR", str(tmp_path / "nao-existe.exe"))
    assert mod.achar_navegador() is None


@pytest.mark.skipif(mod.achar_navegador() is None, reason="sem Chrome/Edge/Chromium nesta máquina")
def test_captura_de_verdade_grava_png(prototipo, tmp_path, capsys):
    saida = tmp_path / "fotos"
    assert mod.main([str(prototipo), "--telas", "tela-pedidos", "--nav", "gaveta", "--saida", str(saida)]) == 0
    png = saida / "tela-pedidos--gaveta.png"
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
