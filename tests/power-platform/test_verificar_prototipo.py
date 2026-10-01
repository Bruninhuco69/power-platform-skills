"""Testes do verificar-prototipo.py: o molde passa; cada desvio do contrato vira o código esperado."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "verificar-prototipo.py"
MOLDE = RAIZ / "skills" / "power-platform" / "assets" / "prototipo-molde.html"
MOLDE_MOCKUPS = RAIZ / "skills" / "power-platform" / "assets" / "mockups-molde.json"
CATALOGO = RAIZ / "skills" / "powerapps-canvas" / "assets" / "componentes"

_spec = importlib.util.spec_from_file_location("verificar_prototipo", SCRIPT)
vp = importlib.util.module_from_spec(_spec)
sys.modules["verificar_prototipo"] = vp  # antes de exec_module: o dataclass precisa do módulo registrado
_spec.loader.exec_module(vp)

CABECA = """<!doctype html>
<html lang="pt-BR" data-prototipo="v1">
<head>
<style>
:root { --fxColorPrimary: rgb(15 108 189); --fxColorSurface: #ffffff; }
.botao { background: var(--fxColorPrimary); color: var(--fxColorSurface); }
</style>
</head>
<body>
<div data-prototipo-controles><span data-prototipo-aviso>Protótipo para validação — não é o app</span></div>
<main data-canvas="1920x1080">
"""
PE = """</main>
</body>
</html>
"""
TELA_OK = """<section data-tela="tela-pedidos" data-titulo="Pedidos" data-perfis="administrador,gestor" data-mockups="tl-01-lista,tl-02-novo">
  <div data-componente="cabecalho-tela"><h1>Pedidos</h1></div>
  <div data-componente="galeria-tabela"><span data-componente="badge-status">aberto</span></div>
</section>
"""
RE_ACHADO = re.compile(r":\d+: (ERRO|AVISO) (V\d{3}) ")


def montar(pasta: Path, corpo: str = TELA_OK, cabeca: str = CABECA, nome: str = "index.html") -> Path:
    arquivo = pasta / nome
    arquivo.write_text(cabeca + corpo + PE, encoding="utf-8")
    return arquivo


def spec_mockups(pasta: Path, ids=("tl-01-lista", "tl-02-novo"), com_png: bool = True) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    spec = {"app": "Pedidos", "design_system": {"paleta": {"primaria": "#0F6CBD"}},
            "moldura": {"header": "faixa azul"},
            "telas": [{"id": i, "nome": i, "descricao": "x"} for i in ids]}
    caminho = pasta / "mockups.json"
    caminho.write_text(json.dumps(spec), encoding="utf-8")
    if com_png:
        for i in ids:
            (pasta / f"{i}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return caminho


def rodar(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=cwd)


def codigos(saida: str) -> list[str]:
    return [m.group(2) for m in map(RE_ACHADO.search, saida.splitlines()) if m]


def test_help_sai_com_zero():
    assert rodar("--help").returncode == 0


def test_codigos_lista_todos():
    saida = rodar("--codigos").stdout
    for codigo in ("V001", "V002", "V003", "V004", "V005", "V006", "V007", "V008", "V009",
                   "V010", "V011", "V012", "V013"):
        assert codigo in saida


def test_catalogo_embutido_bate_com_a_pasta_do_catalogo():
    na_pasta = {p.stem for p in CATALOGO.glob("*.md") if p.name != "INDICE.md"}
    assert set(vp.CATALOGO_CANVAS) == na_pasta


def test_prototipo_minimo_passa_limpo(tmp_path):
    r = rodar(str(montar(tmp_path)))
    assert r.returncode == 0, r.stdout
    assert r.stdout.strip().endswith("0 erro(s), 0 aviso(s)")


def test_molde_passa_limpo_e_usa_o_catalogo_inteiro():
    r = rodar(str(MOLDE), "--inventario")
    assert r.returncode == 0, r.stdout
    assert r.stdout.strip().endswith("0 erro(s), 0 aviso(s)")
    usados = set(vp.analisar(MOLDE.read_text(encoding="utf-8"), "molde").componentes())
    assert usados == set(vp.CATALOGO_CANVAS), sorted(set(vp.CATALOGO_CANVAS) - usados)


def test_molde_cobre_o_spec_de_mockups_do_kit(tmp_path):
    ids = [t["id"] for t in json.loads(MOLDE_MOCKUPS.read_text(encoding="utf-8"))["telas"]]
    pasta = tmp_path / "mockups"
    pasta.mkdir()
    (pasta / "mockups.json").write_text(MOLDE_MOCKUPS.read_text(encoding="utf-8"), encoding="utf-8")
    for i in ids:
        (pasta / f"{i}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    r = rodar(str(MOLDE), "--mockups", str(pasta / "mockups.json"))
    assert r.returncode == 0, r.stdout
    assert r.stdout.strip().endswith("0 erro(s), 0 aviso(s)")


@pytest.mark.parametrize("corpo, codigo", [
    (TELA_OK.replace("badge-status", "carrossel"), "V001"),
    (TELA_OK.replace('data-componente="badge-status"', 'data-componente=""'), "V001"),
    (TELA_OK + '<script src="https://cdn.contoso.com/lib.js"></script>', "V003"),
    (TELA_OK + '<link rel="stylesheet" href="//cdn.contoso.com/a.css">', "V003"),
    (TELA_OK + '<img src="http://contoso.com/logo.png" alt="logo">', "V003"),
    (TELA_OK + '<style>.x { background: url(https://contoso.com/a.png); }</style>', "V003"),
    (TELA_OK + '<style>@import "fontes.css";</style>', "V003"),
    ('<div data-componente="toast"></div>', "V004"),
    (TELA_OK + TELA_OK, "V005"),
    (TELA_OK.replace('data-tela="tela-pedidos"', 'data-tela="Tela Pedidos"'), "V005"),
    (TELA_OK.replace(' data-mockups="tl-01-lista,tl-02-novo"', ""), "V010"),
    (TELA_OK.replace('data-mockups="tl-01-lista,tl-02-novo"', 'data-mockups=""'), "V010"),
    (TELA_OK.replace("tl-02-novo", "../tl-02"), "V010"),
])
def test_erro_esperado(tmp_path, corpo, codigo):
    r = rodar(str(montar(tmp_path, corpo)))
    assert r.returncode == 1, r.stdout
    assert codigo in codigos(r.stdout)


def test_sem_aviso_de_prototipo_e_erro(tmp_path):
    cabeca = CABECA.replace(" data-prototipo-aviso", "")
    r = rodar(str(montar(tmp_path, cabeca=cabeca)))
    assert r.returncode == 1 and "V008" in codigos(r.stdout)


def test_aviso_dentro_do_canvas_e_erro(tmp_path):
    cabeca = CABECA.replace("<span data-prototipo-aviso>Protótipo para validação — não é o app</span>", "")
    corpo = TELA_OK + "<span data-prototipo-aviso>Protótipo para validação — não é o app</span>"
    r = rodar(str(montar(tmp_path, corpo, cabeca=cabeca)))
    assert r.returncode == 1 and "V008" in codigos(r.stdout)


@pytest.mark.parametrize("canvas", ['<main>', '<main data-canvas="grande">'])
def test_canvas_ausente_ou_invalido_e_erro(tmp_path, canvas):
    cabeca = CABECA.replace('<main data-canvas="1920x1080">', canvas)
    r = rodar(str(montar(tmp_path, cabeca=cabeca)))
    assert r.returncode == 1 and "V009" in codigos(r.stdout)


@pytest.mark.parametrize("corpo, codigo", [
    (TELA_OK.replace("badge-status", "novo:timeline"), "V002"),
    (TELA_OK.replace(' data-perfis="administrador,gestor"', ""), "V006"),
    (TELA_OK + '<style>.alerta { color: #c82333; }</style>', "V007"),
    (TELA_OK + '<style>.alerta { border-color: rgba(200, 35, 51, .5); }</style>', "V007"),
    (TELA_OK + '<style>.alerta { color: white; }</style>', "V007"),
    (TELA_OK + '<style>.tema { --fxColorPrimary: #000000; }</style>', "V007"),
    (TELA_OK + '<p style="color: rgb(0 0 0)">texto</p>', "V007"),
    (TELA_OK + '<svg viewBox="0 0 10 10"><path d="M0 0h10" fill="#0F6CBD"/></svg>', "V007"),
    (TELA_OK + "<script>el.style.background = '#0F6CBD';</script>", "V007"),
])
def test_aviso_esperado(tmp_path, corpo, codigo):
    r = rodar(str(montar(tmp_path, corpo)))
    assert r.returncode == 0, r.stdout
    assert codigo in codigos(r.stdout)


@pytest.mark.parametrize("corpo", [
    TELA_OK + '<a href="https://learn.microsoft.com/">referência</a>',
    TELA_OK + '<style>#aviso { color: var(--fxColorPrimary); } @media (prefers-color-scheme: dark) { :root { --fxColorSurface: #111827; } }</style>',
    TELA_OK + '<style>:root[data-theme="dark"] { --fxColorSurface: #111827; } .x { border: 1px solid transparent; }</style>',
    TELA_OK + '<svg viewBox="0 0 10 10"><use href="#icone"/><path d="M0 0h10" stroke="currentColor" fill="none"/></svg>',
    TELA_OK + '<style>.x { background: url(#grad); content: "#fff"; font-family: var(--fxFont); }</style>',
    TELA_OK + "<script>location.hash = '#/tela-pedidos'; const PASTA_MOCKUPS = '../mockups/';</script>",
    TELA_OK + '<img src="../mockups/tl-01-lista.png" alt="mockup">',
])
def test_nao_acusa_o_que_e_permitido(tmp_path, corpo):
    r = rodar(str(montar(tmp_path, corpo)))
    assert r.returncode == 0, r.stdout
    assert codigos(r.stdout) == []


def test_achado_traz_a_linha_do_elemento(tmp_path):
    arquivo = montar(tmp_path, TELA_OK.replace("badge-status", "carrossel"))
    linha_esperada = next(i for i, l in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1)
                          if "carrossel" in l)
    achado = next(l for l in rodar(str(arquivo)).stdout.splitlines() if "V001" in l)
    assert f":{linha_esperada}: ERRO V001" in achado


def test_achado_de_css_traz_a_linha_da_declaracao(tmp_path):
    corpo = TELA_OK + "<style>\n.a { color: var(--fxColorPrimary); }\n.b { color: #c82333; }\n</style>"
    arquivo = montar(tmp_path, corpo)
    linha_esperada = next(i for i, l in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1)
                          if "#c82333" in l)
    achado = next(l for l in rodar(str(arquivo)).stdout.splitlines() if "V007" in l)
    assert f":{linha_esperada}: AVISO V007" in achado


def test_inventario_lista_telas_componentes_e_mockups(tmp_path):
    corpo = TELA_OK + '<div data-componente="toast"></div>'
    saida = rodar(str(montar(tmp_path, corpo)), "--inventario").stdout
    linha = next(l for l in saida.splitlines() if l.startswith("| `tela-pedidos`"))
    assert "Pedidos" in linha and "administrador, gestor" in linha
    assert "`badge-status`" in linha and "`cabecalho-tela`" in linha and "`galeria-tabela`" in linha
    assert "`tl-01-lista`" in linha and "`tl-02-novo`" in linha
    assert any(l.startswith("| (global)") and "`toast`" in l for l in saida.splitlines())


def test_catalogo_alternativo_por_pasta(tmp_path):
    pasta = tmp_path / "catalogo"
    pasta.mkdir()
    for nome in ("cabecalho-tela", "galeria-tabela", "badge-status", "timeline"):
        (pasta / f"{nome}.md").write_text("# x\n", encoding="utf-8")
    corpo = TELA_OK.replace("badge-status", "timeline")
    r = rodar(str(montar(tmp_path, corpo)), "--catalogo", str(pasta))
    assert r.returncode == 0 and codigos(r.stdout) == []


def test_sem_caminho_usa_pastas_prototipo_da_config(tmp_path):
    (tmp_path / "power-platform.config.json").write_text(
        json.dumps({"pastas": {"prototipo": ["ux/proto"]}}), encoding="utf-8")
    pasta = tmp_path / "ux" / "proto"
    pasta.mkdir(parents=True)
    montar(pasta, TELA_OK.replace("badge-status", "carrossel"))
    r = rodar(cwd=tmp_path)
    assert r.returncode == 1 and "V001" in codigos(r.stdout)


def test_caminho_inexistente_e_uso_incorreto(tmp_path):
    assert rodar(str(tmp_path / "nao-existe.html")).returncode == 2


# ------------------------------------------------ origem nas imagens (--mockups)

def test_mockups_cobertos_e_pngs_presentes_passa_limpo(tmp_path):
    spec = spec_mockups(tmp_path / "mockups")
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec))
    assert r.returncode == 0, r.stdout
    assert r.stdout.strip().endswith("0 erro(s), 0 aviso(s)")


def test_id_que_nao_existe_no_spec_e_erro(tmp_path):
    spec = spec_mockups(tmp_path / "mockups", ids=("tl-01-lista",))
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec))
    assert r.returncode == 1 and "V011" in codigos(r.stdout)


def test_mockup_do_spec_sem_tela_no_prototipo_e_erro(tmp_path):
    spec = spec_mockups(tmp_path / "mockups", ids=("tl-01-lista", "tl-02-novo", "tl-03-inicio"))
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec))
    assert r.returncode == 1 and "V012" in codigos(r.stdout)
    assert "tl-03-inicio" in r.stdout


def test_png_ausente_e_aviso(tmp_path):
    spec = spec_mockups(tmp_path / "mockups", com_png=False)
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec))
    assert r.returncode == 0 and codigos(r.stdout).count("V013") == 2


def test_png_procurado_em_mockups_pasta_da_config(tmp_path):
    (tmp_path / "power-platform.config.json").write_text(
        json.dumps({"mockups": {"pasta": "imagens"}}), encoding="utf-8")
    spec = spec_mockups(tmp_path / "spec", com_png=False)
    (tmp_path / "imagens").mkdir()
    for i in ("tl-01-lista", "tl-02-novo"):
        (tmp_path / "imagens" / f"{i}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec), cwd=tmp_path)
    assert r.returncode == 0 and codigos(r.stdout) == [], r.stdout


@pytest.mark.parametrize("conteudo", [None, "{ quebrado", '{"telas": "x"}', '["lista"]'])
def test_spec_de_mockups_inexistente_ou_invalido_e_uso_incorreto(tmp_path, conteudo):
    spec = tmp_path / "mockups.json"
    if conteudo is not None:
        spec.write_text(conteudo, encoding="utf-8")
    r = rodar(str(montar(tmp_path)), "--mockups", str(spec))
    assert r.returncode == 2, r.stdout + r.stderr


def test_saida_utf8_mesmo_com_console_cp1252(tmp_path):
    arquivo = montar(tmp_path, TELA_OK.replace("badge-status", "carrossel"))
    r = subprocess.run([sys.executable, str(SCRIPT), str(arquivo)], capture_output=True,
                       env={**__import__("os").environ, "PYTHONIOENCODING": "cp1252"})
    assert r.returncode == 1
    assert "catálogo".encode("utf-8") in r.stdout
