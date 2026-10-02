"""Testes do verificar-fluxo.py: o molde passa; cada fixture falha com o código esperado."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-automate" / "scripts" / "verificar-fluxo.py"
MOLDE = RAIZ / "skills" / "power-automate" / "assets" / "flow-gravar-molde.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

_spec = importlib.util.spec_from_file_location("verificar_fluxo", SCRIPT)
vf = importlib.util.module_from_spec(_spec)
sys.modules["verificar_fluxo"] = vf  # antes de exec_module: o dataclass precisa do módulo registrado
_spec.loader.exec_module(vf)

CODIGOS_ERRO = {
    "F001-json-invalido.json": "F001",
    "F002-envelope-sem-chaves.json": "F002",
    "F003-no-folha-identidade.json": "F003",
    "F004-nome-duplicado.json": "F004",
    "F005-runafter-inexistente.json": "F005",
    "F006-referencia-inexistente.json": "F006",
    "F007-items-fora-do-foreach.json": "F007",
    "F008-caso-colide-com-acao.json": "F008",
    "F009-catch-sem-skipped.json": "F009",
    "F010-response-sem-4-campos.json": "F010",
    "F011-outputs-de-select.json": "F011",
    "F013-expressao-longa.json": "F013",
    "F015-response-sem-terminate.json": "F015",
    "F016-condicao-constante.json": "F016",
    "F017-conexao-ausente.json": "F017",
    "F019-segmentos-guid-repetido.json": "F019",
    "F020-condicao-em-texto.json": "F020",
}
CODIGOS_AVISO = {
    "F012-coalesce-string.json": "F012",
    "F014-literal-de-ambiente.json": "F014",
    "F018-parametro-interpolado.json": "F018",
    "F021-inicializar-variavel-no-escopo.json": "F021",
    "F022-variavel-pura.json": "F022",
    "F023-fazer-ate-em-texto.json": "F023",
}


def rodar(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8", cwd=cwd or FIXTURES)


def achados_de(caminho: Path) -> list:
    achados, _ = vf.verificar_arquivo(caminho, caminho.name, True, False, vf.NOMES_CONFIG_PADRAO)
    return achados


def test_molde_passa_sem_erro_nem_aviso():
    assert achados_de(MOLDE) == []
    r = rodar(str(MOLDE))
    assert r.returncode == 0
    assert r.stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"


@pytest.mark.parametrize("arquivo,codigo", sorted(CODIGOS_ERRO.items()))
def test_fixture_acusa_erro_esperado(arquivo, codigo):
    achados = achados_de(FIXTURES / arquivo)
    assert [(a.nivel, a.codigo) for a in achados] == [("ERRO", codigo)], [a.formatar() for a in achados]
    r = rodar(arquivo)
    assert r.returncode == 1
    assert f"ERRO {codigo}" in r.stdout


@pytest.mark.parametrize("arquivo,codigo", sorted(CODIGOS_AVISO.items()))
def test_fixture_acusa_aviso_esperado(arquivo, codigo):
    achados = achados_de(FIXTURES / arquivo)
    assert [(a.nivel, a.codigo) for a in achados] == [("AVISO", codigo)], [a.formatar() for a in achados]
    assert rodar(arquivo).returncode == 0


def test_cada_codigo_tem_fixture():
    cobertos = set(CODIGOS_ERRO.values()) | set(CODIGOS_AVISO.values())
    assert cobertos == {f"F{n:03d}" for n in range(1, 24)}


def test_no_folha_do_designer_passa():
    assert achados_de(FIXTURES / "no-folha-valido.json") == []


def test_formato_da_linha_usa_nome_da_acao_em_json_de_uma_linha():
    r = rodar("F006-referencia-inexistente.json")
    assert re.search(r"^F006-referencia-inexistente\.json:Codigo_gravar: ERRO F006 ", r.stdout, re.M)
    assert re.search(r"^\d+ erro\(s\), \d+ aviso\(s\)$", r.stdout.strip().splitlines()[-1])


def test_f001_informa_a_linha_do_json():
    r = rodar("F001-json-invalido.json")
    assert "F001-json-invalido.json:2: ERRO F001" in r.stdout


def test_definicao_de_solucao_com_gatilho_power_apps_cobra_os_4_campos():
    achados = achados_de(FIXTURES / "definicao-solucao-sem-url.json")
    assert [a.codigo for a in achados] == ["F010"]


def test_md_com_cerca_json_e_aceito_e_md_comum_e_ignorado():
    assert achados_de(FIXTURES / "molde-em-markdown.md") == []
    r = rodar(str(FIXTURES / "nao-e-flow.md"))
    assert r.returncode == 0
    assert "1 ignorado(s)" in r.stdout


def test_estrito_acusa_coalesce_string_com_fallback_vazio(tmp_path):
    dados = json.loads(MOLDE.read_text(encoding="utf-8"))
    sv = dados["serializedValue"]["actions"]["Try_gravar"]["actions"]["Switch_acao"]["cases"]["Caso_gravar"]["actions"]
    sv["Codigo_gravar"]["inputs"] = "@coalesce(string(body('Gravar_registro')?['x']),'')"
    alvo = tmp_path / "flow.json"
    alvo.write_text(json.dumps(dados), encoding="utf-8")
    assert rodar(str(alvo)).stdout.strip().endswith("0 erro(s), 0 aviso(s)")
    assert rodar("--estrito", str(alvo)).stdout.strip().endswith("0 erro(s), 1 aviso(s)")


def test_config_pastas_flows_e_ignorar(tmp_path):
    (tmp_path / "Backend" / "nos").mkdir(parents=True)
    (tmp_path / "Backend" / "nos" / "bom.json").write_text(MOLDE.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "Backend" / "nos" / "old").mkdir()
    (tmp_path / "Backend" / "nos" / "old" / "quebrado.json").write_text("{", encoding="utf-8")
    (tmp_path / vf.NOME_CONFIG).write_text(json.dumps({"pastas": {"flows": ["Backend/nos"]}, "ignorar": ["**/old/**"]}), encoding="utf-8")
    r = rodar(cwd=tmp_path)
    assert r.returncode == 0, r.stdout
    assert "# config: power-platform.config.json" in r.stdout
    (tmp_path / vf.NOME_CONFIG).write_text(json.dumps({"pastas": {"flows": ["Backend/nos"]}}), encoding="utf-8")
    assert rodar(cwd=tmp_path).returncode == 1


def test_sem_config_diz_que_usa_defaults(tmp_path):
    r = rodar(str(MOLDE), cwd=tmp_path)
    assert "defaults genéricos" in r.stdout


def test_uso_incorreto_devolve_2(tmp_path):
    assert rodar("nao-existe.json").returncode == 2
    assert rodar("--config", "nao-existe.json", str(MOLDE)).returncode == 2
    assert rodar("--opcao-inexistente").returncode == 2


def test_script_so_le_e_help_funciona():
    antes = MOLDE.read_bytes()
    assert rodar("--help").returncode == 0
    rodar(str(MOLDE))
    assert MOLDE.read_bytes() == antes


def test_catch_fora_do_nome_catch_e_aviso_nao_erro():
    escopo = {"Log": {"type": "Scope", "actions": {}, "runAfter": {"Principal": ["Succeeded", "Failed"]}},
              "Principal": {"type": "Scope", "actions": {}}}
    ctx = vf.Contexto("x")
    vf.checar_catch(ctx, escopo)
    assert [(a.nivel, a.codigo) for a in ctx.achados] == [("AVISO", "F009")]


def test_response_http_antecipada_e_aviso():
    acoes = {"Resp": {"type": "Response", "kind": "Http", "inputs": {"statusCode": 200, "body": {}}},
             "Depois": {"type": "Compose", "inputs": "x", "runAfter": {"Resp": ["Succeeded"]}}}
    ctx = vf.Contexto("x")
    vf.checar_respostas(ctx, acoes)
    assert [(a.nivel, a.codigo) for a in ctx.achados] == [("AVISO", "F015")]


# ---------- colagem no designer novo (F020-F023) ----------

def _no_if(expressao) -> dict:
    return {"type": "If", "expression": expressao, "actions": {}, "else": {"actions": {}}}


def _analisar(acoes: dict, colagem: bool) -> list[tuple[str, str]]:
    ctx = vf.Contexto("x", colagem=colagem)
    vf.analisar_acoes(ctx, acoes, None, None)
    return [(a.nivel, a.codigo) for a in ctx.achados]


def test_f020_condicao_sem_and_ou_or_na_raiz_e_aviso():
    acoes = {"Se": _no_if({"equals": ["@empty(triggerBody()?['text'])", "@true"]})}
    assert _analisar(acoes, colagem=True) == [("AVISO", "F020")]
    acoes = {"Se": _no_if({"and": [{"equals": ["@empty(triggerBody()?['text'])", "@true"]}]})}
    assert _analisar(acoes, colagem=True) == []


def test_f020_condicao_em_texto_e_erro_tambem_na_definicao():
    assert _analisar({"Se": _no_if("@empty(triggerBody()?['text'])")}, colagem=False) == [("ERRO", "F020")]


def test_f021_inicializar_variavel_fora_da_raiz_da_definicao_e_erro():
    iniciar = {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Total", "type": "integer", "value": 0}]}}
    assert _analisar({"Iniciar": iniciar}, colagem=False) == []
    assert _analisar({"Escopo": {"type": "Scope", "actions": {"Iniciar": iniciar}}}, colagem=False) == [("ERRO", "F021")]


def test_f022_variavel_iniciada_dentro_do_trecho_colado_e_erro():
    acoes = {"Escopo": {"type": "Scope", "actions": {
        "Iniciar": {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Total", "type": "integer", "value": 0}]}},
        "Ler": {"type": "Compose", "inputs": "@{variables('Total')}", "runAfter": {"Iniciar": ["Succeeded"]}},
        "Dobro": {"type": "Compose", "inputs": "@mul(variables('Total'), 2)", "runAfter": {"Ler": ["Succeeded"]}},
    }}}
    assert sorted(_analisar(acoes, colagem=True)) == [("AVISO", "F021"), ("ERRO", "F022")]


def test_f022_e_f023_nao_valem_para_a_definicao_exportada():
    acoes = {"Ler": {"type": "Compose", "inputs": "@variables('Total')"},
             "Esperar": {"type": "Until", "expression": "@equals(variables('Total'), 3)", "limit": {"count": 3},
                         "actions": {}}}
    assert _analisar(acoes, colagem=False) == []
    assert sorted(_analisar(acoes, colagem=True)) == [("AVISO", "F022"), ("AVISO", "F023")]
