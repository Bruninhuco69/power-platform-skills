"""Testes do `montar-carga-mockup.py --flow`: o plano do construtor Dataverse e o pacote do flow (sem rede)."""
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPT = RAIZ / "skills" / "power-platform" / "scripts" / "montar-carga-mockup.py"
VERIFICAR = RAIZ / "skills" / "power-automate" / "scripts" / "verificar-fluxo.py"
MOLDE = RAIZ / "skills" / "power-platform" / "assets" / "carga-mockup-molde.json"
FLUXO = RAIZ / "skills" / "power-platform" / "assets" / "construtor-dataverse.json"
AMBIENTE = {"{{prefixo}}": "abc", "{{opcao}}": "12345", "{{idioma}}": "1046"}
CRLF = chr(13) + chr(10)
LF = chr(10)
ZIP = "ConstrutorDataverse_1_0_0_0.zip"


# ---------- apoio ----------

def rodar(*args, cwd: Path, script: Path = SCRIPT):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=cwd, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    return r.returncode, r.stdout + r.stderr


def codigos(saida: str) -> list[str]:
    return re.findall(r": (?:ERRO|AVISO) (C[0-9]{3}) ", saida)


def erros(saida: str) -> list[str]:
    return re.findall(r": ERRO (C[0-9]{3}) ", saida)


def gerar(pasta: Path, spec=None, *extra):
    caminho = MOLDE
    if spec is not None:
        caminho = pasta / "carga-mockup.json"
        caminho.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return rodar(caminho, "--trilha", "dataverse", "--flow", "--saida", pasta / "out", *extra, cwd=pasta)


def texto_do_plano(pasta: Path) -> str:
    return (pasta / "out" / "plano-dataverse.json").read_text(encoding="utf-8")


def plano(pasta: Path) -> dict:
    """O plano como o flow o lê: marcadores do ambiente trocados antes do json()."""
    texto = texto_do_plano(pasta)
    for marca, valor in AMBIENTE.items():
        texto = texto.replace(marca, valor)
    return json.loads(texto)


def passo(p: dict, fase: str, rotulo: str) -> dict:
    return next(s for s in p["passos"] if s["fase"] == fase and s["rotulo"] == rotulo)


def corpo(s: dict) -> dict:
    return json.loads(s["corpo"])


def rotulo(label: dict) -> tuple[str, int]:
    item = label["LocalizedLabels"][0]
    return item["Label"], item["LanguageCode"]


def partes_do_lote(s: dict) -> list[tuple[list[str], dict]]:
    """[(cabeçalhos e linha de pedido, corpo JSON)] de cada parte do changeset."""
    fronteira = s["tipo"].split("boundary=")[1]
    texto = s["corpo"]
    linhas = texto.split(CRLF)
    assert linhas[0] == f"--{fronteira}"
    changeset = linhas[1].split("boundary=")[1]
    blocos = texto.split(f"--{changeset}{CRLF}")[1:]
    saida = []
    for bloco in blocos:
        bloco = bloco.split(f"--{changeset}--")[0]
        cabeca, _, resto = bloco.partition(CRLF + CRLF)
        pedido, _, json_parte = resto.partition(CRLF + CRLF)
        saida.append((cabeca.split(CRLF) + pedido.split(CRLF), json.loads(json_parte.strip())))
    return saida


def _spec_tipos() -> dict:
    return {"linhas": 3, "tabelas": [{"nome": "Item", "colunas": [
        {"nome": "Nome", "tipo": "texto", "primaria": True},
        {"nome": "Código", "tipo": "codigo", "tamanho": 10},
        {"nome": "Detalhe", "tipo": "texto_longo"},
        {"nome": "Quantidade", "tipo": "inteiro"},
        {"nome": "Peso", "tipo": "decimal", "casas": 3},
        {"nome": "Preço", "tipo": "moeda"},
        {"nome": "Entrega", "tipo": "data"},
        {"nome": "Registro", "tipo": "data_hora"},
        {"nome": "Ativo", "tipo": "sim_nao"},
        {"nome": "Situação", "tipo": "choice", "opcoes": ["Nova", "Usada", "Avariada"]},
        {"nome": "Cores", "tipo": "escolhas", "opcoes": ["Azul", "Verde"]},
        {"nome": "Contato", "tipo": "email"},
        {"nome": "Telefone", "tipo": "telefone"},
        {"nome": "Site", "tipo": "url"},
        {"nome": "Número", "tipo": "autonumero"},
        {"nome": "Foto", "tipo": "imagem"},
        {"nome": "Anexo", "tipo": "arquivo"},
    ]}]}


