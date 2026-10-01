"""Testes de `skills/dataverse/scripts/extrair-nomes-as-built.py` (fixtures fictícias)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "dataverse" / "scripts" / "extrair-nomes-as-built.py"
FIX = Path(__file__).parent / "fixtures"


def _carregar():
    spec = importlib.util.spec_from_file_location("extrair_nomes_as_built", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["extrair_nomes_as_built"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def _rodar(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


def test_help_funciona():
    assert _rodar("--help").returncode == 0


def test_entrada_valida_sai_zero_e_nao_escreve_sem_saida(tmp_path):
    r = _rodar(FIX / "entitydefinitions-ok.json", "--prefixo", "abc_")
    assert r.returncode == 0
    assert r.stderr.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"
    assert r.stdout == ""


def test_gera_markdown_com_tipos_e_aspas(tmp_path):
    saida = tmp_path / "nomes.md"
    r = _rodar(FIX / "entitydefinitions-ok.json", "--prefixo", "abc_", "--saida", saida)
    assert r.returncode == 0
    texto = saida.read_text(encoding="utf-8")
    assert "`'produto-unidade'`" in texto  # hífen exige aspas simples
    assert "| `unidade_origem` | `abc_unidadedeorigem` | String | Texto |" in texto
    assert "opções: Ativo=1; Inativo=2" in texto
    assert "`'situacao (produto-unidade)'`" in texto  # nome da Choice em Power Fx
    assert "aponta para `abc_categoria`" in texto
    assert "exibição = nome da tabela: usar aspas" in texto
    assert "createdon" not in texto and "outro_campo" not in texto  # sistema e fora do prefixo


def test_stdout_com_saida_traco():
    r = _rodar(FIX / "entitydefinitions-ok.json", "--prefixo", "abc_", "--saida", "-")
    assert r.returncode == 0 and r.stdout.startswith("# Nomes as-built")


def test_entidade_sem_atributos_acusa_e002():
    r = _rodar(FIX / "entitydefinitions-sem-atributos.json")
    assert r.returncode == 1
    assert "ERRO E002" in r.stderr


def test_json_quebrado_acusa_e001():
    r = _rodar(FIX / "quebrado.json")
    assert r.returncode == 1 and "ERRO E001" in r.stderr


def test_prefixo_sem_correspondencia_acusa_e003():
    r = _rodar(FIX / "entitydefinitions-ok.json", "--prefixo", "zzz_")
    assert r.returncode == 1 and "ERRO E003" in r.stderr


def test_exibicao_duplicada_e_sem_rotulo_sao_avisos():
    r = _rodar(FIX / "entidade-duplicada.json", "--prefixo", "abc_")
    assert r.returncode == 0
    assert "AVISO D001" in r.stderr and "AVISO A001" in r.stderr


def test_arquivo_inexistente_sai_dois():
    assert _rodar(FIX / "nao-existe.json").returncode == 2


def test_recusa_sobrescrever_a_entrada(tmp_path):
    copia = tmp_path / "e.json"
    copia.write_text((FIX / "entitydefinitions-ok.json").read_text(encoding="utf-8"), encoding="utf-8")
    r = _rodar(copia, "--saida", copia)
    assert r.returncode == 2
    assert copia.read_text(encoding="utf-8").startswith("{")


@pytest.mark.parametrize("nome,esperado", [("nome", "nome"), ("table-x", "'table-x'"), ("a b", "'a b'"), ("d'a", "'d''a'"), ("1a", "'1a'")])
def test_identificador_powerfx(nome, esperado):
    assert mod.identificador_powerfx(nome) == esperado


def test_choice_sem_opcoes_avisa_a003():
    r = _rodar(FIX / "entitydefinitions-sem-cast.json", "--prefixo", "abc_")
    assert r.returncode == 0 and "AVISO A003" in r.stderr


def test_complemento_funde_opcoes_e_destinos(tmp_path):
    saida = tmp_path / "n.md"
    r = _rodar(FIX / "entitydefinitions-sem-cast.json", "--prefixo", "abc_",
               "--complemento", f"abc_produto={FIX / 'complemento-produto.json'}", "--saida", saida)
    assert r.returncode == 0 and "A003" not in r.stderr
    texto = saida.read_text(encoding="utf-8")
    assert "opções: Ativo=1; Inativo=2" in texto and "aponta para `abc_categoria`" in texto


def test_complemento_de_tabela_inexistente_acusa_e004():
    r = _rodar(FIX / "entitydefinitions-ok.json", "--complemento", f"abc_zzz={FIX / 'complemento-produto.json'}")
    assert r.returncode == 1 and "ERRO E004" in r.stderr


def test_complemento_quebrado_acusa_e005():
    r = _rodar(FIX / "entitydefinitions-ok.json", "--complemento", f"abc_produto={FIX / 'quebrado.json'}")
    assert r.returncode == 1 and "ERRO E005" in r.stderr
