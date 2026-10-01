"""Catálogo de componentes: todo bloco YAML de assets/componentes/ passa no validar-telas.py.

O validador só vê o que classifica como tela, fragmento ou mapa de controles; um bloco que cai em
"outro" é ignorado sem aviso. Por isso este teste também exige que cada arquivo tenha pelo menos
um bloco de fato validado e planta um erro para provar que o validador acusa nesses arquivos.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[2]
SKILL = RAIZ / "skills" / "powerapps-canvas"
SCRIPT = SKILL / "scripts" / "validar-telas.py"
COMPONENTES = SKILL / "assets" / "componentes"

_spec = importlib.util.spec_from_file_location("validar_telas_componentes", SCRIPT)
vt = importlib.util.module_from_spec(_spec)
sys.modules["validar_telas_componentes"] = vt
_spec.loader.exec_module(vt)

ACHADO = re.compile(r"^(?P<arq>.+?):(?P<linha>\d+): (?P<nivel>ERRO|AVISO) (?P<cod>T\d{3}) ")
SECOES = ["Propósito", "Quando usar / quando não usar", "Anatomia", "Dependências", "YAML", "Parâmetros a trocar",
          "Comportamento", "Acessibilidade", "Armadilhas", "Variações"]
CLASSES_VALIDADAS = {"tela", "fragmento", "controles"}

ARQUIVOS = sorted(COMPONENTES.glob("*.md"))
COMPONENTES_MD = [a for a in ARQUIVOS if a.name != "INDICE.md"]


@pytest.fixture()
def config_neutra(tmp_path):
    """Config vazia: o resultado não depende de um power-platform.config.json acima do repositório."""
    arquivo = tmp_path / "power-platform.config.json"
    arquivo.write_text(json.dumps({"projeto": "teste"}), encoding="utf-8")
    return arquivo


def rodar(capsys, config, *alvos: Path):
    codigo = vt.main(["--config", str(config), *[str(a) for a in alvos]])
    saida = capsys.readouterr().out
    achados = [m for m in (ACHADO.match(l) for l in saida.splitlines()) if m]
    return codigo, achados, saida


def blocos_validados(arquivo: Path) -> list[str]:
    texto = arquivo.read_text(encoding="utf-8")
    blocos, _ = vt.extrair_blocos(texto)
    classes = []
    for _, corpo in blocos:
        raiz = yaml.compose(corpo, Loader=yaml.SafeLoader)
        classes.append(vt.classificar(raiz) if raiz is not None else "outro")
    return classes


def test_existem_componentes_e_indice():
    assert (COMPONENTES / "INDICE.md").is_file()
    assert len(COMPONENTES_MD) >= 15


@pytest.mark.parametrize("arquivo", ARQUIVOS, ids=lambda a: a.name)
def test_arquivo_passa_no_validador_sem_t020(capsys, config_neutra, arquivo):
    codigo, achados, saida = rodar(capsys, config_neutra, arquivo)
    erros = [m.string for m in achados if m["nivel"] == "ERRO"]
    t020 = [m.string for m in achados if m["cod"] == "T020"]
    assert codigo == 0 and not erros, "\n".join(erros) or saida
    assert not t020, "\n".join(t020)


def test_pasta_inteira_passa_junta(capsys, config_neutra):
    """Todos os arquivos no mesmo run: acusa nome duplicado entre unidades que dividem escopo."""
    codigo, achados, saida = rodar(capsys, config_neutra, COMPONENTES)
    assert codigo == 0, saida
    assert not [m for m in achados if m["cod"] == "T020"], saida
    assert saida.strip().endswith("0 erro(s), 0 aviso(s)"), saida


@pytest.mark.parametrize("arquivo", ARQUIVOS, ids=lambda a: a.name)
def test_todo_bloco_yaml_e_de_fato_validado(arquivo):
    classes = blocos_validados(arquivo)
    assert classes, f"{arquivo.name}: nenhum bloco yaml"
    ignorados = [c for c in classes if c not in CLASSES_VALIDADAS]
    assert not ignorados, f"{arquivo.name}: bloco(s) que o validador ignora em silêncio: {ignorados}"


@pytest.mark.parametrize("arquivo", COMPONENTES_MD, ids=lambda a: a.name)
def test_estrutura_do_componente(arquivo):
    texto = arquivo.read_text(encoding="utf-8")
    titulos = re.findall(r"^## (.+)$", texto, re.M)
    assert titulos == SECOES, f"{arquivo.name}: seções {titulos}"
    assert re.search(r"^Maturidade: \*\*(estável|único)\*\* · Frequência: \*\*(muito comum|comum|ocasional|rara)\*\*", texto, re.M)
    linha = re.search(r"^Maturidade: .*$", texto, re.M).group(0)
    assert not re.search(r"\d+ (telas?|projetos?)\b", linha), f"{arquivo.name}: contagem de projeto na linha de maturidade"
    assert "Destino: YAML colado no Studio" in texto
    for _, corpo in vt.extrair_blocos(texto)[0]:
        assert not re.search(r"^\s*(#\s*)?\.\.\.\s*$", corpo, re.M), f"{arquivo.name}: linha só com reticências (bloco precisa ser completo)"
        assert ";;" not in corpo, f"{arquivo.name}: ';;' em YAML"
        assert "RGBA(" not in corpo, f"{arquivo.name}: RGBA literal"


def test_indice_lista_todos_os_componentes():
    indice = (COMPONENTES / "INDICE.md").read_text(encoding="utf-8")
    for arquivo in COMPONENTES_MD:
        assert f"({arquivo.name})" in indice, f"{arquivo.name} fora do INDICE.md"
    for ref in re.findall(r"\]\(([a-z0-9-]+\.md)\)", indice):
        assert (COMPONENTES / ref).is_file(), f"INDICE.md aponta para {ref}, que não existe"
    assert "## Tokens a acrescentar" in indice


def test_validador_acusa_erro_plantado_nos_componentes(capsys, config_neutra, tmp_path):
    """Prova de que acusa: o mesmo arquivo com `;;` e RGBA plantados deixa de passar."""
    original = (COMPONENTES / "botoes.md").read_text(encoding="utf-8")
    plantado = original.replace("Size: =fxBtnFontSize", "Size: =fxBtnFontSize;; RGBA(1, 2, 3, 1)", 1)
    assert plantado != original
    alvo = tmp_path / "botoes-plantado.md"
    alvo.write_text(plantado, encoding="utf-8")
    codigo, achados, _ = rodar(capsys, config_neutra, alvo)
    assert codigo == 1
    assert {"T007", "T009"} <= {m["cod"] for m in achados}


def test_componentes_sem_aviso_nenhum(capsys, config_neutra):
    """Os blocos já saem normalizados: sem RGBA literal, sem nome fora de kebab-case, sem `.Run` solto."""
    _, achados, saida = rodar(capsys, config_neutra, COMPONENTES)
    assert not achados, saida
