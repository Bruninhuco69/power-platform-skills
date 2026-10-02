"""Skill `powerapps-canvas` do plugin en-US: o catálogo, os moldes e as referências passam no validador
en-US como os do pt-BR passam no pt-BR, e o YAML colado é o mesmo do pt-BR (muda só texto e comentário)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[2]
PT = RAIZ / "skills" / "powerapps-canvas"
EN = RAIZ / "en" / "skills" / "powerapps-canvas"
SCRIPT_EN = EN / "scripts" / "validar-telas.py"
COMPONENTES = EN / "assets" / "components"
INDICE = "INDEX.md"
MAPA = json.loads((RAIZ / "i18n" / "mapa.json").read_text(encoding="utf-8"))["arquivos"]
PARES_MD = sorted((RAIZ / pt, RAIZ / e["en"]) for pt, e in MAPA.items()
                  if pt.startswith("skills/powerapps-canvas/") and pt.endswith(".md"))

ACHADO = re.compile(r"^(?P<arq>.+?):(?P<linha>\d+): (?P<nivel>ERROR|WARNING) (?P<cod>T\d{3}) ", re.M)
RESUMO_LIMPO = "0 error(s), 0 warning(s)"
SECOES = ["Purpose", "When to use / when not to use", "Anatomy", "Dependencies", "YAML", "Parameters to change",
          "Behavior", "Accessibility", "Pitfalls", "Variations"]
MATURIDADE = re.compile(r"^Maturity: \*\*(stable|unique|new)\*\* · "
                        r"Frequency: \*\*(very common|common|occasional|rare|to be measured)\*\*", re.M)
CLASSES_VALIDADAS = {"tela", "fragmento", "controles"}  # valores internos do validador, iguais nos dois idiomas
IDENTIFICADOR = re.compile(r"[A-Za-z0-9_.@/<>-]*")  # tipo de controle, variante, nome: código


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


vt = _carregar("validar_telas_en", SCRIPT_EN)
vp = _carregar("verificar_prototipo_catalogo", RAIZ / "skills" / "power-platform" / "scripts" / "verificar-prototipo.py")
ARQUIVOS = sorted(COMPONENTES.glob("*.md"))
COMPONENTES_MD = [a for a in ARQUIVOS if a.name != INDICE]


@pytest.fixture(scope="module")
def config_neutra(tmp_path_factory):
    """Config vazia: o resultado não depende de um power-platform.config.json acima do repositório."""
    arquivo = tmp_path_factory.mktemp("cfg") / "power-platform.config.json"
    arquivo.write_text(json.dumps({"projeto": "teste"}), encoding="utf-8")
    return arquivo


def rodar(config: Path, *args) -> tuple[int, list[re.Match], str]:
    env = {k: v for k, v in os.environ.items() if k != "PP_LANG"}
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(SCRIPT_EN), "--config", str(config), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    return r.returncode, list(ACHADO.finditer(r.stdout)), r.stdout + r.stderr


def blocos_yaml(arquivo: Path) -> list[str]:
    return [corpo for _, corpo in vt.extrair_blocos(arquivo.read_text(encoding="utf-8"))[0]]


# ---------------------------------------------------------------- catálogo

def test_catalogo_en_e_o_do_verificar_prototipo():
    assert {a.stem for a in COMPONENTES_MD} == set(vp._CATALOGO_EN)


def test_pasta_inteira_passa_sem_achado_nenhum(config_neutra):
    codigo, achados, saida = rodar(config_neutra, COMPONENTES)
    assert codigo == 0 and not achados, saida
    assert saida.strip().endswith(RESUMO_LIMPO), saida


@pytest.mark.parametrize("arquivo", ARQUIVOS, ids=lambda a: a.name)
def test_todo_bloco_yaml_e_de_fato_validado(arquivo):
    classes = [vt.classificar(raiz) if (raiz := yaml.compose(c, Loader=yaml.SafeLoader)) is not None else "outro"
               for c in blocos_yaml(arquivo)]
    assert classes and set(classes) <= CLASSES_VALIDADAS, f"{arquivo.name}: {classes}"


@pytest.mark.parametrize("arquivo", COMPONENTES_MD, ids=lambda a: a.name)
def test_estrutura_do_componente(arquivo):
    texto = arquivo.read_text(encoding="utf-8")
    assert re.findall(r"^## (.+)$", texto, re.M) == SECOES
    assert MATURIDADE.search(texto)
    assert "Destination: YAML pasted into Studio" in texto
    for corpo in blocos_yaml(arquivo):
        assert ";;" not in corpo and "RGBA(" not in corpo
        assert not re.search(r"^\s*(#\s*)?\.\.\.\s*$", corpo, re.M)


def test_indice_lista_todos_os_componentes():
    indice = (COMPONENTES / INDICE).read_text(encoding="utf-8")
    assert {f"{a.name}" for a in COMPONENTES_MD} <= set(re.findall(r"\]\(([a-z0-9-]+\.md)\)", indice))
    assert all((COMPONENTES / ref).is_file() for ref in re.findall(r"\]\(([a-z0-9-]+\.md)\)", indice))
    assert "## Tokens to add" in indice


def test_validador_en_acusa_erro_plantado(config_neutra, tmp_path):
    original = (COMPONENTES / "buttons.md").read_text(encoding="utf-8")
    plantado = original.replace("Size: =fxBtnFontSize", "Size: =fxBtnFontSize;; RGBA(1, 2, 3, 1)", 1)
    assert plantado != original
    alvo = tmp_path / "buttons-planted.md"
    alvo.write_text(plantado, encoding="utf-8")
    codigo, achados, _ = rodar(config_neutra, alvo)
    assert codigo == 1 and {"T007", "T009"} <= {m["cod"] for m in achados}


# ---------------------------------------------------------------- moldes e referências

def test_documentacao_en_passa_no_validador(config_neutra):
    codigo, achados, saida = rodar(config_neutra, EN / "references", EN / "assets")
    assert codigo == 0, "\n".join(m.group(0) for m in achados if m["nivel"] == "ERROR") or saida


def test_molde_de_tela_passa_sem_achado_e_na_trilha_sql_so_t013(config_neutra):
    molde = EN / "assets" / "screen-template.md"
    codigo, achados, saida = rodar(config_neutra, molde)
    assert codigo == 0 and not achados, saida
    codigo, achados, _ = rodar(config_neutra, molde, "--trilha", "sql-server")
    assert codigo == 0 and {m["cod"] for m in achados} == {"T013"}


def test_tokens_usados_existem_no_bloco_de_tokens():
    definidos = set(re.findall(r"^(fx[A-Za-z0-9]+)\s*=", (EN / "assets" / "app-formulas-tokens.md")
                               .read_text(encoding="utf-8"), re.M))
    pt = set(re.findall(r"^(fx[A-Za-z0-9]+)\s*=", (PT / "assets" / "app-formulas-tokens.md").read_text(encoding="utf-8"), re.M))
    assert definidos == pt
    usados = {t for arq in ("assets/screen-template.md", "references/ux-components.md", "references/ux-feedback.md")
              for corpo in blocos_yaml(EN / arq) for t in re.findall(r"\b(fx[A-Z][A-Za-z0-9]*)\b", vt.limpar(corpo))}
    assert usados - definidos == set()


# ---------------------------------------------------------------- o YAML colado é o do pt-BR

def _formula(texto: str) -> str:
    return re.sub(r"\s+", " ", vt.limpar(texto)).strip()


def _sem_texto(bloco: str) -> str:
    """Bloco que nem é YAML válido (exemplo do que dá erro): o texto sem literais e sem comentário `#`."""
    return "\n".join(re.sub(r"\s*#.*$", "", vt.limpar(linha)).rstrip() for linha in bloco.splitlines())


def _diferencas(pt, en, caminho: str = "") -> list[str]:
    """O código do bloco é o mesmo: chaves, tipos e fórmulas sem o texto dos literais e sem comentário.
    Lê os nós (`yaml.compose`): `Prop: =` sozinho é texto no YAML colado, e o `safe_load` recusa. Valor
    sem `=` que no pt-BR tem cara de código (`Label@2.1.0`, `ManualLayout`) fica igual; o resto é texto."""
    if type(pt) is not type(en):
        return [f"{caminho}: tipo"]
    if isinstance(pt, yaml.MappingNode):
        chaves_pt, chaves_en = [k.value for k, _ in pt.value], [k.value for k, _ in en.value]
        if chaves_pt != chaves_en:
            return [f"{caminho}: chaves {chaves_pt} != {chaves_en}"]
        return [d for (k, a), (_, b) in zip(pt.value, en.value) for d in _diferencas(a, b, f"{caminho}.{k.value}")]
    if isinstance(pt, yaml.SequenceNode):
        if len(pt.value) != len(en.value):
            return [f"{caminho}: tamanho"]
        return [d for i, (a, b) in enumerate(zip(pt.value, en.value)) for d in _diferencas(a, b, f"{caminho}[{i}]")]
    if pt is None or pt.value == en.value:
        return []
    if pt.value.startswith("="):
        return [] if en.value.startswith("=") and _formula(pt.value) == _formula(en.value) else [f"{caminho}: fórmula"]
    return [f"{caminho}: {pt.value!r} -> {en.value!r}"] if IDENTIFICADOR.fullmatch(pt.value) else []


@pytest.mark.parametrize("pt, en", PARES_MD, ids=lambda p: p.name)
def test_yaml_en_e_o_do_pt(pt, en):
    blocos_pt, blocos_en = blocos_yaml(pt), blocos_yaml(en)
    assert len(blocos_en) == len(blocos_pt)
    for i, (a, b) in enumerate(zip(blocos_pt, blocos_en), start=1):
        try:
            arvore_pt = yaml.compose(a)
        except yaml.YAMLError:  # exemplo de YAML inválido de propósito: o texto, sem literais nem comentário
            assert _sem_texto(b) == _sem_texto(a), f"{en.name}: bloco yaml {i}"
            continue
        assert _diferencas(arvore_pt, yaml.compose(b)) == [], f"{en.name}: bloco yaml {i}"
