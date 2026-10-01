"""Testes de `skills/sql-procedures/scripts/lint-procedure.py`.

Cada regra tem uma fixture que falha com o codigo esperado; o molde da skill passa.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "sql-procedures" / "scripts" / "lint-procedure.py"
ASSETS = RAIZ / "skills" / "sql-procedures" / "assets"
REFERENCIAS = RAIZ / "skills" / "sql-procedures" / "references"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _carregar():
    spec = importlib.util.spec_from_file_location("lint_procedure", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["lint_procedure"] = modulo
    spec.loader.exec_module(modulo)
    return modulo


lint = _carregar()


def rodar(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          cwd=str(cwd or FIXTURES), encoding="utf-8")


def achados(nome: str, *extra: str) -> list[str]:
    r = rodar(str(FIXTURES / nome), *extra)
    return [linha for linha in r.stdout.splitlines() if ": ERRO " in linha or ": AVISO " in linha]


def codigos(nome: str, *extra: str) -> set[str]:
    return {linha.split(" ")[2] for linha in achados(nome, *extra)}


# --- o que passa -----------------------------------------------------------------

@pytest.mark.parametrize("arquivo", [
    ASSETS / "procedure-escrita-molde.sql",
    ASSETS / "funcao-leitura-molde.sql",
    FIXTURES / "funcao_valida.sql",
    FIXTURES / "doc_so_limpo.md",
])
def test_arquivos_limpos_passam(arquivo: Path) -> None:
    r = rodar(str(arquivo))
    assert r.returncode == 0, r.stdout
    assert r.stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"


def test_comentarios_e_strings_sao_ignorados() -> None:
    assert achados("ignora_comentarios_e_strings.sql") == []


def test_lint_ok_dispensa_achado() -> None:
    assert achados("dispensa_lint_ok.sql") == []


def test_referencias_da_skill_nao_tem_erro() -> None:
    arquivos = sorted(REFERENCIAS.rglob("*.md"))
    assert arquivos, "references/ vazia"
    r = rodar(*[str(a) for a in arquivos])
    assert r.returncode == 0, r.stdout


# --- uma fixture por regra -------------------------------------------------------

@pytest.mark.parametrize("arquivo,codigo,nivel", [
    ("p001_sem_nocount.sql", "P001", "ERRO"),
    ("p002_sem_xact_abort.sql", "P002", "ERRO"),
    ("p003_tran_sem_commit.sql", "P003", "ERRO"),
    ("p004_retorno_incompleto.sql", "P004", "AVISO"),
    ("p005_nome_fora_padrao.sql", "P005", "AVISO"),
    ("p006_cast_data_int.sql", "P006", "AVISO"),
    ("p007_select_estrela.sql", "P007", "AVISO"),
    ("p008_sem_schema.sql", "P008", "AVISO"),
    ("p009_sql_dinamico.sql", "P009", "ERRO"),
    ("p010_nolock.sql", "P010", "AVISO"),
    ("p011_output_sem_into.sql", "P011", "AVISO"),
])
def test_cada_regra_acusa(arquivo: str, codigo: str, nivel: str) -> None:
    linhas = [l for l in achados(arquivo) if f" {codigo} " in l]
    assert linhas, f"{codigo} nao acusado em {arquivo}"
    assert f": {nivel} {codigo} " in linhas[0]


def test_erro_devolve_exit_1_e_aviso_devolve_0() -> None:
    assert rodar(str(FIXTURES / "p001_sem_nocount.sql")).returncode == 1
    r = rodar(str(FIXTURES / "p007_select_estrela.sql"))
    assert r.returncode == 0
    assert r.stdout.strip().splitlines()[-1] == "0 erro(s), 1 aviso(s)"


def test_formato_da_linha_e_resumo() -> None:
    r = rodar(str(FIXTURES / "p001_sem_nocount.sql"))
    primeira = [l for l in r.stdout.splitlines() if "P001" in l][0]
    assert primeira.startswith("p001_sem_nocount.sql:1: ERRO P001 ") or ":1: ERRO P001" in primeira
    assert r.stdout.strip().splitlines()[-1] == "1 erro(s), 0 aviso(s)"


def test_linha_do_achado_aponta_para_o_statement() -> None:
    linhas = [l for l in achados("p007_select_estrela.sql") if "P007" in l]
    assert ":6: AVISO P007" in linhas[0]


# --- .md com bloco sql -----------------------------------------------------------

def test_md_le_bloco_sql_e_ignora_texto_e_outros_blocos() -> None:
    linhas = achados("doc_com_bloco.md")
    p001 = [l for l in linhas if "P001" in l]
    assert len(p001) == 1
    # CREATE esta na linha 6 do .md (numero de linha do arquivo, nao do bloco)
    assert ":6: ERRO P001" in p001[0]
    assert not any("Fora_Do_Bloco" in l or "Bloco_Texto" in l for l in linhas)


# --- configuracao e opcoes -------------------------------------------------------

def test_padrao_nome_por_flag() -> None:
    assert "P005" in codigos("p005_nome_fora_padrao.sql")
    assert "P005" not in codigos("p005_nome_fora_padrao.sql", "--padrao-nome", r"^baixar_\w+$")


def test_default_aceita_usp_e_sp_maiusculo(tmp_path: Path) -> None:
    sql = tmp_path / "a.sql"
    sql.write_text(
        "CREATE PROCEDURE dbo.SP_APP_UPD_ITEM AS BEGIN SET NOCOUNT ON; SELECT 1 AS x; END\nGO\n"
        "CREATE PROCEDURE dbo.sp_APP_item AS BEGIN SET NOCOUNT ON; SELECT 1 AS x; END\n",
        encoding="utf-8")
    r = rodar(str(sql), cwd=tmp_path)
    p005 = [l for l in r.stdout.splitlines() if "P005" in l]
    assert len(p005) == 1 and "sp_APP_item" in p005[0]


def test_colunas_retorno_vazia_desliga_p004() -> None:
    assert "P004" in codigos("p004_retorno_incompleto.sql")
    assert "P004" not in codigos("p004_retorno_incompleto.sql", "--colunas-retorno", "")


def test_config_define_pastas_ignorar_e_nome(tmp_path: Path) -> None:
    procs = tmp_path / "Backend" / "procs"
    (procs / "old").mkdir(parents=True)
    ruim = (FIXTURES / "p001_sem_nocount.sql").read_text(encoding="utf-8")
    (procs / "nova.sql").write_text(ruim, encoding="utf-8")
    (procs / "old" / "velha.sql").write_text(ruim, encoding="utf-8")
    (tmp_path / "power-platform.config.json").write_text(json.dumps({
        "pastas": {"procedures": ["Backend/procs"]},
        "ignorar": ["**/old/**"],
        "padrao_nome_procedure": r"^usp_ZZZ_\w+$",
    }), encoding="utf-8")
    r = rodar(cwd=tmp_path)
    assert "nova.sql" in r.stdout and "velha.sql" not in r.stdout
    assert "P005" in r.stdout            # nome do config nao casa
    assert "sem power-platform.config.json" not in r.stdout
    assert r.returncode == 1


def test_sem_config_avisa_na_saida(tmp_path: Path) -> None:
    (tmp_path / "x.sql").write_text(
        "CREATE PROCEDURE dbo.usp_APP_X_Y AS BEGIN SET NOCOUNT ON; SELECT 1 AS x; END\n", encoding="utf-8")
    r = rodar(str(tmp_path / "x.sql"), cwd=tmp_path)
    assert "sem power-platform.config.json" in r.stdout


def test_flag_config_explicita(tmp_path: Path) -> None:
    cfg = tmp_path / "meu.json"
    cfg.write_text(json.dumps({"colunas_retorno_procedure": []}), encoding="utf-8")
    assert "P004" not in codigos("p004_retorno_incompleto.sql", "--config", str(cfg))


# --- uso incorreto ---------------------------------------------------------------

def test_exit_2_caminho_inexistente() -> None:
    assert rodar("nao-existe.sql").returncode == 2


def test_exit_2_regex_invalido() -> None:
    assert rodar(str(FIXTURES / "p005_nome_fora_padrao.sql"), "--padrao-nome", "(").returncode == 2


def test_exit_2_config_invalido(tmp_path: Path) -> None:
    (tmp_path / "power-platform.config.json").write_text("{nao e json", encoding="utf-8")
    assert rodar(str(FIXTURES / "p001_sem_nocount.sql"), cwd=tmp_path).returncode == 2


def test_help_funciona() -> None:
    r = rodar("--help")
    assert r.returncode == 0 and "--padrao-nome" in r.stdout


# --- unidades --------------------------------------------------------------------

def test_so_leitura_nao_altera_arquivo() -> None:
    alvo = FIXTURES / "p001_sem_nocount.sql"
    antes = alvo.read_bytes()
    rodar(str(alvo))
    assert alvo.read_bytes() == antes


def test_mascarar_preserva_tamanho_e_linhas() -> None:
    texto = "SELECT 'a--b' -- fim\n/* x\n y */ SELECT 2"
    mascarado = lint.mascarar(texto)
    assert len(mascarado) == len(texto)
    assert mascarado.count("\n") == texto.count("\n")
    assert "a--b" not in mascarado and "fim" not in mascarado


def test_mascarar_comentario_de_bloco_aninhado() -> None:
    assert "oculto" not in lint.mascarar("/* a /* oculto */ ainda */ SELECT 1")


def test_cast_de_datediff_nao_acusa() -> None:
    sql = ("CREATE PROCEDURE dbo.usp_APP_A_B AS BEGIN SET NOCOUNT ON; "
           "SELECT CAST(DATEDIFF(day, 0, i.Dt_Inclusao) AS INT) AS x FROM dbo.T AS i; END")
    mascarado = lint.mascarar(sql)
    obj = lint.separar_objetos(mascarado)[0]
    assert lint.checar_cast_int(obj) == []


def test_convert_int_de_data_acusa() -> None:
    sql = "CREATE PROCEDURE dbo.usp_APP_A_B AS BEGIN SELECT CONVERT(INT, GETUTCDATE()); END"
    obj = lint.separar_objetos(lint.mascarar(sql))[0]
    assert [c for _, _, c, _ in lint.checar_cast_int(obj)] == ["P006"]


def test_exists_select_estrela_e_tolerado() -> None:
    sql = "CREATE PROCEDURE dbo.usp_APP_A_B AS BEGIN SELECT 1 WHERE EXISTS (SELECT * FROM dbo.T); END"
    obj = lint.separar_objetos(lint.mascarar(sql))[0]
    assert lint.checar_select_estrela(obj) == []


def test_sql_dinamico_literal_nao_acusa() -> None:
    sql = ("CREATE PROCEDURE dbo.usp_APP_A_B AS BEGIN SET NOCOUNT ON; "
           "EXEC (N'SELECT 1 AS x'); "
           "EXEC sp_executesql N'SELECT @p AS x', N'@p INT', @p = 1; END")
    obj = lint.separar_objetos(lint.mascarar(sql))[0]
    assert lint.checar_sql_dinamico(obj) == []


def test_sql_dinamico_com_parametros_e_variavel_montada_acusa() -> None:
    sql = ("CREATE PROCEDURE dbo.usp_APP_A_B @t NVARCHAR(50) AS BEGIN SET NOCOUNT ON; "
           "DECLARE @sql NVARCHAR(MAX) = N''; SELECT @sql = @sql + N'SELECT 1 FROM ' + @t; "
           "EXEC sp_executesql @sql; END")
    obj = lint.separar_objetos(lint.mascarar(sql))[0]
    assert [c for _, _, c, _ in lint.checar_sql_dinamico(obj)] == ["P009"]


def test_assinatura_sem_corpo_e_fragmento_de_documentacao(tmp_path: Path) -> None:
    doc = tmp_path / "contrato.md"
    doc.write_text("```sql\nCREATE OR ALTER PROCEDURE dbo.usp_APP_Item_Obter\n    @Email NVARCHAR(100)\nAS\n```\n",
                   encoding="utf-8")
    r = rodar(str(doc), cwd=tmp_path)
    assert r.stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"


def test_nome_com_placeholder_e_modelo_de_documentacao(tmp_path: Path) -> None:
    doc = tmp_path / "padrao.md"
    doc.write_text("```sql\nCREATE OR ALTER PROCEDURE dbo.usp_APP_<Entidade>_<Acao>\nAS\nBEGIN\n    UPDATE x SET y = 1;\nEND\n```\n",
                   encoding="utf-8")
    assert rodar(str(doc), cwd=tmp_path).stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"


def test_funcao_nao_exige_nocount(tmp_path: Path) -> None:
    sql = tmp_path / "f.sql"
    sql.write_text("CREATE FUNCTION dbo.tvf_APP_X () RETURNS TABLE AS RETURN (SELECT 1 AS x);\n", encoding="utf-8")
    assert rodar(str(sql), cwd=tmp_path).stdout.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"