def _spec_auto(**coluna) -> dict:
    return {"linhas": 3, "tabelas": [{"nome": "Setor", "colunas": [
        {"nome": "Nome", "tipo": "texto", "primaria": True, "exemplos": ["A", "B", "C"]},
        {"nome": "Setor pai", "tipo": "lookup", "alvo": "Setor", **coluna},
    ]}]}


# ---------- molde ----------

def test_molde_gera_plano_e_construtor_sem_erro(tmp_path):
    codigo, saida = gerar(tmp_path)
    assert codigo == 0, saida
    assert "0 erro(s)" in saida
    out = tmp_path / "out"
    for arquivo in ("carga-mockup.xlsx", "plano-dataverse.json", f"construtor-dataverse/{ZIP}",
                    "construtor-dataverse/construtor-escopo.json"):
        assert (out / arquivo).is_file(), arquivo
    achados = codigos(saida)
    assert "C018" in achados
    assert not {"C011", "C013", "C014"} & set(achados), "aviso da importação por planilha não vale para o construtor"


def test_passos_seguem_as_fases_na_ordem(tmp_path):
    gerar(tmp_path)
    p = plano(tmp_path)
    fases = [s["fase"] for s in p["passos"]]
    ordem = ["tabela", "coluna", "relacionamento", "publicar", "dados", "chave"]
    assert sorted(fases, key=ordem.index) == fases
    assert fases.count("tabela") == 2 and fases.count("publicar") == 1 and fases.count("dados") == 2
    assert [s["n"] for s in p["passos"]] == list(range(1, len(fases) + 1))
    assert [s["rotulo"] for s in p["passos"] if s["fase"] == "tabela"] == ["Unidade", "Pedido"]
    assert p["formato"] == "plano-dataverse/1"
    assert p["resumo"]["tabelas"] == 2 and p["resumo"]["linhas"] == 13


def test_so_os_marcadores_que_o_flow_troca(tmp_path):
    gerar(tmp_path)
    marcas = set(re.findall(r"[{][{]([a-z]+)[}][}]", texto_do_plano(tmp_path)))
    assert marcas == {"prefixo", "opcao", "idioma"}
    troca = json.dumps(json.loads(FLUXO.read_text(encoding="utf-8")), ensure_ascii=False)
    for marca in AMBIENTE:
        assert f"'{marca}'" in troca, f"o flow não troca {marca}"


def test_todo_pedido_tem_url_relativa_sem_espaco_e_corpo_valido(tmp_path):
    gerar(tmp_path)
    for s in plano(tmp_path)["passos"]:
        assert s["metodo"] == "POST"
        assert s["url"].startswith("/api/data/v9.2/")
        assert " " not in s["url"] + s["existe"]
        if s["fase"] != "dados":
            assert s["tipo"].startswith("application/json")
            corpo(s)
        assert s["corpo"].isascii(), "acento vai escapado: o corpo não depende da codificação do conector"


def test_tabela_nasce_com_a_primaria_o_conjunto_e_os_rotulos(tmp_path):
    gerar(tmp_path)
    s = passo(plano(tmp_path), "tabela", "Unidade")
    c = corpo(s)
    assert s["url"] == "/api/data/v9.2/EntityDefinitions"
    assert "LogicalName%20eq%20'abc_unidade'" in s["existe"]
    assert c["@odata.type"] == "Microsoft.Dynamics.CRM.EntityMetadata"
    assert c["SchemaName"] == "abc_Unidade" and c["EntitySetName"] == "abc_unidades"
    assert rotulo(c["DisplayName"]) == ("Unidade", 1046)
    assert rotulo(c["DisplayCollectionName"])[0] == "Unidades"
    assert c["OwnershipType"] == "UserOwned" and c["HasNotes"] is False
    primaria, = c["Attributes"]
    assert primaria["IsPrimaryName"] is True and primaria["SchemaName"] == "abc_Nome"
    assert primaria["FormatName"] == {"Value": "Text"} and primaria["MaxLength"] == 100
    assert primaria["RequiredLevel"]["Value"] == "ApplicationRequired"
    assert not any(x["fase"] == "coluna" and x["rotulo"] == "Unidade.Nome" for x in plano(tmp_path)["passos"])


