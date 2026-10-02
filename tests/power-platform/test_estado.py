"""Testes de `skills/power-platform/scripts/estado.py` (o ESTADO.md do pipeline /pp:*)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "estado.py"
HOJE = "2026-10-01"


def _carregar():
    spec = importlib.util.spec_from_file_location("estado", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["estado"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


@pytest.fixture(autouse=True)
def _data_fixa(monkeypatch):
    monkeypatch.setenv("PP_DATA_HOJE", HOJE)


@pytest.fixture
def projeto(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert mod.main(["iniciar", "--projeto", "Pedidos", "--ideia", "controlar pedidos por unidade"]) == 0
    return tmp_path


def _situacao(pasta: Path, etapa: str) -> str:
    return mod.ler_estado(pasta / "ESTADO.md")["etapas"][etapa]["situacao"]


def test_iniciar_cria_estado_com_novo_concluido_e_aponta_brainstorm(projeto, capsys):
    capsys.readouterr()
    assert _situacao(projeto, "novo") == "concluida"
    assert mod.main(["proximo"]) == 0
    saida = capsys.readouterr().out
    assert "`/pp:brainstorm`" in saida
    assert "nova sessão" in saida and "/clear" in saida


def test_iniciar_recusa_projeto_ja_iniciado(projeto, capsys):
    assert mod.main(["iniciar", "--projeto", "Outro"]) == 2
    assert "já existe" in capsys.readouterr().err


def test_comecar_fora_de_ordem_bloqueia_com_exit_1_e_mostra_a_etapa_certa(projeto, capsys):
    capsys.readouterr()
    assert mod.main(["comecar", "design"]) == 1
    saida = capsys.readouterr().out
    assert "ETAPA FORA DE ORDEM" in saida
    assert "`/pp:brainstorm`" in saida
    assert _situacao(projeto, "design") == "pendente"


def test_comecar_marca_andamento_e_proximo_diz_retomar(projeto, capsys):
    assert mod.main(["comecar", "brainstorm"]) == 0
    assert _situacao(projeto, "brainstorm") == "andamento"
    capsys.readouterr()
    mod.main(["proximo"])
    assert "Em andamento" in capsys.readouterr().out


def test_concluir_avanca_para_a_proxima_etapa(projeto, capsys):
    assert mod.main(["concluir", "brainstorm", "--nota", "PRD com o MVP"]) == 0
    saida = capsys.readouterr().out
    assert "`/pp:design`" in saida
    dados = mod.ler_estado(projeto / "ESTADO.md")
    assert dados["etapas"]["brainstorm"] == {"situacao": "concluida", "data": HOJE, "nota": "PRD com o MVP",
                                             "argumento": ""}


def test_concluir_fora_de_ordem_bloqueia(projeto):
    assert mod.main(["concluir", "arquitetura"]) == 1
    assert _situacao(projeto, "arquitetura") == "pendente"


def test_dispensar_conta_como_feita(projeto, capsys):
    for etapa in ("brainstorm", "design"):
        mod.main(["concluir", etapa])
    assert mod.main(["dispensar", "mockups", "--motivo", "sem chave da OpenAI"]) == 0
    assert "`/pp:prototipo`" in capsys.readouterr().out
    assert mod.main(["checar", "prototipo"]) == 0


def test_reabrir_volta_a_etapa_e_as_seguintes_ja_tocadas(projeto, capsys):
    for etapa in ("brainstorm", "design", "mockups"):
        mod.main(["concluir", etapa])
    mod.main(["comecar", "prototipo"])
    assert mod.main(["reabrir", "design", "--motivo", "ajustes do protótipo, rodada 1"]) == 0
    saida = capsys.readouterr().out
    assert [_situacao(projeto, e) for e in ("design", "mockups", "prototipo", "arquitetura")] == \
        ["reaberta", "reaberta", "reaberta", "pendente"]
    assert "`/pp:design`" in saida.split("Próximo passo")[1]
    assert "ajustes do protótipo, rodada 1" in saida


def test_reabrir_com_argumento_entra_no_comando_e_some_ao_concluir(projeto, capsys):
    for etapa in ("brainstorm", "design", "mockups", "prototipo", "arquitetura", "construir"):
        mod.main(["concluir", etapa])
    mod.main(["reabrir", "construir", "--motivo", "QA: fórmula de filtro", "--argumento", "app"])
    capsys.readouterr()
    mod.main(["proximo"])
    saida = capsys.readouterr().out
    assert "`/pp:construir app`" in saida
    assert "`/pp:construir flows`" in saida  # alternativa
    mod.main(["concluir", "construir"])
    assert mod.ler_estado(projeto / "ESTADO.md")["etapas"]["construir"]["argumento"] == ""


def test_todas_concluidas_mostra_app_publicado(projeto, capsys):
    for etapa in mod.IDS[1:]:
        assert mod.main(["concluir", etapa]) == 0
    capsys.readouterr()
    mod.main(["proximo"])
    assert "App publicado" in capsys.readouterr().out


def test_estado_renderiza_tabela_e_sobrevive_a_pipe_na_nota(projeto):
    mod.main(["concluir", "brainstorm", "--nota", "a | b --> c"])
    texto = (projeto / "ESTADO.md").read_text(encoding="utf-8")
    assert "| 2 | 1. Definição do produto | Brainstorm e requisitos |" in texto
    assert mod.ler_estado(projeto / "ESTADO.md")["etapas"]["brainstorm"]["nota"] == "a / b -> c"


def test_procura_estado_nas_pastas_acima(projeto, monkeypatch, capsys):
    sub = projeto / "docs" / "planejamento"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)
    capsys.readouterr()
    assert mod.main(["mostrar"]) == 0
    assert "PROGRESSO" in capsys.readouterr().out


def test_sem_estado_da_exit_2_e_manda_para_novo(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert mod.main(["mostrar"]) == 2
    assert "/pp:novo" in capsys.readouterr().err


@pytest.mark.parametrize("conteudo", [
    "# editado à mão, sem bloco\n",
    "<!-- pp:estado\n{quebrado\n-->\n",
    '<!-- pp:estado\n{"etapas": {}}\n-->\n',
])
def test_estado_corrompido_da_exit_2(tmp_path, monkeypatch, capsys, conteudo):
    (tmp_path / "ESTADO.md").write_text(conteudo, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert mod.main(["mostrar"]) == 2
    assert "ERRO" in capsys.readouterr().err


@pytest.mark.parametrize("args", [["dispensar", "novo", "--motivo", "x"], ["reabrir", "novo", "--motivo", "x"]])
def test_novo_nao_se_dispensa_nem_reabre(projeto, args):
    assert mod.main(args) == 2


def test_help_e_etapa_invalida_pela_linha_de_comando(tmp_path):
    ok = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, encoding="utf-8")
    assert ok.returncode == 0 and "brainstorm" in ok.stdout
    ruim = subprocess.run([sys.executable, str(SCRIPT), "checar", "xyz"], capture_output=True, text=True,
                          encoding="utf-8", cwd=tmp_path)
    assert ruim.returncode == 2


def test_veredito_conta_na_tabela_e_no_historico(projeto, capsys):
    capsys.readouterr()
    assert mod.main(["veredito", "construir", "--agente", "agente-canvas", "--resultado", "revisao",
                     "--motivo", "faltou o toast de erro"]) == 0
    assert mod.main(["veredito", "construir", "--agente", "agente-canvas", "--resultado", "aceito"]) == 0
    assert mod.main(["veredito", "construir", "--agente", "agente-automate", "--resultado", "aceito"]) == 0
    saida = capsys.readouterr().out
    assert "↻ agente-canvas: revisão — faltou o toast de erro" in saida
    dados = mod.ler_estado(projeto / "ESTADO.md")
    assert dados["etapas"]["construir"]["vereditos"] == {"agente-canvas": {"revisao": 1, "aceito": 1},
                                                         "agente-automate": {"aceito": 1}}
    texto = (projeto / "ESTADO.md").read_text(encoding="utf-8")
    assert "| 2✓ 1↻ |" in texto
    assert "construir · agente-canvas: ↻ revisão — faltou o toast de erro" in texto


def test_veredito_sobrevive_a_reabrir_e_rejeita_resultado_invalido(projeto, capsys):
    mod.main(["veredito", "brainstorm", "--agente", "agente-pesquisa", "--resultado", "escalado"])
    mod.main(["concluir", "brainstorm"])
    mod.main(["reabrir", "brainstorm", "--motivo", "x"])
    assert mod.ler_estado(projeto / "ESTADO.md")["etapas"]["brainstorm"]["vereditos"] == {
        "agente-pesquisa": {"escalado": 1}}
    with pytest.raises(SystemExit):
        mod.main(["veredito", "brainstorm", "--agente", "x", "--resultado", "talvez"])
    assert mod.main(["veredito", "brainstorm", "--agente", "  ", "--resultado", "aceito"]) == 2


def test_vereditos_corrompidos_dao_exit_2(projeto, capsys):
    caminho = projeto / "ESTADO.md"
    texto = caminho.read_text(encoding="utf-8").replace('"argumento": ""', '"argumento": "", "vereditos": {"x": {"talvez": 1}}', 1)
    caminho.write_text(texto, encoding="utf-8")
    assert mod.main(["mostrar"]) == 2


def test_depois_de_publicado_aponta_mudanca_e_mudanca_reabre_homologacao(projeto, capsys):
    for etapa in mod.IDS[1:]:
        assert mod.main(["concluir", etapa]) == 0
    capsys.readouterr()
    mod.main(["proximo"])
    assert "`/pp:mudanca`" in capsys.readouterr().out
    assert mod.main(["reabrir", "homologar", "--motivo", "MUD-001: 3 pedidos"]) == 0
    saida = capsys.readouterr().out
    assert "`/pp:homologar`" in saida
    assert _situacao(projeto, "publicar") == "reaberta" and _situacao(projeto, "testar") == "concluida"
