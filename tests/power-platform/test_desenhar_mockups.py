"""Testes de `skills/power-platform/scripts/desenhar-mockups.py` (sem rede: a chamada HTTP é falsa)."""
import base64
import importlib.util
import io
import json
import os
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "desenhar-mockups.py"
MOLDE = RAIZ / "skills" / "power-platform" / "assets" / "mockups-molde.json"
CHAVE = "sk-teste-nao-real-123"
PNG = b"\x89PNG\r\n\x1a\nfalso"


def _carregar():
    spec = importlib.util.spec_from_file_location("desenhar_mockups", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["desenhar_mockups"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def _spec(**sobre):
    base = {
        "app": "Pedidos",
        "idioma": "pt-BR",
        "canvas": "1920x1080",
        "design_system": {
            "paleta": {"primaria": "#0F6CBD", "fundo": "#F5F5F5", "texto": "#242424"},
            "fonte": "Segoe UI",
            "raio": 4,
            "estilo": "Fluent 2, corporativo",
        },
        "moldura": {
            "header": "faixa superior na cor primária com nome do app e usuário",
            "navegacao": "menu lateral recolhível",
            "notificacoes": "toast no canto superior direito",
            "popups": "modal centralizado com fundo escurecido",
        },
        "telas": [
            {"id": "tl-01-lista", "nome": "Lista de pedidos", "descricao": "galeria em tabela com filtros",
             "componentes": ["cabecalho-tela", "galeria-tabela"], "estado": "com dados"},
            {"id": "tl-01-confirmar", "nome": "Lista de pedidos", "descricao": "lista com modal aberto",
             "estado": "modal de confirmação aberto"},
            {"id": "tl-02-novo", "nome": "Novo pedido", "descricao": "formulário de inclusão"},
        ],
    }
    base.update(sobre)
    return base


@pytest.fixture
def projeto(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for var in ("OPENAI_API_KEY", "OPENAI_IMAGE_MODEL", "OPENAI_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    pasta = tmp_path / "docs" / "planejamento" / "mockups"
    pasta.mkdir(parents=True)
    return pasta


def _gravar(pasta, spec):
    caminho = pasta / "mockups.json"
    caminho.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return caminho


class _Resposta:
    def __init__(self, corpo):
        self._corpo = json.dumps(corpo).encode("utf-8")

    def read(self, limite=-1):
        return self._corpo

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def api(monkeypatch):
    chamadas = []

    def falsa(req, timeout):
        chamadas.append({"url": req.full_url, "headers": dict(req.header_items()),
                         "body": json.loads(req.data.decode("utf-8")), "timeout": timeout})
        return _Resposta({"data": [{"b64_json": base64.b64encode(PNG).decode("ascii")}]})

    monkeypatch.setattr(mod, "_urlopen", falsa)
    return chamadas


def _proibir_rede(monkeypatch):
    def falsa(req, timeout):
        raise AssertionError("não devia chamar a API")
    monkeypatch.setattr(mod, "_urlopen", falsa)


def test_help_funciona():
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "OPENAI_API_KEY" in r.stdout and "OPENAI_IMAGE_MODEL" in r.stdout


def test_simular_valida_sem_chave_e_sem_rede(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _gravar(projeto, _spec())
    assert mod.main([str(spec), "--simular"]) == 0
    out = capsys.readouterr().out
    assert "modelo: gpt-image-2" in out and "tamanho: 1536x1024" in out and "qualidade: high" in out
    assert "3 imagem(ns) nova(s)" in out
    assert "#0F6CBD" in out and "pt-BR" in out and "faixa superior na cor primária" in out
    assert out.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"
    assert not list(projeto.glob("*.png"))


@pytest.mark.parametrize("cli,env,cfg,esperado", [
    (None, None, None, "gpt-image-2"),
    (None, None, "modelo-config", "modelo-config"),
    (None, "modelo-env", "modelo-config", "modelo-env"),
    ("modelo-cli", "modelo-env", "modelo-config", "modelo-cli"),
])
def test_precedencia_do_modelo(projeto, monkeypatch, capsys, cli, env, cfg, esperado):
    _proibir_rede(monkeypatch)
    if cfg:
        Path("power-platform.config.json").write_text(json.dumps({"mockups": {"modelo": cfg}}), encoding="utf-8")
    if env:
        monkeypatch.setenv("OPENAI_IMAGE_MODEL", env)
    args = [str(_gravar(projeto, _spec())), "--simular"] + (["--modelo", cli] if cli else [])
    assert mod.main(args) == 0
    assert f"modelo: {esperado}" in capsys.readouterr().out


def test_tamanho_e_qualidade_do_config(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    Path("power-platform.config.json").write_text(
        json.dumps({"mockups": {"tamanho": "1024x1024", "qualidade": "medium"}}), encoding="utf-8")
    assert mod.main([str(_gravar(projeto, _spec())), "--simular"]) == 0
    out = capsys.readouterr().out
    assert "tamanho: 1024x1024" in out and "qualidade: medium" in out


def test_cor_fora_do_formato_acusa_m003(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _spec()
    spec["design_system"]["paleta"]["primaria"] = "azul"
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert "ERRO M003" in capsys.readouterr().out


def test_id_duplicado_ou_invalido_acusa_m004(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _spec()
    spec["telas"][1]["id"] = "tl-01-lista"
    spec["telas"][2]["id"] = "Tela Nova"
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert capsys.readouterr().out.count("ERRO M004") == 2


@pytest.mark.parametrize("remover", ["app", "moldura", "telas"])
def test_campo_obrigatorio_ausente_acusa_m002(projeto, monkeypatch, capsys, remover):
    _proibir_rede(monkeypatch)
    spec = _spec()
    del spec[remover]
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert "ERRO M002" in capsys.readouterr().out


def test_tela_sem_descricao_acusa_m002(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _spec()
    del spec["telas"][0]["descricao"]
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert "tl-01-lista" in capsys.readouterr().out


def test_email_real_no_spec_acusa_m006(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _spec()
    spec["telas"][0]["descricao"] = "mostra o solicitante fulano@empresa.com.br"  # lint-ok: caso do M006
    spec["telas"][1]["descricao"] = "mostra usuario@contoso.com"
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert capsys.readouterr().out.count("ERRO M006") == 1


@pytest.mark.parametrize("tamanho,nivel", [
    ("1000x1000", "ERRO"),   # não é múltiplo de 16
    ("3840x1024", "ERRO"),   # proporção acima de 3:1
    ("abc", "ERRO"),
    ("1920x1088", "AVISO"),  # personalizado: depende do modelo
])
def test_tamanho_validado_m005(projeto, monkeypatch, capsys, tamanho, nivel):
    _proibir_rede(monkeypatch)
    codigo = mod.main([str(_gravar(projeto, _spec())), "--simular", "--tamanho", tamanho])
    out = capsys.readouterr().out
    assert f"{nivel} M005" in out
    assert codigo == (1 if nivel == "ERRO" else 0)


def test_sem_chave_sai_2_e_explica(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    assert mod.main([str(_gravar(projeto, _spec()))]) == 2
    assert "OPENAI_API_KEY" in capsys.readouterr().err


def test_gera_png_e_galeria_sem_vazar_chave(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    assert mod.main([str(_gravar(projeto, _spec()))]) == 0
    assert len(api) == 3
    primeira = api[0]
    assert primeira["url"] == "https://api.openai.com/v1/images/generations"
    assert primeira["headers"]["Authorization"] == f"Bearer {CHAVE}"
    corpo = primeira["body"]
    assert corpo["model"] == "gpt-image-2" and corpo["size"] == "1536x1024" and corpo["quality"] == "high"
    assert corpo["n"] == 1 and "#0F6CBD" in corpo["prompt"] and "Lista de pedidos" in corpo["prompt"]
    assert (projeto / "tl-01-lista.png").read_bytes() == PNG
    galeria = (projeto / "mockups.md").read_text(encoding="utf-8")
    assert "gerado — não editar" in galeria and "![Novo pedido](tl-02-novo.png)" in galeria
    saida = capsys.readouterr()
    assert CHAVE not in saida.out + saida.err


def test_pula_imagem_existente_e_sobrescreve_quando_pedido(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    spec = _gravar(projeto, _spec())
    (projeto / "tl-01-lista.png").write_bytes(b"antiga")
    assert mod.main([str(spec)]) == 0
    assert len(api) == 2 and (projeto / "tl-01-lista.png").read_bytes() == b"antiga"
    assert mod.main([str(spec), "--sobrescrever", "--telas", "tl-01-lista"]) == 0
    assert len(api) == 3 and (projeto / "tl-01-lista.png").read_bytes() == PNG


def test_filtro_de_telas_e_tela_inexistente(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    spec = _gravar(projeto, _spec())
    assert mod.main([str(spec), "--telas", "tl-02-novo"]) == 0
    assert len(api) == 1 and (projeto / "tl-02-novo.png").exists()
    assert mod.main([str(spec), "--telas", "tl-99"]) == 2


def test_teto_de_imagens_por_execucao(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    assert mod.main([str(_gravar(projeto, _spec())), "--max-imagens", "2"]) == 2
    assert not api and "--max-imagens" in capsys.readouterr().err


def test_base_url_do_ambiente(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://proxy.contoso.com/openai/v1/")
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-01-lista"]) == 0
    assert api[0]["url"] == "https://proxy.contoso.com/openai/v1/images/generations"


def test_http_401_aborta_e_nao_vaza_chave(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    chamadas = []

    def falsa(req, timeout):
        chamadas.append(1)
        corpo = io.BytesIO(json.dumps({"error": {"message": f"Incorrect API key provided: {CHAVE}"}}).encode())
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, corpo)

    monkeypatch.setattr(mod, "_urlopen", falsa)
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    saida = capsys.readouterr()
    assert len(chamadas) == 1
    assert "ERRO M101" in saida.out and "HTTP 401" in saida.out
    assert CHAVE not in saida.out + saida.err


def test_resposta_sem_imagem_acusa_m102(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    monkeypatch.setattr(mod, "_urlopen", lambda req, timeout: _Resposta({"data": [{}]}))
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-02-novo"]) == 1
    assert "ERRO M102" in capsys.readouterr().out


def test_spec_inexistente_sai_2(projeto, capsys):
    assert mod.main(["nao-existe.json", "--simular"]) == 2


def test_json_quebrado_acusa_m001(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    caminho = projeto / "mockups.json"
    caminho.write_text("{ quebrado", encoding="utf-8")
    assert mod.main([str(caminho), "--simular"]) == 1
    assert "ERRO M001" in capsys.readouterr().out


def test_molde_do_kit_e_valido(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    assert mod.main([str(MOLDE), "--simular"]) == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines()[-1] == "0 erro(s), 0 aviso(s)"


# ---------- robustez (revisão de código) ----------

OK = {"data": [{"b64_json": base64.b64encode(PNG).decode("ascii")}]}


def _http_erro(req, codigo, mensagem="falhou", cabecalhos=None):
    corpo = io.BytesIO(json.dumps({"error": {"message": mensagem}}).encode())
    return urllib.error.HTTPError(req.full_url, codigo, "erro", cabecalhos or {}, corpo)


def _api_roteiro(monkeypatch, roteiro):
    """Cada item: dict de resposta, exceção pronta ou função req -> exceção. O último se repete."""
    chamadas = []

    def falsa(req, timeout):
        item = roteiro[min(len(chamadas), len(roteiro) - 1)]
        chamadas.append(req)
        if callable(item):
            raise item(req)
        if isinstance(item, BaseException):
            raise item
        return _Resposta(item)

    monkeypatch.setattr(mod, "_urlopen", falsa)
    monkeypatch.setattr(mod, "_dormir", lambda segundos: None)
    return chamadas


def test_urlerror_aborta_e_ainda_escreve_galeria(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    chamadas = _api_roteiro(monkeypatch, [OK, urllib.error.URLError("sem rota")])
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    assert len(chamadas) == 2
    assert "ERRO M101" in capsys.readouterr().out
    assert "tl-01-lista.png" in (projeto / "mockups.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("excecao", [TimeoutError("lento"), ConnectionResetError("caiu")])
def test_erro_de_rede_na_leitura_vira_m101(projeto, monkeypatch, capsys, excecao):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    _api_roteiro(monkeypatch, [excecao])
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    assert "ERRO M101" in capsys.readouterr().out


class _Bruta(_Resposta):
    def __init__(self, texto):
        self._corpo = texto.encode("utf-8")


@pytest.mark.parametrize("resposta", [
    _Bruta("<html>proxy</html>"),
    _Resposta({"data": [{"b64_json": base64.b64encode(b"lixo").decode()}]}),
    _Resposta({"data": [{"url": "https://exemplo.com/img.png"}]}),
])
def test_resposta_que_nao_e_png_vira_m102(projeto, monkeypatch, capsys, resposta):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    monkeypatch.setattr(mod, "_urlopen", lambda req, timeout: resposta)
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-02-novo"]) == 1
    assert "ERRO M102" in capsys.readouterr().out
    assert not (projeto / "tl-02-novo.png").exists()


@pytest.mark.parametrize("codigo", [400, 403, 404])
def test_erro_que_se_repete_em_toda_tela_aborta(projeto, monkeypatch, capsys, codigo):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    chamadas = _api_roteiro(monkeypatch, [OK, lambda req: _http_erro(req, codigo)])
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    assert len(chamadas) == 2
    galeria = (projeto / "mockups.md").read_text(encoding="utf-8")
    assert "tl-01-lista.png" in galeria and "tl-02-novo.png" not in galeria


def test_429_e_5xx_tentam_de_novo_e_seguem(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    chamadas = _api_roteiro(monkeypatch, [lambda req: _http_erro(req, 429, cabecalhos={"Retry-After": "1"}),
                                          lambda req: _http_erro(req, 503), OK])
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-01-lista"]) == 0
    assert len(chamadas) == 3 and (projeto / "tl-01-lista.png").exists()


def test_429_persistente_aborta(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    chamadas = _api_roteiro(monkeypatch, [lambda req: _http_erro(req, 429)])
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    assert len(chamadas) == 1 + mod.TENTATIVAS_EXTRAS


def test_falha_ao_gravar_vira_m103_sem_png_truncado(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    _api_roteiro(monkeypatch, [OK])

    def bloqueado(origem, destino):
        raise OSError("arquivo bloqueado")

    monkeypatch.setattr(mod.os, "replace", bloqueado)
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-01-lista"]) == 1
    assert "ERRO M103" in capsys.readouterr().out
    assert not (projeto / "tl-01-lista.png").exists()


@pytest.mark.parametrize("ident", ["tl-01\n", "con", "nul", "com1", "lpt9"])
def test_id_com_quebra_ou_reservado_do_windows_acusa_m004(projeto, monkeypatch, capsys, ident):
    _proibir_rede(monkeypatch)
    spec = _spec()
    spec["telas"][0]["id"] = ident
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert "ERRO M004" in capsys.readouterr().out


def test_cor_com_quebra_de_linha_acusa_m003(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _spec()
    spec["design_system"]["paleta"]["primaria"] = "#0F6CBD\n"
    assert mod.main([str(_gravar(projeto, spec)), "--simular"]) == 1
    assert "ERRO M003" in capsys.readouterr().out


def test_chave_com_caractere_de_controle_sai_2_sem_vazar(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-parte1\x0bparte2")
    assert mod.main([str(_gravar(projeto, _spec()))]) == 2
    saida = capsys.readouterr()
    assert "parte1" not in saida.out + saida.err and "OPENAI_API_KEY" in saida.err


@pytest.mark.parametrize("url,codigo", [
    ("http://proxy.contoso.com/v1", 2),
    ("http://localhost:8080/v1", 0),
    ("ftp://contoso.com", 2),
])
def test_base_url_exige_https_fora_do_localhost(projeto, monkeypatch, capsys, api, url, codigo):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    monkeypatch.setenv("OPENAI_BASE_URL", url)
    assert mod.main([str(_gravar(projeto, _spec())), "--telas", "tl-01-lista"]) == codigo


def test_redirecionamento_nao_e_seguido():
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=b"{}", method="POST")
    assert mod._SemRedirecionar().redirect_request(req, None, 302, "Found", {}, "https://outro.contoso.com") is None


def test_mensagem_http_redige_chave_e_controles(projeto, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    _api_roteiro(monkeypatch, [lambda req: _http_erro(req, 401, "eco Bearer sk-outra-chave-999\nERRO falso")])
    assert mod.main([str(_gravar(projeto, _spec()))]) == 1
    out = capsys.readouterr().out
    assert "sk-outra-chave-999" not in out and "\nERRO falso" not in out


@pytest.mark.parametrize("config", [[1, 2], {"mockups": {"modelo": 5}}, {"mockups": {"pasta": ["x"]}}])
def test_config_mal_formado_sai_2(projeto, monkeypatch, capsys, config):
    _proibir_rede(monkeypatch)
    Path("power-platform.config.json").write_text(json.dumps(config), encoding="utf-8")
    assert mod.main([str(_gravar(projeto, _spec())), "--simular"]) == 2


@pytest.mark.parametrize("extra", [["--max-imagens", "0"], ["--timeout", "0"], ["--telas", ","]])
def test_argumentos_invalidos_saem_2(projeto, monkeypatch, capsys, extra):
    _proibir_rede(monkeypatch)
    assert mod.main([str(_gravar(projeto, _spec())), "--simular", *extra]) == 2


def test_spec_em_ansi_vira_m001(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    caminho = projeto / "mockups.json"
    caminho.write_bytes(json.dumps(_spec(), ensure_ascii=False).encode("cp1252"))
    assert mod.main([str(caminho), "--simular"]) == 1
    assert "ERRO M001" in capsys.readouterr().out


def test_qualidade_invalida_m007_e_tamanho_auto(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    spec = _gravar(projeto, _spec())
    assert mod.main([str(spec), "--simular", "--qualidade", "ultra"]) == 1
    assert "ERRO M007" in capsys.readouterr().out
    assert mod.main([str(spec), "--simular", "--tamanho", "auto"]) == 0


def test_precedencia_de_tamanho_e_qualidade(projeto, monkeypatch, capsys):
    _proibir_rede(monkeypatch)
    Path("power-platform.config.json").write_text(
        json.dumps({"mockups": {"tamanho": "1024x1024", "qualidade": "medium"}}), encoding="utf-8")
    args = [str(_gravar(projeto, _spec())), "--simular", "--tamanho", "1024x1536", "--qualidade", "low"]
    assert mod.main(args) == 0
    out = capsys.readouterr().out
    assert "tamanho: 1024x1536" in out and "qualidade: low" in out


def test_galeria_aguenta_crases_e_avisa_que_imagem_pode_ser_anterior(projeto, monkeypatch, capsys, api):
    monkeypatch.setenv("OPENAI_API_KEY", CHAVE)
    spec = _spec()
    spec["telas"][0]["descricao"] = "mostra o código ```x``` na tela"
    assert mod.main([str(_gravar(projeto, spec)), "--telas", "tl-01-lista"]) == 0
    galeria = (projeto / "mockups.md").read_text(encoding="utf-8")
    assert "````text" in galeria and "a imagem pode ser anterior" in galeria
    assert CHAVE not in galeria


def test_simular_redirecionado_sai_em_utf8(tmp_path):
    spec = tmp_path / "mockups.json"
    dados = _spec()
    dados["telas"][0]["descricao"] = "seta → e acento ção"
    spec.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
    env["PYTHONIOENCODING"] = "cp1252"
    r = subprocess.run([sys.executable, str(SCRIPT), str(spec), "--simular"], capture_output=True, env=env, cwd=tmp_path)
    assert r.returncode == 0
    assert "seta → e acento ção" in r.stdout.decode("utf-8")