TIPOS_ESPERADOS = {
    "Código": ("StringAttributeMetadata", {"MaxLength": 10, "FormatName": {"Value": "Text"}}),
    "Detalhe": ("MemoAttributeMetadata", {"MaxLength": 2000, "Format": "TextArea"}),
    "Quantidade": ("IntegerAttributeMetadata", {"Format": "None", "MaxValue": 2147483647}),
    "Peso": ("DecimalAttributeMetadata", {"Precision": 3}),
    "Preço": ("MoneyAttributeMetadata", {"Precision": 2, "PrecisionSource": 0}),
    "Entrega": ("DateTimeAttributeMetadata", {"Format": "DateOnly", "DateTimeBehavior": {"Value": "DateOnly"}}),
    "Registro": ("DateTimeAttributeMetadata", {"Format": "DateAndTime", "DateTimeBehavior": {"Value": "UserLocal"}}),
    "Ativo": ("BooleanAttributeMetadata", {"DefaultValue": False}),
    "Situação": ("PicklistAttributeMetadata", {}),
    "Cores": ("MultiSelectPicklistAttributeMetadata", {}),
    "Contato": ("StringAttributeMetadata", {"FormatName": {"Value": "Email"}}),
    "Telefone": ("StringAttributeMetadata", {"FormatName": {"Value": "Phone"}}),
    "Site": ("StringAttributeMetadata", {"FormatName": {"Value": "Url"}}),
    "Número": ("StringAttributeMetadata", {"AutoNumberFormat": "NUM-{SEQNUM:5}"}),
    "Foto": ("ImageAttributeMetadata", {"CanStoreFullImage": True, "AttributeTypeName": {"Value": "ImageType"}}),
    "Anexo": ("FileAttributeMetadata", {"MaxSizeInKB": 32768, "AttributeTypeName": {"Value": "FileType"}}),
}


@pytest.mark.parametrize("coluna", list(TIPOS_ESPERADOS))
def test_cada_tipo_vira_a_coluna_certa(tmp_path, coluna):
    codigo, saida = gerar(tmp_path, _spec_tipos())
    assert codigo == 0, saida
    s = passo(plano(tmp_path), "coluna", f"Item.{coluna}")
    c = corpo(s)
    classe, props = TIPOS_ESPERADOS[coluna]
    assert s["url"] == "/api/data/v9.2/EntityDefinitions(LogicalName='abc_item')/Attributes"
    assert c["@odata.type"] == f"Microsoft.Dynamics.CRM.{classe}"
    for chave, valor in props.items():
        assert c[chave] == valor, chave
    assert rotulo(c["DisplayName"]) == (coluna, 1046)
    assert "IsPrimaryImage" not in c, "IsPrimaryImage false na criação levanta exceção"


def test_choice_e_sim_nao_levam_as_opcoes_com_o_prefixo_de_valor(tmp_path):
    gerar(tmp_path, _spec_tipos())
    p = plano(tmp_path)
    opcoes = corpo(passo(p, "coluna", "Item.Situação"))["OptionSet"]
    assert opcoes["IsGlobal"] is False
    assert [(o["Value"], rotulo(o["Label"])[0]) for o in opcoes["Options"]] == [
        (123450000, "Nova"), (123450001, "Usada"), (123450002, "Avariada")]
    booleano = corpo(passo(p, "coluna", "Item.Ativo"))["OptionSet"]
    assert (booleano["TrueOption"]["Value"], rotulo(booleano["FalseOption"]["Label"])[0]) == (1, "Não")


def test_nomes_derivados_sem_acento_e_plural(tmp_path):
    gerar(tmp_path, _spec_tipos())
    p = plano(tmp_path)
    t = corpo(passo(p, "tabela", "Item"))
    assert rotulo(t["DisplayCollectionName"])[0] == "Itens"
    assert corpo(passo(p, "coluna", "Item.Situação"))["SchemaName"] == "abc_Situacao"
    assert "LogicalName%20eq%20'abc_situacao'" in passo(p, "coluna", "Item.Situação")["existe"]


