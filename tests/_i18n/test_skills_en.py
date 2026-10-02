"""Skills do plugin en-US (`en/skills/`): o padrão de skill, o mapa e os moldes que os scripts leem."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
EN = RAIZ / "en"
PT_PP = RAIZ / "skills" / "power-platform"
EN_PP = EN / "skills" / "power-platform"
MAPA = json.loads((RAIZ / "i18n" / "mapa.json").read_text(encoding="utf-8"))["arquivos"]
FEITOS_EN = {e["en"]: pt for pt, e in MAPA.items() if e["situacao"] == "feito"}
RESUMO_LIMPO = "0 error(s), 0 warning(s)"
# `agente-x` sozinho é chave de `modelos.agentes` no config (igual nos dois idiomas); comando e agente não
COMANDO_PT = re.compile(r"/pp:|\bpp:agente-|agents/agente-")
LITERAL_EXPRESSAO = re.compile(r"'(?:[^']|'')*'")
IDENTIFICADOR = re.compile(r"'[A-Za-z0-9_.$/{}-]*'")
TRECHO_EXPRESSAO = re.compile(r"@\{[^}]*\}")
# título e descrição das ações e o texto das linhas do relatório; o resto do construtor é código: igual ao pt-BR
TEXTO_DO_FLUXO = {"title", "description", "rotulo", "resultado"}
STATUS_FILTRADO = "falhou"  # o Fechar/Falhas filtra o relatório por ele: fica igual nos dois idiomas
CHAVES_LIVRES = {"$.design_system.paleta"}  # no spec dos mockups, o nome da cor é texto livre


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


lint = _carregar("lint_skills_en", RAIZ / "tools" / "lint_skills.py")


def _rodar(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PP_LANG"}
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8",
                          cwd=cwd, env=env, timeout=120)


def _arquivos_en() -> list[str]:
    return sorted(p.relative_to(RAIZ).as_posix() for pasta in ("skills", "agents") if (EN / pasta).is_dir()
                  for p in (EN / pasta).rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("."))


# ---------------------------------------------------------------- padrão e mapa

@pytest.mark.parametrize("skill", sorted(p.parent for p in EN.glob("skills/*/SKILL.md")), ids=lambda p: p.name)
def test_skill_en_segue_o_padrao(skill):
    texto = (skill / "SKILL.md").read_text(encoding="utf-8")
    dados, erro = lint.ler_frontmatter(texto)
    assert erro is None, erro
    assert dados["name"] == skill.name
    descricao = str(dados.get("description") or "").strip()
    assert lint.DESCRICAO_MIN <= len(descricao) <= lint.DESCRICAO_MAX
    assert descricao.startswith("Use when") and "Do not use" in descricao
    assert len(texto.splitlines()) <= lint.LIMITE_AVISO_SKILL
    assert lint.checar_links(skill, texto, RAIZ) == []


def test_todo_arquivo_en_e_um_par_feito_do_mapa():
    orfaos = [p for p in _arquivos_en() if p not in FEITOS_EN]
    assert orfaos == [], "arquivo en-US fora do mapa ou com o par ainda `pendente`"


def test_texto_en_sem_comando_nem_agente_pt():
    achados = [f"{p}:{n}" for p in _arquivos_en() if not p.endswith(".py")
               for n, linha in enumerate((RAIZ / p).read_text(encoding="utf-8").splitlines(), start=1)
               if COMANDO_PT.search(linha)]
    assert achados == []


# ---------------------------------------------------------------- moldes da skill power-platform

def _esqueleto(texto: str) -> str:
    """O código de uma string do flow: sem o texto livre. Literal com espaço ou acento é texto (some);
    literal sem eles é nome de ação, variável ou chave (`outputs('Ler_plano')`) e tem de ficar igual."""
    def sem_texto(trecho: str) -> str:
        return LITERAL_EXPRESSAO.sub(lambda m: m.group(0) if IDENTIFICADOR.fullmatch(m.group(0)) else "''", trecho)

    if texto.startswith("@"):
        return sem_texto(texto)
    return "".join(sem_texto(t) for t in TRECHO_EXPRESSAO.findall(texto))


def _diferencas(pt, en, caminho: str = "$") -> list[str]:
    if type(pt) is not type(en):
        return [f"{caminho}: tipo"]
    if isinstance(pt, dict):
        if list(pt) != list(en):
            return [f"{caminho}: chaves"]
        return [d for k in pt for d in _diferencas(pt[k], en[k], f"{caminho}.{k}")]
    if isinstance(pt, list):
        if len(pt) != len(en):
            return [f"{caminho}: tamanho"]
        return [d for i, (a, b) in enumerate(zip(pt, en)) for d in _diferencas(a, b, f"{caminho}[{i}]")]
    if pt == en or (isinstance(pt, str) and STATUS_FILTRADO not in pt
                    and caminho.rsplit(".", 1)[-1] in TEXTO_DO_FLUXO):
        return []
    if isinstance(pt, str) and ("@" in pt) and _esqueleto(pt) == _esqueleto(en) and (pt.startswith("@") or "@{" in pt):
        return []
    return [f"{caminho}: {pt!r} -> {en!r}"]


def test_construtor_en_tem_o_mesmo_codigo_do_pt():
    texto_pt = (PT_PP / "assets" / "construtor-dataverse.json").read_text(encoding="utf-8")
    texto_en = (EN_PP / "assets" / "dataverse-builder.json").read_text(encoding="utf-8")
    assert _diferencas(json.loads(texto_pt), json.loads(texto_en)) == []
    assert texto_en.count(STATUS_FILTRADO) == texto_pt.count(STATUS_FILTRADO) > 0


def _codigos(saida: str) -> list[str]:
    return re.findall(r": (?:ERRO|AVISO|ERROR|WARNING) ([A-Z][0-9]{3}) ", saida)


@pytest.mark.parametrize("trilha", [["sql-server"], ["dataverse", "--flow"]], ids=lambda t: t[0])
def test_molde_en_da_carga_mockup_gera_como_o_pt(tmp_path, trilha):
    pt = _rodar(PT_PP / "scripts" / "montar-carga-mockup.py", str(PT_PP / "assets" / "carga-mockup-molde.json"),
                "--trilha", *trilha, "--saida", str(tmp_path / "pt"), cwd=tmp_path)
    en = _rodar(EN_PP / "scripts" / "montar-carga-mockup.py", str(EN_PP / "assets" / "mockup-load-template.json"),
                "--trilha", *trilha, "--saida", str(tmp_path / "en"), cwd=tmp_path)
    assert en.returncode == 0, en.stdout + en.stderr
    assert re.search(r"\b0 error\(s\)", en.stdout + en.stderr)
    assert _codigos(en.stdout + en.stderr) == _codigos(pt.stdout + pt.stderr)
    if "--flow" in trilha:
        assert (tmp_path / "en" / "dataverse-builder").is_dir()


def test_molde_en_dos_mockups_valida(tmp_path):
    spec = json.loads((EN_PP / "assets" / "mockups-template.json").read_text(encoding="utf-8"))
    assert spec["idioma"] == "en-US"
    r = _rodar(EN_PP / "scripts" / "desenhar-mockups.py", str(EN_PP / "assets" / "mockups-template.json"),
               "--simular", "--saida", str(tmp_path / "out"), cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip().splitlines()[-1] == RESUMO_LIMPO


def test_molde_en_do_prototipo_passa_limpo_e_cobre_os_mockups(tmp_path):
    script = EN_PP / "scripts" / "verificar-prototipo.py"
    molde = EN_PP / "assets" / "prototype-template.html"
    r = _rodar(script, str(molde), "--inventario", cwd=tmp_path)
    assert r.returncode == 0 and r.stdout.strip().endswith(RESUMO_LIMPO), r.stdout
    texto_mockups = (EN_PP / "assets" / "mockups-template.json").read_text(encoding="utf-8")
    pasta = tmp_path / "mockups"
    pasta.mkdir()
    (pasta / "mockups.json").write_text(texto_mockups, encoding="utf-8")
    for tela in json.loads(texto_mockups)["telas"]:
        (pasta / f"{tela['id']}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    r = _rodar(script, str(molde), "--mockups", str(pasta / "mockups.json"), cwd=tmp_path)
    assert r.returncode == 0 and r.stdout.strip().endswith(RESUMO_LIMPO), r.stdout


def _chaves(no, caminho: str = "$") -> set[str]:
    if caminho in CHAVES_LIVRES:
        return set()
    if isinstance(no, dict):
        return {f"{caminho}.{k}" for k in no} | {c for k, v in no.items() for c in _chaves(v, f"{caminho}.{k}")}
    if isinstance(no, list):
        return {c for v in no for c in _chaves(v, f"{caminho}[]")}
    return set()


@pytest.mark.parametrize("pt, en", [
    ("power-platform.config.exemplo.json", "power-platform.config.example.json"),
    ("carga-mockup-molde.json", "mockup-load-template.json"),
    ("mockups-molde.json", "mockups-template.json"),
])
def test_json_en_tem_as_mesmas_chaves(pt, en):
    a = json.loads((PT_PP / "assets" / pt).read_text(encoding="utf-8"))
    b = json.loads((EN_PP / "assets" / en).read_text(encoding="utf-8"))
    assert _chaves(a) == _chaves(b)
