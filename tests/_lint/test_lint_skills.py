"""Testes do lint do repositório: cada regra tem um caso que passa e um que acusa."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RAIZ_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("lint_skills", RAIZ_REPO / "tools" / "lint_skills.py")
lint = importlib.util.module_from_spec(_spec)
sys.modules["lint_skills"] = lint  # dataclass resolve o módulo por nome
_spec.loader.exec_module(lint)

DESCRICAO_OK = "Use quando precisar validar algo concreto num projeto de teste. Não use para outra coisa (use `x`)."


def _skill(raiz: Path, nome: str, frontmatter: str | None = None, corpo: str = "# Título\n") -> Path:
    pasta = raiz / "skills" / nome
    pasta.mkdir(parents=True)
    fm = frontmatter if frontmatter is not None else f'---\nname: {nome}\ndescription: "{DESCRICAO_OK}"\n---\n'
    (pasta / "SKILL.md").write_text(fm + corpo, encoding="utf-8")
    return pasta


def _repo(tmp_path: Path, versao_plugin: str = "1.0.0", versao_mercado: str = "1.0.0", changelog: bool = True) -> Path:
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "p", "version": versao_plugin}))
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"name": "m", "plugins": [{"name": "p", "source": "./", "version": versao_mercado}]}))
    if changelog:
        (tmp_path / "CHANGELOG.md").write_text(f"## [{versao_plugin}]\n", encoding="utf-8")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "sanitizacao.local.txt").write_text("NOMEINTERNO\n", encoding="utf-8")
    return tmp_path


def _codigos(achados, nivel: str | None = None) -> set[str]:
    return {a.codigo for a in achados if nivel is None or a.nivel == nivel}


def test_skill_conforme_nao_gera_erro(tmp_path):
    raiz = _repo(tmp_path)
    _skill(raiz, "boa")
    assert _codigos(lint.executar([raiz], raiz), "ERRO") == set()


def test_skill_sem_skill_md_acusa_l001(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "skills" / "vazia").mkdir(parents=True)
    assert "L001" in _codigos(lint.executar([raiz], raiz))


@pytest.mark.parametrize("frontmatter, codigo", [
    ("# sem frontmatter\n", "L002"),
    ("---\nname: [quebrado\n---\n", "L002"),
    (f'---\nname: outro-nome\ndescription: "{DESCRICAO_OK}"\n---\n', "L003"),
    ('---\nname: ruim\ndescription: "curta"\n---\n', "L004"),
])
def test_frontmatter_invalido(tmp_path, frontmatter, codigo):
    raiz = _repo(tmp_path)
    _skill(raiz, "ruim", frontmatter=frontmatter)
    assert codigo in _codigos(lint.executar([raiz], raiz), "ERRO")


def test_description_sem_gatilho_e_sem_exclusao_gera_avisos(tmp_path):
    raiz = _repo(tmp_path)
    texto = "Skill que faz várias coisas sobre um assunto qualquer sem dizer quando disparar."
    _skill(raiz, "vaga", frontmatter=f'---\nname: vaga\ndescription: "{texto}"\n---\n')
    assert {"L005", "L006"} <= _codigos(lint.executar([raiz], raiz), "AVISO")


def test_skill_md_longo(tmp_path):
    raiz = _repo(tmp_path)
    _skill(raiz, "media", corpo="x\n" * 300)
    _skill(raiz, "longa", corpo="x\n" * 600)
    achados = lint.executar([raiz], raiz)
    assert any(a.codigo == "L007" and a.nivel == "AVISO" and "media" in a.caminho for a in achados)
    assert any(a.codigo == "L007" and a.nivel == "ERRO" and "longa" in a.caminho for a in achados)


def test_pasta_reference_singular_acusa_l008(tmp_path):
    raiz = _repo(tmp_path)
    (_skill(raiz, "sing") / "reference").mkdir()
    assert "L008" in _codigos(lint.executar([raiz], raiz), "ERRO")


def test_referencia_longa_sem_sumario(tmp_path):
    raiz = _repo(tmp_path)
    refs = _skill(raiz, "refs") / "references"
    refs.mkdir()
    (refs / "sem.md").write_text("# T\n" + "x\n" * 400, encoding="utf-8")
    (refs / "com.md").write_text("# T\n## Sumário\n" + "x\n" * 400, encoding="utf-8")
    (refs / "enorme.md").write_text("# T\n## Sumário\n" + "x\n" * 1100, encoding="utf-8")
    achados = lint.executar([raiz], raiz)
    assert {a.caminho.split("/")[-1] for a in achados if a.codigo == "L009"} == {"sem.md"}
    assert {a.caminho.split("/")[-1] for a in achados if a.codigo == "L010"} == {"enorme.md"}


def test_link_quebrado_acusa_l011_e_link_valido_passa(tmp_path):
    raiz = _repo(tmp_path)
    pasta = _skill(raiz, "links", corpo="Ver [ok](references/ok.md), `references/falta.md` e [web](https://x.y).\n")
    (pasta / "references").mkdir()
    (pasta / "references" / "ok.md").write_text("# ok\n", encoding="utf-8")
    l011 = [a for a in lint.executar([raiz], raiz) if a.codigo == "L011"]
    assert len(l011) == 1 and "falta.md" in l011[0].mensagem


def test_script_com_help_quebrado_acusa_l012_e_sem_teste_l013(tmp_path):
    raiz = _repo(tmp_path)
    scripts = _skill(raiz, "scr") / "scripts"
    scripts.mkdir()
    (scripts / "quebrado.py").write_text("raise SystemExit(3)\n", encoding="utf-8")
    achados = lint.executar([raiz], raiz)
    assert "L012" in _codigos(achados, "ERRO")
    assert "L013" in _codigos(achados, "AVISO")
    assert "L012" not in _codigos(lint.executar([raiz], raiz, executar_scripts=False))


@pytest.mark.parametrize("linha, codigo", [
    ("caminho C:\\Users\\fulano\\x", "S001"),
    ("caminho /c/Users/fulano/x", "S001"),
    ("pasta OneDrive/Projetos", "S001"),
    ("pasta D:\OneDrive\Projetos", "S001"),
    ("pasta OneDrive - Contoso", "S001"),
    ("fale com fulano@empresa.com.br", "S002"),
    ("id 3f2b8c1e-1a2b-4c3d-9e8f-0a1b2c3d4e5f", "S003"),
    ("servidor NOMEINTERNO01", "S004"),
])
def test_sanitizacao_acusa(tmp_path, linha, codigo):
    raiz = _repo(tmp_path)
    _skill(raiz, "san", corpo=linha + "\n")
    assert codigo in _codigos(lint.executar([raiz], raiz), "ERRO")


@pytest.mark.parametrize("linha", [
    "usuario@contoso.com é fictício",
    "Control: Classic/Button@2.2.0",
    "id 00000000-0000-0000-0000-000000000001",
    "C:\\Users\\x citado de propósito  <!-- lint-ok -->",
    "@{outputs('Compose')?['body']}",
    "\"connectionName\": \"shared_onedriveforbusiness\"",
    "conector OneDrive for Business",
    "\"<prefixo>_Pedido@odata.bind\": \"/pedidos(1)\"",
    "@odata.nextLink e x@odata.etag",
])
def test_sanitizacao_nao_acusa_ficticio_nem_isento(tmp_path, linha):
    raiz = _repo(tmp_path)
    _skill(raiz, "limpa", corpo=linha + "\n")
    assert not {"S001", "S002", "S003"} & _codigos(lint.executar([raiz], raiz))


def test_arquivo_local_de_sanitizacao_e_ignorado_na_varredura(tmp_path):
    raiz = _repo(tmp_path)
    _skill(raiz, "x")
    assert "S004" not in _codigos(lint.executar([raiz], raiz))


def test_sem_arquivo_local_avisa_s000(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "tools" / "sanitizacao.local.txt").unlink()
    _skill(raiz, "x")
    assert "S000" in _codigos(lint.executar([raiz], raiz), "AVISO")


def test_versoes_divergentes_acusam_r001_e_changelog_r002(tmp_path):
    raiz = _repo(tmp_path, versao_plugin="1.1.0", versao_mercado="1.0.0", changelog=False)
    _skill(raiz, "x")
    achados = lint.executar([raiz], raiz)
    assert "R001" in _codigos(achados, "ERRO")
    assert "R002" in _codigos(achados, "AVISO")


def test_main_exit_codes(tmp_path, capsys):
    raiz = _repo(tmp_path)
    _skill(raiz, "ok")
    assert lint.main(["--raiz", str(raiz), "--sem-scripts"]) == 0
    _skill(raiz, "suja", corpo="e-mail fulano@empresa.com\n")
    assert lint.main(["--raiz", str(raiz), "--sem-scripts"]) == 1
    assert lint.main(["--raiz", str(raiz), str(raiz / "nao-existe")]) == 2
    saida = capsys.readouterr().out
    assert "erro(s)" in saida and "aviso(s)" in saida


def _mapa(raiz: Path, arquivos: dict[str, tuple[str, str]]) -> None:
    (raiz / "i18n").mkdir(exist_ok=True)
    corpo = {"arquivos": {pt: {"en": en, "situacao": sit} for pt, (en, sit) in arquivos.items()}}
    (raiz / "i18n" / "mapa.json").write_text(json.dumps(corpo, indent=2), encoding="utf-8")


def _l014(achados, nivel: str) -> list:
    return [a for a in achados if a.codigo == "L014" and a.nivel == nivel]


def test_i18n_arquivo_pt_br_sem_entrada_no_mapa_e_erro(tmp_path):
    raiz = _repo(tmp_path)
    _skill(raiz, "mapeada")
    _skill(raiz, "esquecida")
    (raiz / "agents").mkdir()
    (raiz / "agents" / "agente-x.md").write_text("# x\n", encoding="utf-8")
    _mapa(raiz, {"skills/mapeada/SKILL.md": ("en/skills/mapped/SKILL.md", "pendente")})
    erros = _l014(lint.executar([raiz], raiz), "ERRO")
    assert {a.caminho for a in erros} == {"skills/esquecida/SKILL.md", "agents/agente-x.md"}


def test_i18n_feito_sem_arquivo_en_e_erro_e_com_arquivo_passa(tmp_path):
    raiz = _repo(tmp_path)
    _skill(raiz, "a")
    _skill(raiz, "b")
    (raiz / "en" / "skills" / "b-en").mkdir(parents=True)
    (raiz / "en" / "skills" / "b-en" / "SKILL.md").write_text("# b\n", encoding="utf-8")
    _mapa(raiz, {"skills/a/SKILL.md": ("en/skills/a-en/SKILL.md", "feito"),
                 "skills/b/SKILL.md": ("en/skills/b-en/SKILL.md", "feito")})
    erros = _l014(lint.executar([raiz], raiz), "ERRO")
    assert len(erros) == 1 and "en/skills/a-en/SKILL.md" in erros[0].mensagem
    assert erros[0].caminho == "i18n/mapa.json" and erros[0].linha > 1


def test_i18n_feito_com_parametro_de_idioma_confere_o_arquivo_sem_parametro(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "docs").mkdir()
    (raiz / "docs" / "d.html").write_text("<p>x</p>", encoding="utf-8")
    _mapa(raiz, {"docs/d.html": ("docs/d.html?lang=en", "feito")})
    assert not _l014(lint.executar([raiz], raiz), "ERRO")


def test_i18n_pendente_e_aviso_e_main_imprime_a_contagem(tmp_path, capsys):
    raiz = _repo(tmp_path)
    _skill(raiz, "um")
    _skill(raiz, "dois")
    _mapa(raiz, {"skills/um/SKILL.md": ("en/skills/one/SKILL.md", "pendente"),
                 "skills/dois/SKILL.md": ("en/skills/two/SKILL.md", "pendente")})
    achados = lint.executar([raiz], raiz)
    assert not _l014(achados, "ERRO") and len(_l014(achados, "AVISO")) == 2
    assert lint.main(["--raiz", str(raiz), "--sem-scripts"]) == 0
    linhas = capsys.readouterr().out.strip().splitlines()
    assert linhas[-2:] == ["2 pendente(s) de tradução", "0 erro(s), 2 aviso(s)"]


@pytest.mark.parametrize("conteudo, trecho", [
    ('{"arquivos": [', "ilegível"),
    ('{"outro": {}}', "ilegível"),
    ('{"arquivos": {"skills/x/SKILL.md": {"en": "en/x.md", "situacao": "talvez"}}}', "situacao"),
    ('{"arquivos": {"skills/sumiu/SKILL.md": {"en": "en/s.md", "situacao": "pendente"}}}', "não existe"),
])
def test_i18n_mapa_invalido_ou_orfao_e_erro(tmp_path, conteudo, trecho):
    raiz = _repo(tmp_path)
    _skill(raiz, "x")
    (raiz / "i18n").mkdir()
    (raiz / "i18n" / "mapa.json").write_text(conteudo, encoding="utf-8")
    erros = _l014(lint.executar([raiz], raiz), "ERRO")
    assert any(trecho in a.mensagem for a in erros)


@pytest.mark.parametrize("en, trecho", [
    ("skills/x/SKILL.md", "próprio arquivo pt-BR"),
    ("../fora/SKILL.md", "sai do repositório"),
    ("/abs/SKILL.md", "sai do repositório"),
    ("C:/abs/SKILL.md", "sai do repositório"),
])
def test_i18n_destino_en_invalido_e_erro(tmp_path, en, trecho):
    raiz = _repo(tmp_path)
    _skill(raiz, "x")
    _mapa(raiz, {"skills/x/SKILL.md": (en, "feito")})
    assert any(trecho in a.mensagem for a in _l014(lint.executar([raiz], raiz), "ERRO"))


def test_i18n_ignora_lixo_do_sistema_e_ocultos(tmp_path):
    raiz = _repo(tmp_path)
    pasta = _skill(raiz, "x")
    for nome in ("Thumbs.db", "desktop.ini", ".DS_Store"):
        (pasta / nome).write_text("", encoding="utf-8")
    _mapa(raiz, {"skills/x/SKILL.md": ("en/skills/x/SKILL.md", "pendente")})
    assert not _l014(lint.executar([raiz], raiz), "ERRO")


def test_i18n_mapa_ilegivel_nao_imprime_contagem(tmp_path, capsys):
    raiz = _repo(tmp_path)
    _skill(raiz, "x")
    (raiz / "i18n").mkdir()
    (raiz / "i18n" / "mapa.json").write_text("{", encoding="utf-8")
    assert lint.main(["--raiz", str(raiz), "--sem-scripts"]) == 1
    assert "pendente(s)" not in capsys.readouterr().out


def test_i18n_sem_mapa_so_acusa_quando_existe_en(tmp_path, capsys):
    raiz = _repo(tmp_path)
    _skill(raiz, "x")
    assert not _l014(lint.executar([raiz], raiz), "ERRO")
    lint.main(["--raiz", str(raiz), "--sem-scripts"])
    assert "pendente(s)" not in capsys.readouterr().out
    (raiz / "en").mkdir()
    assert _l014(lint.executar([raiz], raiz), "ERRO")


def test_alvo_skill_unica_checa_so_ela(tmp_path):
    raiz = _repo(tmp_path)
    alvo = _skill(raiz, "alvo")
    _skill(raiz, "outra", frontmatter="# sem frontmatter\n")
    achados = lint.executar([alvo.resolve()], raiz)
    assert not any("outra" in a.caminho for a in achados)