def test_lookup_vira_relacionamento_com_a_navegacao_fixa(tmp_path):
    gerar(tmp_path)
    p = plano(tmp_path)
    assert not any(s["fase"] == "coluna" and s["rotulo"] == "Pedido.Unidade" for s in p["passos"])
    s = next(s for s in p["passos"] if s["fase"] == "relacionamento")
    c = corpo(s)
    assert s["url"] == "/api/data/v9.2/RelationshipDefinitions"
    assert c["@odata.type"] == "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata"
    assert (c["ReferencedEntity"], c["ReferencedAttribute"], c["ReferencingEntity"]) == (
        "abc_unidade", "abc_unidadeid", "abc_pedido")
    assert c["ReferencingEntityNavigationPropertyName"] == c["Lookup"]["SchemaName"] == "abc_Unidade"
    assert c["CascadeConfiguration"]["Delete"] == "Restrict", "Lookup obrigatório não pode ficar órfão"
    assert c["Lookup"]["RequiredLevel"]["Value"] == "ApplicationRequired"
    menu = c["AssociatedMenuConfiguration"]
    assert menu["Behavior"] == "UseCollectionName" and rotulo(menu["Label"])[0] == "Pedidos"
    assert f"SchemaName%20eq%20'{c['SchemaName']}'" in s["existe"]


def test_publicar_lista_as_tabelas_e_roda_sempre(tmp_path):
    gerar(tmp_path)
    s = passo(plano(tmp_path), "publicar", "Publicar as tabelas")
    assert s["url"] == "/api/data/v9.2/PublishXml" and s["existe"] == ""
    xml = corpo(s)["ParameterXml"]
    assert "<entity>abc_unidade</entity><entity>abc_pedido</entity>" in xml


def test_lote_de_dados_e_multipart_crlf_com_um_changeset(tmp_path):
    gerar(tmp_path)
    s = passo(plano(tmp_path), "dados", "Pedido: 10 linha(s)")
    assert s["url"] == "/api/data/v9.2/$batch"
    assert s["tipo"].startswith("multipart/mixed; boundary=batch_")
    assert LF not in s["corpo"].replace(CRLF, ""), "o $batch exige CRLF"
    assert s["corpo"].endswith(f"--{s['tipo'].split('boundary=')[1]}--{CRLF}")
    partes = partes_do_lote(s)
    assert len(partes) == 10
    cabeca, _ = partes[0]
    assert "Content-ID: 1" in cabeca and "POST /api/data/v9.2/abc_pedidos HTTP/1.1" in cabeca


def test_linhas_do_filho_apontam_para_o_id_do_pai(tmp_path):
    gerar(tmp_path)
    p = plano(tmp_path)
    pais = [dado for _, dado in partes_do_lote(passo(p, "dados", "Unidade: 3 linha(s)"))]
    filhos = [dado for _, dado in partes_do_lote(passo(p, "dados", "Pedido: 10 linha(s)"))]
    ids = [pai["abc_unidadeid"] for pai in pais]
    assert len(set(ids)) == 3
    assert filhos[0]["abc_Unidade@odata.bind"] == f"/abc_unidades({ids[0]})"
    assert filhos[3]["abc_Unidade@odata.bind"] == f"/abc_unidades({ids[0]})"
    assert pais[2]["abc_ativa"] is False and pais[0]["abc_sigla"] == "AAA"
    assert filhos[1]["abc_status"] == 123450001
    assert filhos[0]["abc_dataprevista"] == "2026-01-13"
    assert filhos[0]["abc_incluidoem"] == "2026-01-13T08:30:00Z"
    assert filhos[0]["abc_valorestimado"] == 150.9
    assert filhos[0]["abc_emaildosolicitante"].endswith("@contoso.com")


def test_dados_deixam_de_fora_o_que_o_dataverse_gera_e_levam_escolhas(tmp_path):
    gerar(tmp_path, _spec_tipos())
    linhas = [dado for _, dado in partes_do_lote(passo(plano(tmp_path), "dados", "Item: 3 linha(s)"))]
    assert not {"abc_numero", "abc_foto", "abc_anexo"} & set(linhas[0])
    assert [linha["abc_cores"] for linha in linhas] == ["123450000", "123450001", "123450000"]
    assert linhas[0]["abc_peso"] == 12.75


def test_autorreferencia_aponta_para_a_linha_anterior_do_mesmo_lote(tmp_path):
    codigo, saida = gerar(tmp_path, _spec_auto())
    assert codigo == 0, saida
    linhas = [dado for _, dado in partes_do_lote(passo(plano(tmp_path), "dados", "Setor: 3 linha(s)"))]
    assert "abc_SetorPai@odata.bind" not in linhas[0]
    assert linhas[1]["abc_SetorPai@odata.bind"] == "$1" and linhas[2]["abc_SetorPai@odata.bind"] == "$1"


def test_autorreferencia_para_linha_posterior_e_c017(tmp_path):
    codigo, saida = gerar(tmp_path, _spec_auto(exemplos=["B", None, None]))
    assert codigo == 1
    assert "C017" in erros(saida)


