"""Testes de `skills/power-platform/scripts/montar-carga-mockup.py` (sem rede; o .xlsx é lido com zipfile)."""
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
MOLDE = RAIZ / "skills" / "power-platform" / "assets" / "carga-mockup-molde.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
ABA_CONFERENCIA = "Conferência de tipos"


# ---------- apoio ----------

def _spec(**sobre):
    base = {
        "linhas": 4,
        "data_base": "2026-01-05",
        "tabelas": [
            {"nome": "Unidade", "sql": "dbo.Unidade", "pk": "Id_Unidade", "colunas": [
                {"nome": "Sigla", "tipo": "codigo", "chave": True, "tamanho": 3, "sql": "Cod_Unidade",
                 "exemplos": ["AAA", "BBB", "CCC", "DDD"]},
                {"nome": "Nome", "tipo": "texto", "primaria": True, "sql": "Nom_Unidade"},
            ]},
            {"nome": "Pedido", "sql": "dbo.Pedido", "pk": "Id_Pedido", "colunas": [
                {"nome": "Protocolo", "tipo": "codigo", "primaria": True, "chave": True, "sql": "Cod_Protocolo"},
                {"nome": "Unidade", "tipo": "lookup", "alvo": "Unidade", "obrigatoria": True, "sql": "Id_Unidade"},
                {"nome": "Status", "tipo": "choice", "opcoes": ["Aberto", "Encerrado"], "sql": "Status"},
            ]},
        ],
    }
    base.update(sobre)
    return base


