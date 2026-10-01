"""Testes do validar-telas.py: uma fixture que passa e uma que falha por regra."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SKILL = RAIZ / "skills" / "powerapps-canvas"
SCRIPT = SKILL / "scripts" / "validar-telas.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

_spec = importlib.util.spec_from_file_location("validar_telas", SCRIPT)
vt = importlib.util.module_from_spec(_spec)
sys.modules["validar_telas"] = vt
_spec.loader.exec_module(vt)

ACHADO = re.compile(r"^(?P<arq>.+?):(?P<linha>\d+): (?P<nivel>ERRO|AVISO) (?P<cod>T\d{3}) ")


def rodar(capsys, *args: str) -> tuple[int, list[re.Match], str]:
    codigo = vt.main([str(a) for a in args])
    saida = capsys.readouterr().out
    achados = [m for m in (ACHADO.match(l) for l in saida.splitlines()) if m]
    return codigo, achados, saida


def codigos(achados: list[re.Match]) -> set[str]:
    return {m["cod"] for m in achados}


def test_fixture_que_passa_da_zero_achados(capsys):
    codigo, achados, saida = rodar(capsys, FIXTURES / "ok-tela-pura.md")
    assert codigo == 0 and not achados
    assert saida.strip().endswith("0 erro(s), 0 aviso(s)")


def test_bloco_cercado_que_passa(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "ok-tela-cercada.md")
    assert codigo == 0 and not achados


def test_colecao_local_nao_gera_aviso_de_delegacao(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "ok-delegacao-colecao.md")
    assert codigo == 0 and not achados


ESPERADOS = [
    ("erro-parse.md", "T001", "ERRO"),
    ("erro-sem-igual.md", "T002", "ERRO"),
    ("erro-sem-control.md", "T003", "ERRO"),
    ("erro-sem-versao.md", "T004", "ERRO"),
    ("erro-control-formula.md", "T005", "ERRO"),
    ("erro-ponto-virgula-duplo.md", "T007", "ERRO"),
    ("erro-pa2108.md", "T008", "ERRO"),
    ("aviso-rgba.md", "T009", "AVISO"),
    ("aviso-nome.md", "T010", "AVISO"),
    ("aviso-delegacao.md", "T011", "AVISO"),
    ("erro-chave-duplicada.md", "T012", "ERRO"),
    ("aviso-hash.md", "T015", "AVISO"),
    ("aviso-zorder.md", "T016", "AVISO"),
    ("aviso-run-sem-iferror.md", "T018", "AVISO"),
    ("erro-chave-topo.md", "T022", "ERRO"),
]


@pytest.mark.parametrize("arquivo,codigo,nivel", ESPERADOS)
def test_cada_regra_acusa_o_codigo_esperado(capsys, arquivo, codigo, nivel):
    saida_codigo, achados, _ = rodar(capsys, FIXTURES / arquivo)
    esperados = [m for m in achados if m["cod"] == codigo]
    assert esperados, f"{arquivo} deveria acusar {codigo}"
    assert esperados[0]["nivel"] == nivel
    assert saida_codigo == (1 if nivel == "ERRO" else 0)


def test_erro_de_parse_informa_a_linha(capsys):
    _, achados, _ = rodar(capsys, FIXTURES / "erro-parse.md")
    t001 = next(m for m in achados if m["cod"] == "T001")
    assert int(t001["linha"]) >= 8


def test_nome_duplicado_vale_para_o_conjunto_de_arquivos(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "dup-a.md", FIXTURES / "dup-b.md")
    assert codigo == 1 and "T006" in codigos(achados)
    sozinho, achados_a, _ = rodar(capsys, FIXTURES / "dup-a.md")
    assert sozinho == 0 and "T006" not in codigos(achados_a)


def test_yaml_puro_em_md_e_validado_e_nao_da_zero_zero(capsys):
    """O verde falso do validador antigo: .md sem cerca nunca era lido."""
    codigo, achados, saida = rodar(capsys, FIXTURES / "erro-sem-igual.md")
    assert codigo == 1 and achados
    assert "0 erro(s), 0 aviso(s)" not in saida


def test_arquivo_que_nao_e_tela_gera_um_unico_aviso(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "nao-tela-app.md")
    assert codigo == 0
    assert [m["cod"] for m in achados] == ["T020"]


def test_md_so_com_cercas_de_outra_linguagem_e_documentacao(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "doc-so-powershell.md")
    assert codigo == 0 and [m["cod"] for m in achados] == ["T020"]


def test_anti_exemplo_marcado_e_pulado(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "anti-exemplo.md")
    assert codigo == 0 and not achados


def test_snippet_de_propriedades_tambem_checa_dialeto(capsys):
    codigo, achados, _ = rodar(capsys, FIXTURES / "snippet-propriedades.md")
    assert codigo == 1 and "T007" in codigos(achados)


def test_contagem_sql_so_acusa_com_trilha_sql(capsys):
    arquivo = FIXTURES / "aviso-countrows-sql.md"
    _, sem_trilha, _ = rodar(capsys, arquivo)
    assert "T013" not in codigos(sem_trilha)
    _, com_trilha, _ = rodar(capsys, arquivo, "--trilha", "sql-server")
    assert "T013" in codigos(com_trilha)


def test_prefixo_de_coluna_so_acusa_com_trilha_dataverse(capsys, tmp_path):
    tela = tmp_path / "t.pa.yaml"
    tela.write_text(
        "Screens:\n  T:\n    Children:\n      - ex-cmb-x:\n          Control: Classic/ComboBox@2.4.0\n"
        "          Properties:\n            DisplayFields: =[\"nome\"]\n", encoding="utf-8")
    cfg = tmp_path / "power-platform.config.json"
    cfg.write_text(json.dumps({"trilha_dados": "dataverse", "prefixo_publisher": "abc_"}), encoding="utf-8")
    _, achados, _ = rodar(capsys, tela, "--config", cfg)
    assert "T014" in codigos(achados)


def test_config_ignorar_e_pastas_telas(capsys, tmp_path):
    (tmp_path / "Frontend" / "old").mkdir(parents=True)
    (tmp_path / "Frontend" / "ok.md").write_text((FIXTURES / "ok-tela-pura.md").read_text(encoding="utf-8"),
                                                 encoding="utf-8")
    (tmp_path / "Frontend" / "old" / "ruim.md").write_text(
        (FIXTURES / "erro-sem-igual.md").read_text(encoding="utf-8"), encoding="utf-8")
    cfg = tmp_path / "power-platform.config.json"
    cfg.write_text(json.dumps({"pastas": {"telas": ["Frontend"]}, "ignorar": ["**/old/**"]}), encoding="utf-8")
    codigo, achados, _ = rodar(capsys, "--config", cfg)
    assert codigo == 0 and not achados


def test_uso_incorreto_devolve_2(capsys):
    assert vt.main([str(FIXTURES / "nao-existe.md")]) == 2


def test_cli_help_e_exit_codes():
    ajuda = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
    assert ajuda.returncode == 0 and "--config" in ajuda.stdout
    erro = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "erro-sem-igual.md")],
                          capture_output=True, text=True, encoding="utf-8")
    assert erro.returncode == 1 and erro.stdout.strip().splitlines()[-1].startswith("1 erro(s)")


def test_todos_os_codigos_documentados_existem_no_script():
    usados = set(re.findall(r'"(T\d{3})"', SCRIPT.read_text(encoding="utf-8")))
    assert usados <= set(vt.CODIGOS)


def test_documentacao_da_skill_passa_no_proprio_validador(capsys):
    """Catálogo, moldes e referências não podem ensinar o que o validador recusa."""
    codigo, achados, saida = rodar(capsys, SKILL / "references", SKILL / "assets")
    erros = [m.string for m in achados if m["nivel"] == "ERRO"]
    assert codigo == 0, "\n".join(erros) or saida


def test_tela_molde_passa_sem_nenhum_achado(capsys):
    codigo, achados, saida = rodar(capsys, SKILL / "assets" / "tela-molde.md")
    assert codigo == 0 and not achados, saida


def test_tela_molde_na_trilha_sql_so_acusa_a_contagem_declarada(capsys):
    codigo, achados, _ = rodar(capsys, SKILL / "assets" / "tela-molde.md", "--trilha", "sql-server")
    assert codigo == 0 and codigos(achados) == {"T013"}


def test_tokens_usados_no_yaml_existem_no_bloco_de_tokens():
    definidos = set(re.findall(r"^(fx[A-Za-z0-9]+)\s*=", (SKILL / "assets" / "app-formulas-tokens.md")
                               .read_text(encoding="utf-8"), re.M))
    usados: set[str] = set()
    for arq in [SKILL / "assets" / "tela-molde.md", SKILL / "references" / "ux-componentes.md",
                SKILL / "references" / "ux-feedback.md"]:
        blocos, _ = vt.extrair_blocos(arq.read_text(encoding="utf-8"))
        for _, texto in blocos:
            usados |= set(re.findall(r"\b(fx[A-Z][A-Za-z0-9]*)\b", vt.limpar(texto)))
    assert usados - definidos == set()