def _spec_grande(linhas: int) -> dict:
    return {"tabelas": [{"nome": "Setor", "linhas": linhas, "colunas": [
        {"nome": "Nome", "tipo": "texto", "primaria": True},
        {"nome": "Setor pai", "tipo": "lookup", "alvo": "Setor"},
    ]}]}


def test_tabela_grande_vira_varios_lotes_com_id_e_autorreferencia_certos(tmp_path):
    codigo, saida = gerar(tmp_path, _spec_grande(150))
    assert codigo == 0, saida
    lotes = [s for s in plano(tmp_path)["passos"] if s["fase"] == "dados"]
    assert [s["rotulo"] for s in lotes] == ["Setor: linhas 1–100 de 150", "Setor: linhas 101–150 de 150"]
    assert all(len(s["corpo"]) < 131072 for s in lotes), "cada passo cabe no limite de expressão do flow"
    primeiro, segundo = (partes_do_lote(s) for s in lotes)
    assert len(primeiro) == 100 and len(segundo) == 50
    assert primeiro[1][1]["abc_SetorPai@odata.bind"] == "$1"
    id_da_primeira = primeiro[0][1]["abc_setorid"]
    assert segundo[0][1]["abc_SetorPai@odata.bind"] == f"/abc_setors({id_da_primeira})", "lote já gravado: pelo ID"
    assert "Content-ID: 1" in segundo[0][0]
    assert segundo[0][1]["abc_setorid"] in lotes[1]["existe"]


def test_dados_ja_carregados_sao_conferidos_pelo_id_da_primeira_linha(tmp_path):
    gerar(tmp_path)
    p = plano(tmp_path)
    s = passo(p, "dados", "Unidade: 3 linha(s)")
    primeiro = partes_do_lote(s)[0][1]["abc_unidadeid"]
    assert s["existe"] == (f"/api/data/v9.2/abc_unidades?$select=abc_unidadeid"
                           f"&$filter=abc_unidadeid%20eq%20{primeiro}")


def test_chave_alternativa_por_ultimo(tmp_path):
    gerar(tmp_path)
    p = plano(tmp_path)
    s = passo(p, "chave", "Unidade.Sigla (chave)")
    c = corpo(s)
    assert s["url"] == "/api/data/v9.2/EntityDefinitions(LogicalName='abc_unidade')/Keys"
    assert c["@odata.type"] == "Microsoft.Dynamics.CRM.EntityKeyMetadata"
    assert c["KeyAttributes"] == ["abc_sigla"]
    assert p["passos"][-1]["fase"] == "chave"


def test_calculada_fica_fora_do_plano_e_avisa(tmp_path):
    spec = _spec_tipos()
    spec["tabelas"][0]["colunas"].append({"nome": "Total", "tipo": "calculada"})
    codigo, saida = gerar(tmp_path, spec)
    assert codigo == 0, saida
    assert not any(s["rotulo"] == "Item.Total" for s in plano(tmp_path)["passos"])
    assert codigos(saida).count("C010") == 1, "só a calculada: o construtor cria escolhas, imagem e arquivo"