def _gravar(pasta: Path, spec, nome="carga-mockup.json") -> Path:
    caminho = pasta / nome
    caminho.write_text(spec if isinstance(spec, str) else json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return caminho


def _config(pasta: Path, **dados) -> Path:
    caminho = pasta / "power-platform.config.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return caminho


def rodar(*args, cwd: Path, env_extra=None):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", **(env_extra or {})}
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=cwd, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    return r.returncode, r.stdout + r.stderr


def codigos(saida: str) -> list[str]:
    return re.findall(r": (?:ERRO|AVISO) (C\d{3}) ", saida)


def erros(saida: str) -> list[str]:
    return re.findall(r": ERRO (C\d{3}) ", saida)


def _texto_celula(c) -> str | None:
    tipo = c.get("t")
    if tipo == "inlineStr":
        return "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
    v = c.find("m:v", NS)
    return None if v is None else v.text


def ler_xlsx(caminho: Path) -> dict[str, list[list[tuple[str | None, str | None, str | None]]]]:
    """{aba: [[(texto, tipo t=, estilo s=) por célula] por linha]} — só com zipfile, sem dependência."""
    with zipfile.ZipFile(caminho) as z:
        livro = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        alvo = {r.get("Id"): r.get("Target") for r in rels}
        saida = {}
        for aba in livro.find("m:sheets", NS):
            folha = ET.fromstring(z.read("xl/" + alvo[aba.get(REL)]))
            linhas = []
            for row in folha.find("m:sheetData", NS):
                linhas.append([(_texto_celula(c), c.get("t"), c.get("s")) for c in row])
            saida[aba.get("name")] = linhas
        return saida


def _valores(linhas, coluna: int) -> list[str | None]:
    return [linha[coluna][0] if coluna < len(linha) else None for linha in linhas[1:]]


def _entidade(nome, logico, primaria, atributos):
    rot = lambda t: {"UserLocalizedLabel": {"Label": t}}  # noqa: E731
    return {
        "LogicalName": logico, "SchemaName": logico, "EntitySetName": logico + "s",
        "PrimaryIdAttribute": logico + "id", "PrimaryNameAttribute": primaria, "DisplayName": rot(nome),
        "Attributes": [
            {"LogicalName": lg, "SchemaName": lg, "AttributeType": tp, "DisplayName": rot(ex),
             "AttributeTypeName": {"Value": tp + "Type"}}
            for ex, lg, tp in atributos
        ],
    }


def _export_molde(**trocas):
    """Export da Web API como o ambiente ficaria se o Dataverse acertasse todos os tipos do molde."""
    unidade = [("Sigla", "abc_sigla", "String"), ("Nome", "abc_nome", "String"), ("Ativa", "abc_ativa", "Boolean")]
    pedido = [
        ("Protocolo", "abc_protocolo", "String"), ("Unidade", "abc_unidade", "Lookup"),
        ("Status", "abc_status", "Picklist"), ("Descrição", "abc_descricao", "Memo"),
        ("Quantidade de itens", "abc_quantidadedeitens", "Integer"), ("Valor estimado", "abc_valorestimado", "Money"),
        ("Data prevista", "abc_dataprevista", "DateTime"), ("Incluído em", "abc_incluidoem", "DateTime"),
        ("Urgente", "abc_urgente", "Boolean"), ("E-mail do solicitante", "abc_emaildosolicitante", "String"),
    ]
    pedido = [(ex, lg, trocas.get(ex, tp)) for ex, lg, tp in pedido if trocas.get(ex) != "-"]
    return {"value": [
        _entidade("Unidade", "abc_unidade", "abc_nome", unidade),
        _entidade("Pedido", "abc_pedido", trocas.get("_primaria", "abc_protocolo"), pedido),
    ]}


# ---------- o molde ----------

def test_molde_passa_no_dataverse_so_com_os_avisos_de_tipagem(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0, saida
    assert "0 erro(s)" in saida
    assert set(codigos(saida)) == {"C013", "C014"}
    assert "Unidade → Pedido" in saida


def test_molde_passa_no_sql_sem_aviso(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "sql-server", cwd=tmp_path)
    assert exit_ == 0, saida
    assert saida.strip().endswith("0 erro(s), 0 aviso(s)")


def test_sem_saida_nao_grava_nada(tmp_path):
    spec = _gravar(tmp_path, _spec())
    rodar(spec, "--trilha", "dataverse", cwd=tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["carga-mockup.json"]


# ---------- a planilha ----------

def test_planilha_tem_uma_aba_por_tabela_na_ordem_de_carga_e_a_conferencia_por_ultimo(tmp_path):
    spec = _spec()
    spec["tabelas"].reverse()  # filha antes da mãe no spec: a ordem de carga corrige
    caminho = _gravar(tmp_path, spec)
    exit_, saida = rodar(caminho, "--trilha", "dataverse", "--saida", tmp_path / "out", cwd=tmp_path)
    assert exit_ == 0, saida
    abas = ler_xlsx(tmp_path / "out" / "carga-mockup.xlsx")
    assert list(abas) == ["Unidade", "Pedido", ABA_CONFERENCIA]


def test_cabecalho_e_nome_de_exibicao_e_numero_de_linhas(tmp_path):
    caminho = _gravar(tmp_path, _spec())
    rodar(caminho, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    abas = ler_xlsx(tmp_path / "carga-mockup.xlsx")
    assert [c[0] for c in abas["Unidade"][0]] == ["Sigla", "Nome"]
    assert [c[0] for c in abas["Pedido"][0]] == ["Protocolo", "Unidade", "Status"]
    assert len(abas["Unidade"]) == 5 and len(abas["Pedido"]) == 5  # cabeçalho + 4


def test_linhas_da_tabela_vencem_o_global_e_a_opcao(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["linhas"] = 2
    caminho = _gravar(tmp_path, spec)
    rodar(caminho, "--trilha", "dataverse", "--linhas", "3", "--saida", tmp_path, cwd=tmp_path)
    abas = ler_xlsx(tmp_path / "carga-mockup.xlsx")
    assert len(abas["Pedido"]) == 3  # 2 da tabela
    assert len(abas["Unidade"]) == 4  # 3 do --linhas, acima do 4 do spec


def test_valores_gerados_tem_o_tipo_de_celula_que_ajuda_a_inferencia(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0, saida
    pedido = ler_xlsx(tmp_path / "carga-mockup.xlsx")["Pedido"]
    cab = [c[0] for c in pedido[0]]
    linha = pedido[1]
    celula = dict(zip(cab, linha))
    assert celula["Protocolo"][1] == "inlineStr" and not celula["Protocolo"][0].isdigit()
    assert celula["Urgente"][1] == "b"
    assert celula["Quantidade de itens"][1] is None and celula["Quantidade de itens"][0].isdigit()
    assert "." in celula["Valor estimado"][0]  # decimal de verdade, não inteiro
    data = float(celula["Data prevista"][0])
    assert data == int(data) and data > 40000  # serial de data do Excel
    assert float(celula["Incluído em"][0]) % 1 != 0  # data e hora: tem fração
    assert len(celula["Descrição"][0]) > 100  # texto longo passa do teto da linha única
    assert celula["E-mail do solicitante"][0].endswith("@contoso.com")


def test_choice_percorre_todas_as_opcoes(tmp_path):
    rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    pedido = ler_xlsx(tmp_path / "carga-mockup.xlsx")["Pedido"]
    status = _valores(pedido, [c[0] for c in pedido[0]].index("Status"))
    assert set(status) == {"Aberto", "Em andamento", "Encerrado", "Cancelado"}


def test_lookup_no_dataverse_aponta_para_o_nome_principal_do_alvo(tmp_path):
    rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    abas = ler_xlsx(tmp_path / "carga-mockup.xlsx")
    nomes = set(_valores(abas["Unidade"], 1))
    unidades = set(_valores(abas["Pedido"], 1))
    assert unidades <= nomes and len(unidades) == 3


def test_aba_de_conferencia_lista_toda_coluna_com_o_tipo_a_escolher(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "Anexo", "tipo": "arquivo"})
    caminho = _gravar(tmp_path, spec)
    rodar(caminho, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    conf = ler_xlsx(tmp_path / "carga-mockup.xlsx")[ABA_CONFERENCIA]
    assert "erra" in conf[0][0][0]  # o aviso no topo da aba
    cab = [c[0] for c in conf[2]]
    assert cab[:3] == ["Tabela", "Coluna", "Tipo no modelo"] and "Veio como" in cab
    linhas = {(l[0][0], l[1][0]): [c[0] for c in l] for l in conf[3:]}
    assert len(linhas) == 6
    assert "Pesquisa" in " ".join(linhas[("Pedido", "Unidade")])
    assert "Aberto" in " ".join(linhas[("Pedido", "Status")])
    assert "fora da planilha" in " ".join(linhas[("Pedido", "Anexo")])


def test_coluna_que_a_importacao_nao_aceita_fica_fora_da_aba(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "Anexo", "tipo": "arquivo"})
    caminho = _gravar(tmp_path, spec)
    exit_, saida = rodar(caminho, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0 and "C010" in codigos(saida)
    pedido = ler_xlsx(tmp_path / "carga-mockup.xlsx")["Pedido"]
    assert "Anexo" not in [c[0] for c in pedido[0]]


def test_tabelas_do_excel_e_estrutura_valida(tmp_path):
    rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    with zipfile.ZipFile(tmp_path / "carga-mockup.xlsx") as z:
        nomes = z.namelist()
        assert nomes[0] == "[Content_Types].xml"
        tabelas = sorted(n for n in nomes if n.startswith("xl/tables/"))
        assert len(tabelas) == 3
        tipos = z.read("[Content_Types].xml").decode()
        for n in tabelas + [n for n in nomes if n.startswith("xl/worksheets/sheet")]:
            assert f'PartName="/{n}"' in tipos
        nomes_tabela = set()
        for n in tabelas:
            t = ET.fromstring(z.read(n))
            nomes_tabela.add(t.get("name"))
            assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", t.get("name"))
        assert len(nomes_tabela) == 3


def test_saida_e_deterministica(tmp_path):
    rodar(MOLDE, "--trilha", "sql-server", "--saida", tmp_path / "a", cwd=tmp_path)
    rodar(MOLDE, "--trilha", "sql-server", "--saida", tmp_path / "b", cwd=tmp_path)
    for nome in ("carga-mockup.xlsx", "carga-mockup.sql"):
        assert (tmp_path / "a" / nome).read_bytes() == (tmp_path / "b" / nome).read_bytes()


def test_uma_por_tabela_grava_um_arquivo_por_tabela_com_uma_aba(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, "--uma-por-tabela", cwd=tmp_path)
    assert exit_ == 0, saida
    pasta = tmp_path / "carga-mockup-tabelas"
    assert sorted(p.name for p in pasta.iterdir()) == ["01-Unidade.xlsx", "02-Pedido.xlsx"]
    assert list(ler_xlsx(pasta / "02-Pedido.xlsx")) == ["Pedido"]
    assert (tmp_path / "carga-mockup.xlsx").is_file()


def test_openpyxl_abre_a_planilha_com_tipos_e_tabelas(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    livro = openpyxl.load_workbook(tmp_path / "carga-mockup.xlsx")
    assert livro.sheetnames == ["Unidade", "Pedido", ABA_CONFERENCIA]
    ws = livro["Pedido"]
    assert len(ws.tables) == 1
    tabela = next(iter(ws.tables.values()))
    assert tabela.ref == "A1:J11"
    cab = [c.value for c in ws[1]]
    linha = {k: c.value for k, c in zip(cab, ws[2])}
    assert linha["Urgente"] in (True, False)
    assert linha["Data prevista"].year == 2026
    assert isinstance(linha["Quantidade de itens"], int)


# ---------- o script SQL ----------

def test_sql_insere_na_ordem_com_transacao_guarda_e_subconsulta_de_lookup(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0, saida
    sql = (tmp_path / "carga-mockup.sql").read_text(encoding="utf-8")
    assert "SET XACT_ABORT ON;" in sql and "BEGIN TRANSACTION;" in sql and sql.rstrip().endswith("COMMIT TRANSACTION;")
    assert "THROW 50001" in sql and "WHERE [Cod_Unidade] = N'AAA'" in sql
    assert sql.index("INSERT INTO [dbo].[Unidade]") < sql.index("INSERT INTO [dbo].[Pedido]")
    assert sql.count("INSERT INTO [dbo].[Unidade]") == 3 and sql.count("INSERT INTO [dbo].[Pedido]") == 10
    assert "(SELECT [Id_Unidade] FROM [dbo].[Unidade] WHERE [Cod_Unidade] = N'AAA')" in sql
    assert "'20260113'" in sql  # data sem ambiguidade de DATEFORMAT
    assert re.search(r"'2026-01-\d\dT\d\d:\d\d:00'", sql)
    assert "Nunca rode em HML ou PRD" in sql


def test_sql_escapa_aspas_grava_null_e_bit(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"][1]["exemplos"] = ["D'Ávila", "B", "C", "E"]
    spec["tabelas"][1]["colunas"].append({"nome": "Urgente", "tipo": "sim_nao", "sql": "Flg_Urgente",
                                          "exemplos": [True, False]})
    spec["tabelas"][1]["colunas"].append({"nome": "Obs", "tipo": "texto", "sql": "Obs", "exemplos": [None, "x"]})
    caminho = _gravar(tmp_path, spec)
    exit_, saida = rodar(caminho, "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0, saida
    sql = (tmp_path / "carga-mockup.sql").read_text(encoding="utf-8")
    assert "N'D''Ávila'" in sql
    assert ", 1, NULL;" in sql and ", 0, N'x';" in sql


def test_sql_deixa_autonumero_e_calculada_fora_do_insert(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"] += [
        {"nome": "Número", "tipo": "autonumero", "sql": "Num_Pedido"},
        {"nome": "Prazo", "tipo": "calculada", "sql": "Dt_Prazo"},
    ]
    caminho = _gravar(tmp_path, spec)
    exit_, saida = rodar(caminho, "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0 and "aviso" in saida and codigos(saida) == []
    sql = (tmp_path / "carga-mockup.sql").read_text(encoding="utf-8")
    assert "Num_Pedido" not in sql and "Dt_Prazo" not in sql


def test_sql_lookup_sem_pk_no_alvo_grava_a_chave_literal(tmp_path):
    spec = _spec()
    del spec["tabelas"][0]["pk"]
    caminho = _gravar(tmp_path, spec)
    rodar(caminho, "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    sql = (tmp_path / "carga-mockup.sql").read_text(encoding="utf-8")
    assert "(SELECT [Id_Unidade]" not in sql
    assert re.search(r"SELECT N'PRO001', N'AAA', N'Aberto';", sql)
    assert "já foi aplicada" in sql  # acento intacto: o arquivo sai em UTF-8 com BOM, que o SSMS lê


def test_sql_tambem_grava_a_planilha_sem_aba_de_conferencia(tmp_path):
    rodar(MOLDE, "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert list(ler_xlsx(tmp_path / "carga-mockup.xlsx")) == ["Unidade", "Pedido"]


def test_lookup_para_a_propria_tabela(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"].append({"nome": "Unidade mãe", "tipo": "lookup", "alvo": "Unidade", "sql": "Id_Mae"})
    caminho = _gravar(tmp_path, spec)
    exit_, saida = rodar(caminho, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0, saida
    unidade = ler_xlsx(tmp_path / "carga-mockup.xlsx")["Unidade"]
    maes = [linha[2][0] if len(linha) > 2 else None for linha in unidade[1:]]
    assert maes[0] is None and set(maes[1:]) == {"Unidade 01"}


def test_lookup_obrigatorio_para_a_propria_tabela_e_erro(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"].append({"nome": "Mãe", "tipo": "lookup", "alvo": "Unidade", "obrigatoria": True,
                                          "sql": "Id_Mae"})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 1 and "C008" in erros(saida)


# ---------- erros do spec ----------

@pytest.mark.parametrize("mexer, codigo", [
    (lambda s: s["tabelas"][1]["colunas"][1].update(alvo="Inexistente"), "C006"),
    (lambda s: s["tabelas"][1]["colunas"][2].pop("opcoes"), "C006"),
    (lambda s: s["tabelas"][1]["colunas"][2].update(opcoes=["A", "A"]), "C006"),
    (lambda s: s["tabelas"][1]["colunas"][2].update(tipo="lista"), "C004"),
    (lambda s: s["tabelas"][1]["colunas"].append({"nome": "status", "tipo": "texto", "sql": "S2"}), "C004"),
    (lambda s: s["tabelas"][1]["colunas"][0].update(primaria=False), "C005"),
    (lambda s: s["tabelas"][1]["colunas"][2].update(primaria=True), "C005"),
    (lambda s: s["tabelas"][0]["colunas"][1].update(tipo="inteiro"), "C005"),
    (lambda s: s["tabelas"][0]["colunas"][1].update(chave=True), "C005"),
    (lambda s: s["tabelas"][1].update(nome="Pedido/Item"), "C003"),
    (lambda s: s["tabelas"][1].update(nome="P" * 32), "C003"),
    (lambda s: s["tabelas"][1].update(nome="unidade"), "C003"),
    (lambda s: s["tabelas"][1].update(nome=ABA_CONFERENCIA), "C003"),
    (lambda s: s["tabelas"][1].update(linhas=0), "C003"),
    (lambda s: s["tabelas"][1].update(colunas=[]), "C003"),
    (lambda s: s.update(linhas=201), "C001"),
    (lambda s: s.update(tabelas=[]), "C001"),
    (lambda s: s.update(data_base="05/01/2026"), "C001"),
])
def test_erros_de_estrutura(tmp_path, mexer, codigo):
    spec = _spec()
    mexer(spec)
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 1, saida
    assert codigo in erros(saida)


def test_dependencia_circular_e_erro(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"].append({"nome": "Último pedido", "tipo": "lookup", "alvo": "Pedido", "sql": "Id_Ult"})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 1 and "C007" in erros(saida)
    assert "Unidade" in saida and "Pedido" in saida


@pytest.mark.parametrize("coluna, exemplos", [
    ({"nome": "Código", "tipo": "codigo"}, [1, 2]),  # número perde o zero à esquerda
    ({"nome": "Data", "tipo": "data"}, ["05/01/2026"]),
    ({"nome": "Quando", "tipo": "data_hora"}, ["2026-01-05"]),
    ({"nome": "Valor", "tipo": "decimal"}, ["12,50"]),
    ({"nome": "Valor", "tipo": "decimal", "casas": 2}, [1.234]),
    ({"nome": "Qtd", "tipo": "inteiro"}, [1.5]),
    ({"nome": "Qtd", "tipo": "inteiro"}, [True]),
    ({"nome": "Ativo", "tipo": "sim_nao"}, ["Sim"]),
    ({"nome": "Tipo", "tipo": "choice", "opcoes": ["A", "B"]}, ["C"]),
    ({"nome": "Unid", "tipo": "lookup", "alvo": "Unidade"}, ["Unidade 99"]),
    ({"nome": "Curto", "tipo": "texto", "tamanho": 3}, ["abcd"]),
    ({"nome": "Mail", "tipo": "email"}, ["sem-arroba"]),
    ({"nome": "Site", "tipo": "url"}, ["contoso.com"]),
    ({"nome": "Obrig", "tipo": "texto", "obrigatoria": True}, [None]),
])
def test_exemplo_invalido_para_o_tipo(tmp_path, coluna, exemplos):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({**coluna, "sql": "Col_X", "exemplos": exemplos})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 1, saida
    assert "C008" in erros(saida)


def test_chave_com_exemplo_repetido_ou_curto(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"][0]["exemplos"] = ["AAA", "BBB"]  # 4 linhas, 2 valores
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 1 and "C008" in erros(saida)
    assert "linhas" in saida


@pytest.mark.parametrize("mexer", [
    lambda s: s["tabelas"][0].pop("sql"),
    lambda s: s["tabelas"][1]["colunas"][2].pop("sql"),
    lambda s: s["tabelas"][1].update(sql="dbo.Pedido; DROP TABLE x"),
    lambda s: s["tabelas"][0].update(pk="Id Unidade"),
])
def test_trilha_sql_exige_nomes_validos(tmp_path, mexer):
    spec = _spec()
    mexer(spec)
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", cwd=tmp_path)
    assert exit_ == 1 and "C009" in erros(saida)


def test_trilha_dataverse_nao_exige_nome_sql(tmp_path):
    spec = _spec()
    for tabela in spec["tabelas"]:
        tabela.pop("sql")
        for coluna in tabela["colunas"]:
            coluna.pop("sql")
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0, saida


def test_sql_lookup_para_chave_gerada_pelo_banco_e_erro(tmp_path):
    spec = _spec()
    spec["tabelas"][0]["colunas"] = [
        {"nome": "Número", "tipo": "autonumero", "chave": True, "sql": "Num"},
        {"nome": "Nome", "tipo": "texto", "sql": "Nom"},
    ]
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", cwd=tmp_path)
    assert exit_ == 1 and "C009" in erros(saida)


# ---------- trilha e config ----------

def test_sem_trilha_e_erro(tmp_path):
    exit_, saida = rodar(_gravar(tmp_path, _spec()), cwd=tmp_path)
    assert exit_ == 1 and "C002" in erros(saida)


def test_trilha_vem_do_config(tmp_path):
    _config(tmp_path, trilha_dados="sql-server")
    exit_, saida = rodar(_gravar(tmp_path, _spec()), cwd=tmp_path)
    assert exit_ == 0, saida
    assert "trilha: sql-server" in saida


def test_spec_que_contradiz_o_config_e_erro(tmp_path):
    _config(tmp_path, trilha_dados="sql-server")
    exit_, saida = rodar(_gravar(tmp_path, _spec(trilha="dataverse")), cwd=tmp_path)
    assert exit_ == 1 and "C002" in erros(saida)


def test_opcao_trilha_vence_o_config(tmp_path):
    _config(tmp_path, trilha_dados="sql-server")
    exit_, saida = rodar(_gravar(tmp_path, _spec()), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0 and "trilha: dataverse" in saida


# ---------- avisos ----------

def test_avisos_de_tipagem_no_dataverse(tmp_path):
    exit_, saida = rodar(_gravar(tmp_path, _spec()), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0
    assert codigos(saida).count("C013") == 1
    assert codigos(saida).count("C014") == 2  # Unidade (lookup) e Status (choice)
    assert "confira" in saida.lower()


def test_choice_com_mais_opcoes_que_linhas_avisa(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"][2]["opcoes"] = ["A", "B", "C", "D", "E"]
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0 and "C011" in codigos(saida)


def test_email_de_dominio_real_avisa(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "Mail", "tipo": "email", "sql": "Mail",
                                          "exemplos": ["alguem@empresa-real.com.br"]})  # lint-ok: prova do C012
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", cwd=tmp_path)
    assert exit_ == 0 and "C012" in codigos(saida)


# ---------- conferência contra o ambiente ----------

def _rodar_conferir(tmp_path, export):
    caminho = tmp_path / "export.json"
    caminho.write_text(json.dumps(export, ensure_ascii=False), encoding="utf-8")
    return rodar(MOLDE, "--trilha", "dataverse", "--conferir", caminho, cwd=tmp_path)


def test_conferir_ambiente_igual_ao_modelo_so_avisa_o_que_o_export_nao_prova(tmp_path):
    exit_, saida = _rodar_conferir(tmp_path, _export_molde())
    assert exit_ == 0, saida
    assert erros(saida) == []
    assert set(codigos(saida)) == {"C104"}
    assert "Somente data" in saida and "Aberto" in saida


def test_conferir_acusa_choice_e_lookup_que_vieram_como_texto(tmp_path):
    exit_, saida = _rodar_conferir(tmp_path, _export_molde(Status="String", Unidade="String"))
    assert exit_ == 1
    assert erros(saida).count("C103") == 2
    assert "Pedido.Status" in saida and "Texto não vira" in saida


def test_conferir_acusa_decimal_que_virou_inteiro(tmp_path):
    exit_, saida = _rodar_conferir(tmp_path, _export_molde(**{"Valor estimado": "Integer"}))
    assert exit_ == 1 and "C103" in erros(saida)


def test_conferir_acusa_coluna_e_tabela_ausentes(tmp_path):
    export = _export_molde(Urgente="-")
    exit_, saida = _rodar_conferir(tmp_path, export)
    assert exit_ == 1 and "C102" in erros(saida)
    export["value"] = export["value"][1:]
    exit_, saida = _rodar_conferir(tmp_path, export)
    assert "C101" in erros(saida)


def test_conferir_acusa_nome_principal_errado(tmp_path):
    exit_, saida = _rodar_conferir(tmp_path, _export_molde(_primaria="abc_status"))
    assert exit_ == 1 and "C105" in erros(saida)


def test_conferir_acha_pelo_nome_logico_do_spec(tmp_path):
    spec = json.loads(MOLDE.read_text(encoding="utf-8"))
    spec["tabelas"][1]["logico"] = "abc_pedido"
    spec["tabelas"][1]["nome"] = "Pedido de compra"
    export = _export_molde()
    caminho_spec = _gravar(tmp_path, spec)
    (tmp_path / "export.json").write_text(json.dumps(export), encoding="utf-8")
    exit_, saida = rodar(caminho_spec, "--trilha", "dataverse", "--conferir", tmp_path / "export.json", cwd=tmp_path)
    assert exit_ == 0, saida


def test_conferir_na_trilha_sql_e_uso_incorreto(tmp_path):
    (tmp_path / "export.json").write_text("{}", encoding="utf-8")
    exit_, saida = rodar(MOLDE, "--trilha", "sql-server", "--conferir", tmp_path / "export.json", cwd=tmp_path)
    assert exit_ == 2 and "dataverse" in saida


def test_conferir_export_invalido_e_uso_incorreto(tmp_path):
    (tmp_path / "export.json").write_text("não é json", encoding="utf-8")
    exit_, _ = rodar(MOLDE, "--trilha", "dataverse", "--conferir", tmp_path / "export.json", cwd=tmp_path)
    assert exit_ == 2


# ---------- uso ----------

def test_spec_ilegivel_e_uso_incorreto(tmp_path):
    exit_, _ = rodar(_gravar(tmp_path, "{ quebrado"), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 2
    exit_, _ = rodar(tmp_path / "nao-existe.json", "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 2


def test_linhas_invalida_e_uso_incorreto(tmp_path):
    exit_, _ = rodar(MOLDE, "--trilha", "dataverse", "--linhas", "0", cwd=tmp_path)
    assert exit_ == 2


def test_falha_ao_gravar_e_erro(tmp_path):
    (tmp_path / "carga-mockup.xlsx").mkdir()  # um diretório no lugar do arquivo
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 1 and "C015" in erros(saida)


def test_saida_com_acento_em_console_cp1252(tmp_path):
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", cwd=tmp_path, env_extra={"PYTHONIOENCODING": "cp1252"})
    assert exit_ == 0
    assert "Descrição" in saida or "Conferência" in saida


# ---------- achados da revisão: entrada malformada vira código, nunca traceback ----------

def _sem_traceback(saida: str) -> None:
    assert "Traceback" not in saida, saida


@pytest.mark.parametrize("tipo", [["a"], {}, 3])
def test_tipo_que_nao_e_texto_e_c004(tmp_path, tipo):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "X", "tipo": tipo, "sql": "X"})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    _sem_traceback(saida)
    assert exit_ == 1 and "C004" in erros(saida)


@pytest.mark.parametrize("bruto", ["Infinity", "NaN", "-Infinity", "1e30"])
def test_decimal_nao_finito_ou_enorme_e_c008(tmp_path, bruto):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "V", "tipo": "moeda", "sql": "V", "exemplos": ["__X__"]})
    texto = json.dumps(spec, ensure_ascii=False).replace('"__X__"', bruto)
    exit_, saida = rodar(_gravar(tmp_path, texto), "--trilha", "dataverse", cwd=tmp_path)
    _sem_traceback(saida)
    assert exit_ == 1 and "C008" in erros(saida)


def test_caractere_invalido_no_spec_e_uso_incorreto(tmp_path):
    escape_surrogate = chr(92) + "ud800"  # o JSON leva o escape; json.loads devolve um surrogate solto
    texto = json.dumps(_spec()).replace('"Status"', '"Status' + escape_surrogate + '"', 1)
    exit_, saida = rodar(_gravar(tmp_path, texto), "--trilha", "dataverse", "--saida", tmp_path, cwd=tmp_path)
    _sem_traceback(saida)
    assert exit_ == 2


def test_data_base_no_fim_do_calendario_e_c001(tmp_path):
    spec = _spec(data_base="9999-12-30")
    spec["tabelas"][1]["colunas"].append({"nome": "D", "tipo": "data", "sql": "D"})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    _sem_traceback(saida)
    assert exit_ == 1 and "C001" in erros(saida)


def test_export_malformado_nao_quebra(tmp_path):
    export = _export_molde()
    for atributo in export["value"][1]["Attributes"]:
        atributo["AttributeTypeName"] = "MoneyType"  # texto no lugar de {"Value": ...}
    exit_, saida = _rodar_conferir(tmp_path, export)
    _sem_traceback(saida)
    assert exit_ == 0, saida
    for atributo in export["value"][1]["Attributes"]:
        atributo["DisplayName"] = "texto solto"
    exit_, saida = _rodar_conferir(tmp_path, export)
    _sem_traceback(saida)
    assert exit_ == 1 and "C102" in erros(saida)


def test_export_aninhado_demais_e_uso_incorreto(tmp_path):
    (tmp_path / "export.json").write_text("[" * 100000 + "]" * 100000, encoding="utf-8")
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", "--conferir", tmp_path / "export.json", cwd=tmp_path)
    _sem_traceback(saida)
    assert exit_ == 2


def test_tabela_sem_coluna_na_carga_e_c003(tmp_path):
    spec = {"tabelas": [{"nome": "T", "sql": "dbo.T", "colunas": [
        {"nome": "N", "tipo": "autonumero", "sql": "C"}, {"nome": "F", "tipo": "arquivo", "sql": "F"}]}]}
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 1 and "C003" in erros(saida)
    assert not (tmp_path / "carga-mockup.sql").exists()


def test_limites_do_excel(tmp_path):
    casos = [
        (lambda s: s["tabelas"][1]["colunas"][2].update(nome="N" * 256), "C004"),
        (lambda s: s["tabelas"][1].update(nome="\U0001F600" * 16), "C003"),
        (lambda s: s["tabelas"][1]["colunas"].append(
            {"nome": "Longo", "tipo": "texto_longo", "sql": "L", "exemplos": ["y" * 32768]}), "C008"),
    ]
    for mexer, codigo in casos:
        spec = _spec()
        mexer(spec)
        exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
        assert exit_ == 1 and codigo in erros(saida), saida


def test_limites_do_excel_no_limite_passam(tmp_path):
    spec = _spec()
    spec["tabelas"][1]["colunas"][2]["nome"] = "N" * 255
    spec["tabelas"][1]["nome"] = "\U0001F600" * 15
    spec["tabelas"][1]["colunas"].append({"nome": "Longo", "tipo": "texto_longo", "sql": "L", "exemplos": ["y" * 32767]})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0, saida


def test_chave_que_so_difere_em_maiuscula_ou_espaco_no_fim_e_repetida(tmp_path):
    for exemplos in (["aaa", "AAA", "bbb", "ccc"], ["aaa", "aaa ", "bbb", "ccc"]):
        spec = _spec()
        spec["tabelas"][0]["colunas"][0].update(exemplos=exemplos, tamanho=4)
        exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", cwd=tmp_path)
        assert exit_ == 1 and "C008" in erros(saida), exemplos


@pytest.mark.parametrize("tipo", ["email", "url"])
def test_valor_gerado_que_nao_cabe_no_tamanho_e_c008(tmp_path, tipo):
    spec = _spec()
    spec["tabelas"][1]["colunas"].append({"nome": "E", "tipo": tipo, "tamanho": 10, "sql": "E"})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", cwd=tmp_path)
    assert exit_ == 1 and "C008" in erros(saida)
    assert "tamanho" in saida


def test_conferir_ignora_atributo_auxiliar_com_o_mesmo_nome_de_exibicao(tmp_path):
    export = _export_molde()
    pedido = export["value"][1]["Attributes"]
    auxiliar = {"LogicalName": "abc_unidadename", "AttributeType": "String", "AttributeOf": "abc_unidade",
                "AttributeTypeName": {"Value": "StringType"}, "DisplayName": {"UserLocalizedLabel": {"Label": "Unidade"}}}
    pedido.insert(0, auxiliar)
    exit_, saida = _rodar_conferir(tmp_path, export)
    assert exit_ == 0, saida


def test_conferir_sem_atributoof_prefere_o_do_tipo_esperado(tmp_path):
    export = _export_molde()
    pedido = export["value"][1]["Attributes"]
    pedido.insert(0, {"LogicalName": "abc_unidadename", "AttributeType": "String",
                      "AttributeTypeName": {"Value": "StringType"},
                      "DisplayName": {"UserLocalizedLabel": {"Label": "Unidade"}}})
    exit_, saida = _rodar_conferir(tmp_path, export)
    assert exit_ == 0, saida


def test_ciclo_nomeia_so_as_tabelas_do_ciclo(tmp_path):
    def tabela(nome, alvo):
        return {"nome": nome, "colunas": [{"nome": "Nome", "tipo": "texto", "primaria": True},
                                          {"nome": "Ref", "tipo": "lookup", "alvo": alvo}]}
    spec = {"tabelas": [tabela("A", "B"), tabela("B", "C"), tabela("C", "A"), tabela("D", "A")]}
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "dataverse", cwd=tmp_path)
    linha = next(l for l in saida.splitlines() if "C007" in l)
    assert "A, B, C" in linha and "D" not in linha.split("C007", 1)[1].split(":")[0]


def test_sem_trilha_com_conferir_mostra_o_c002(tmp_path):
    (tmp_path / "export.json").write_text(json.dumps(_export_molde()), encoding="utf-8")
    exit_, saida = rodar(MOLDE, "--conferir", tmp_path / "export.json", cwd=tmp_path)
    assert exit_ == 1 and "C002" in erros(saida)


def test_config_quebrado_achado_para_cima_nao_atrapalha_com_trilha_explicita(tmp_path):
    (tmp_path / "power-platform.config.json").write_text("{ quebrado", encoding="utf-8")
    exit_, saida = rodar(MOLDE, "--trilha", "dataverse", cwd=tmp_path)
    assert exit_ == 0, saida
    exit_, _ = rodar(MOLDE, "--trilha", "dataverse", "--config", tmp_path / "power-platform.config.json",
                     cwd=tmp_path)
    assert exit_ == 2  # config passado de propósito continua sendo lido


def test_datas_geradas_tem_dia_13_ou_mais_e_nao_repetem(tmp_path):
    # dia/mês trocado na importação vira mês inválido (erro visível), não uma data errada calada
    spec = _spec(data_base="2026-01-05")
    spec["tabelas"].append({"nome": "Agenda", "sql": "dbo.Agenda", "pk": "Id_Agenda", "linhas": 60, "colunas": [
        {"nome": "Titulo", "tipo": "texto", "primaria": True, "sql": "Des_Titulo"},
        {"nome": "Dia", "tipo": "data", "sql": "Dat_Dia"},
        {"nome": "Quando", "tipo": "data_hora", "sql": "Dat_Quando"},
    ]})
    exit_, saida = rodar(_gravar(tmp_path, spec), "--trilha", "sql-server", "--saida", tmp_path, cwd=tmp_path)
    assert exit_ == 0, saida
    sql = (tmp_path / "carga-mockup.sql").read_text(encoding="utf-8")
    dias = re.findall(r"'(\d{4})(\d{2})(\d{2})'", sql)
    horas = re.findall(r"'(\d{4})-(\d{2})-(\d{2})T\d\d:\d\d:00'", sql)
    assert len(dias) == 60 and len(horas) == 60
    assert all(int(d) >= 13 for _, _, d in dias + horas), [x for x in dias + horas if int(x[2]) < 13]
    assert len(set(dias)) == 60 and dias == sorted(dias), "as datas continuam distintas e em ordem"
    assert dias[0] == ("2026", "01", "13")