def test_plano_e_pacote_sao_deterministicos(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    gerar(tmp_path / "a")
    gerar(tmp_path / "b")
    for arquivo in ("plano-dataverse.json", f"construtor-dataverse/{ZIP}", "construtor-dataverse/construtor-escopo.json"):
        assert (tmp_path / "a" / "out" / arquivo).read_bytes() == (tmp_path / "b" / "out" / arquivo).read_bytes()


def test_flow_com_uma_por_tabela_grava_os_dois(tmp_path):
    codigo, saida = gerar(tmp_path, None, "--uma-por-tabela")
    assert codigo == 0, saida
    assert (tmp_path / "out" / "carga-mockup-tabelas" / "02-Pedido.xlsx").is_file()
    assert (tmp_path / "out" / "plano-dataverse.json").is_file()


def test_c018_conta_so_as_colunas_que_o_construtor_cria(tmp_path):
    spec = _spec_tipos()
    spec["tabelas"][0]["colunas"].append({"nome": "Total", "tipo": "calculada"})
    _, saida = gerar(tmp_path, spec)
    assert f"cria as {plano(tmp_path)['resumo']['colunas']} colunas" in saida
    assert plano(tmp_path)["resumo"]["colunas"] == 17


def test_sem_saida_so_valida_e_mostra_o_resumo(tmp_path):
    codigo, saida = rodar(MOLDE, "--trilha", "dataverse", "--flow", cwd=tmp_path)
    assert codigo == 0, saida
    assert "# construtor:" in saida
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("extra", [("--trilha", "sql-server", "--flow"),
                                   ("--trilha", "dataverse", "--flow", "--conferir", "x.json"),
                                   ("--trilha", "dataverse", "--flow", "--idioma", "0")])
def test_uso_incorreto(tmp_path, extra):
    (tmp_path / "x.json").write_text("{}", encoding="utf-8")
    codigo, _ = rodar(MOLDE, *extra, cwd=tmp_path)
    assert codigo == 2


# ---------- erros do plano ----------

def _spec_simples(*colunas, nome="Pedido", logico=None) -> dict:
    tabela = {"nome": nome, "colunas": [{"nome": "Protocolo", "tipo": "codigo", "primaria": True}, *colunas]}
    if logico:
        tabela["logico"] = logico
    return {"linhas": 2, "tabelas": [tabela]}


@pytest.mark.parametrize("spec", [
    _spec_simples(nome="123"),
    _spec_simples({"nome": "Data prevista", "tipo": "data"}, {"nome": "Data-prevista", "tipo": "data"}),
    _spec_simples({"nome": "Pedido Id", "tipo": "texto"}),
    _spec_simples(logico="semprefixo"),
    _spec_simples(logico="_ped"),
    _spec_simples({"nome": "Observação " + "x" * 40, "tipo": "texto"}),
], ids=["comeca-com-numero", "dois-viram-o-mesmo", "colide-com-a-chave-primaria", "logico-sem-prefixo",
        "logico-com-prefixo-vazio", "longo-demais"])
def test_nome_logico_invalido_e_c016(tmp_path, spec):
    codigo, saida = gerar(tmp_path, spec)
    assert codigo == 1, saida
    assert "C016" in erros(saida)
    assert not (tmp_path / "out" / "plano-dataverse.json").exists()


def test_logico_do_spec_vence_o_derivado(tmp_path):
    codigo, saida = gerar(tmp_path, _spec_simples({"nome": "Situação", "tipo": "texto", "logico": "xyz_estado"},
                                                  logico="xyz_ped"))
    assert codigo == 0, saida
    p = plano(tmp_path)
    assert corpo(passo(p, "tabela", "Pedido"))["SchemaName"] == "abc_ped"
    assert corpo(passo(p, "coluna", "Pedido.Situação"))["SchemaName"] == "abc_estado"


@pytest.mark.parametrize("coluna", [
    {"nome": "Valor", "tipo": "moeda", "casas": 5},
    {"nome": "Obs", "tipo": "texto", "tamanho": 5000},
    {"nome": "Obs", "tipo": "texto", "exemplos": ["{{prefixo}}"]},
    {"nome": "Qtd", "tipo": "inteiro", "exemplos": [3000000000]},
    {"nome": "Peso", "tipo": "decimal", "exemplos": [200000000000]},
    {"nome": "Obs", "tipo": "texto", "exemplos": ["x" * 150]},
    {"nome": "Fone", "tipo": "telefone", "exemplos": ["9" * 60]},
    {"nome": "Situação", "tipo": "choice", "opcoes": ["A" + chr(1), "B"]},
    {"nome": "Entrega", "tipo": "data", "exemplos": ["1700-01-01"]},
    {"nome": "Registro", "tipo": "data_hora", "exemplos": ["1752-12-31T08:00"]},
], ids=["moeda-casas", "texto-longo-demais", "marcador-no-valor", "inteiro-grande", "decimal-grande",
        "texto-maior-que-o-padrao", "telefone-maior-que-o-padrao", "controle-na-opcao", "data-antes-de-1753",
        "data-hora-antes-de-1753"])
def test_limite_do_dataverse_e_c017(tmp_path, coluna):
    codigo, saida = gerar(tmp_path, _spec_simples(coluna))
    assert codigo == 1, saida
    assert "C017" in erros(saida)


# ---------- pacote do flow ----------

def _zip(pasta: Path) -> zipfile.ZipFile:
    return zipfile.ZipFile(pasta / "out" / "construtor-dataverse" / ZIP)


def _fluxo_do_zip(z: zipfile.ZipFile) -> tuple[str, dict]:
    nome = next(n for n in z.namelist() if n.startswith("Workflows/"))
    return nome, json.loads(z.read(nome))


def test_zip_e_uma_solucao_nao_gerenciada_com_o_flow_e_a_conexao(tmp_path):
    gerar(tmp_path)
    z = _zip(tmp_path)
    nome, fluxo = _fluxo_do_zip(z)
    assert sorted(n for n in z.namelist() if not n.startswith("Workflows/")) == [
        "[Content_Types].xml", "customizations.xml", "solution.xml"]
    solucao = ET.fromstring(z.read("solution.xml"))
    assert solucao.get("languagecode") == "1046"
    manifesto = solucao.find("SolutionManifest")
    assert manifesto.findtext("UniqueName") == "ConstrutorDataverse" and manifesto.findtext("Managed") == "0"
    prefixo = manifesto.find("Publisher").findtext("CustomizationPrefix")
    raiz = {c.get("type"): c for c in manifesto.find("RootComponents")}
    guid = raiz["29"].get("id").strip("{}")
    assert nome == f"Workflows/ConstrutorDataverse-{guid.upper()}.json"
    personalizacao = ET.fromstring(z.read("customizations.xml"))
    workflow = personalizacao.find("Workflows/Workflow")
    assert workflow.get("WorkflowId").strip("{}") == guid
    assert workflow.findtext("JsonFileName") == "/" + nome and workflow.findtext("Category") == "5"
    referencia = fluxo["properties"]["connectionReferences"]["shared_webcontents"]
    logico = referencia["connection"]["connectionReferenceLogicalName"]
    assert logico.startswith(prefixo + "_") and raiz["10037"].get("schemaName") == logico
    conexao = personalizacao.find("connectionreferences/connectionreference")
    assert conexao.get("connectionreferencelogicalname") == logico
    assert conexao.findtext("connectorid") == "/providers/Microsoft.PowerApps/apis/shared_webcontents"
    assert fluxo["properties"]["definition"]["triggers"]["manual"]["kind"] == "Button"
    assert {info.create_system for info in z.infolist()} == {0}, "o mesmo zip em qualquer sistema"
    acoes = re.findall(r'"host": [{][^}]*[}]', json.dumps(fluxo, ensure_ascii=False))
    assert acoes and all('"connectionName": "shared_webcontents"' in h for h in acoes), "formato da solução exportada"
    autenticacao = '"authentication": ' + json.dumps("@parameters('$authentication')")
    assert json.dumps(fluxo).count(autenticacao) == len(acoes)


def test_idioma_da_solucao_vem_da_opcao(tmp_path):
    gerar(tmp_path, None, "--idioma", "1033")
    z = _zip(tmp_path)
    assert ET.fromstring(z.read("solution.xml")).get("languagecode") == "1033"
    assert "<Language>1033</Language>" in z.read("customizations.xml").decode("utf-8")


def test_flow_do_zip_passa_no_verificador(tmp_path):
    gerar(tmp_path)
    _, fluxo = _fluxo_do_zip(_zip(tmp_path))
    caminho = tmp_path / "fluxo.json"
    caminho.write_text(json.dumps(fluxo, ensure_ascii=False), encoding="utf-8")
    codigo, saida = rodar(caminho, cwd=tmp_path, script=VERIFICAR)
    assert codigo == 0, saida
    assert "0 erro(s), 0 aviso(s)" in saida, saida


def test_escopo_para_colar_passa_no_verificador_e_religa_as_acoes_http(tmp_path):
    gerar(tmp_path)
    caminho = tmp_path / "out" / "construtor-dataverse" / "construtor-escopo.json"
    codigo, saida = rodar(caminho, cwd=tmp_path, script=VERIFICAR)
    assert codigo == 0, saida
    assert "0 erro(s), 0 aviso(s)" in saida, "F020/F022: a colagem deixaria condição ou campo em branco"
    envelope = json.loads(caminho.read_text(encoding="utf-8"))
    assert envelope["nodeId"] == "Construtor" and envelope["isScopeNode"] is True
    assert '"connection": "shared_webcontents"' in json.dumps(envelope), "a colagem usa o formato do designer"
    acoes_http = set(re.findall(r'"([A-Za-z_]+)": [{]"type": "OpenApiConnection"',
                                json.dumps(envelope["serializedValue"], ensure_ascii=False)))
    assert acoes_http == set(envelope["allConnectionData"]) == {"Consultar_solucao", "Consultar_idioma",
                                                                "Consultar", "Enviar"}


def test_flow_inicia_toda_variavel_que_usa(tmp_path):
    definicao = json.loads(FLUXO.read_text(encoding="utf-8"))
    texto = json.dumps(definicao, ensure_ascii=False)
    iniciadas = {v["name"] for a in definicao["actions"].values() if a["type"] == "InitializeVariable"
                 for v in a["inputs"]["variables"]}
    usadas = set(re.findall(r"variables[(]'([A-Za-z_]+)'[)]", texto))
    usadas |= set(re.findall(r'"name": "([A-Za-z_]+)", "value"', texto))
    assert usadas <= iniciadas == {"Falhou", "Ja_existe", "Relatorio"}
    entradas = definicao["triggers"]["manual"]["inputs"]["schema"]["properties"]
    assert entradas["file"]["x-ms-content-hint"] == "FILE" and entradas["text"]["x-ms-content-hint"] == "TEXT"
    ambiente = definicao["actions"]["Construtor"]["actions"]["Ambiente"]["inputs"]
    assert ambiente["prefixo"].startswith("@toLower(coalesce("), "o nome lógico é minúsculo"
    passos = definicao["actions"]["Construtor"]["actions"]["Conferir_ambiente"]["actions"]["Passos"]
    assert passos["runtimeConfiguration"]["concurrency"]["repetitions"] == 1, "metadados um de cada vez"
    assert "replace(" in passos["actions"]["Seguir"]["actions"]["Passo"]["inputs"], "troca por passo, não no plano"
    assert "items('Passos')?['corpo']" not in texto and "items('Passos')?['url']" not in texto
    assert "json(string(body('Consultar')))" in texto, "o corpo do GET pode vir como texto ou objeto"
    fechar = definicao["actions"]["Construtor"]["actions"]["Fechar"]["actions"]
    assert fechar["Falhas"]["type"] == "Query" and "'falhou'" in fechar["Falhas"]["inputs"]["where"]
    assert "first(body('Falhas'))" in fechar["Encerrar_com_erro"]["inputs"]["runError"]["message"],         "a mensagem mostra a primeira falha, não a última linha do relatório"


def _acoes(no: dict):
    for nome, acao in (no.get("actions") or {}).items():
        yield nome, acao
        yield from _acoes(acao)
        for ramo in ("else", "default"):
            yield from _acoes(acao.get(ramo) or {})


def test_condicoes_do_flow_tem_and_ou_or_e_nenhum_campo_tem_variavel_sozinha():
    definicao = json.loads(FLUXO.read_text(encoding="utf-8"))
    condicoes = {nome: acao["expression"] for nome, acao in _acoes(definicao) if acao["type"] == "If"}
    assert all(isinstance(e, dict) and list(e) in (["and"], ["or"]) for e in condicoes.values()), condicoes
    sozinhas = re.findall(r'''"@[{]?variables[(]'[A-Za-z_]+'[)][}]?"''', json.dumps(definicao, ensure_ascii=False))
    assert sozinhas == [], "a colagem transforma em token de variável, que pode vir em branco"


def test_idioma_cai_no_padrao_se_a_leitura_falhar():
    definicao = json.loads(FLUXO.read_text(encoding="utf-8"))
    idioma = definicao["actions"]["Construtor"]["actions"]["Ambiente"]["inputs"]["idioma"]
    assert idioma.startswith("@string(coalesce(") and "1046" in idioma, "vazio quebraria o json() de todo passo com rótulo"


def test_relatorio_abre_com_o_ambiente_e_tem_uma_linha_por_passo():
    definicao = json.loads(FLUXO.read_text(encoding="utf-8"))
    conferir = definicao["actions"]["Construtor"]["actions"]["Conferir_ambiente"]
    abertura = conferir["actions"]["Anotar_solucao"]
    assert abertura["type"] == "AppendToArrayVariable" and abertura["inputs"]["value"]["fase"] == "ambiente"
    assert all(chave in abertura["inputs"]["value"]["detalhe"] for chave in ("'prefixo'", "'opcao'", "'idioma'"))
    assert conferir["actions"]["Passos"]["runAfter"] == {"Anotar_solucao": ["Succeeded"]}
    pulado = conferir["actions"]["Passos"]["actions"]["Seguir"]["else"]["actions"]["Anotar_pulado"]
    assert pulado["type"] == "AppendToArrayVariable" and pulado["inputs"]["value"]["resultado"] == "não executado"
    assert pulado["inputs"]["value"]["n"] == "@items('Passos')?['n']", "o Passo só existe no ramo que roda"
