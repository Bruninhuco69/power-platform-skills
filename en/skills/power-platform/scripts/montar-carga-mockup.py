#!/usr/bin/env python3
"""Monta a carga mockup das tabelas do app: um .xlsx com dados fictícios e, no SQL, o script de INSERT.

Entrada: `carga-mockup.json` (molde em `assets/carga-mockup-molde.json`), escrito no `/pp:arquitetura`
pelo `pp:agente-arquitetura` junto com o modelo de dados: uma entrada por tabela, com as colunas
(nome de exibição, tipo, chave, primária, opções de Choice, alvo de Lookup) e, se quiser, exemplos.

Saída (só com --saida <pasta>):
  carga-mockup.xlsx   uma aba por tabela, na ordem de carga (quem é apontado por Lookup vem antes),
                      cada uma formatada como tabela do Excel e com o valor do tipo certo na célula
                      (data é data, número é número, código é texto). Na trilha Dataverse, a última
                      aba é a "Conferência de tipos": o que escolher em cada coluna e o que costuma
                      vir errado.
  carga-mockup.sql    só na trilha SQL: INSERT em transação, na mesma ordem, para o banco de DEV.
  carga-mockup-tabelas/NN-<tabela>.xlsx   com --uma-por-tabela: um arquivo por tabela (o "Criar com
                      dados externos" do Dataverse lê só a primeira aba do arquivo).

--flow (trilha Dataverse): grava também o plano do construtor e o flow que o executa, para criar tudo
direto pela Web API (tabelas, colunas com o tipo certo, Choices, relacionamentos e as linhas mockup):
  plano-dataverse.json                       os pedidos à Web API, na ordem, sem nada do ambiente
  construtor-dataverse/ConstrutorDataverse_1_0_0_0.zip   solução não gerenciada com o flow (importar)
  construtor-dataverse/construtor-escopo.json            o mesmo flow para colar no designer

--conferir <export.json>: compara o tipo de cada coluna criada no Dataverse (o export da Web API do
`extrair-nomes-as-built.py`) com o tipo do spec. O Dataverse deduz o tipo pelos dados e erra.

Trilha: --trilha > `trilha_dados` do power-platform.config.json > `trilha` do spec.
Linhas por tabela: `linhas` da tabela > --linhas > `linhas` do spec > 10.

Módulos de apoio na mesma pasta: `_carga_modelo.py` (tipos e estruturas), `_carga_valores.py` (valores
fictícios), `_carga_xlsx.py` (gravador do .xlsx), `_carga_sql.py` (script T-SQL), `_carga_conferir.py`
(--conferir), `_carga_plano.py` (plano do construtor) e `_carga_construtor.py` (pacote do flow).

Só lê os arquivos de entrada. Sem rede. Saída: `caminho:lugar: ERRO|AVISO Cnnn mensagem`;
última linha `N erro(s), M aviso(s)`. Exit: 0 sem erro, 1 com erro, 2 uso incorreto.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from _carga_conferir import conferir_ambiente, entidades_do_export
from _carga_construtor import arquivos_do_construtor
from _carga_modelo import (CASAS_PADRAO, CHAVE_OK, COM_CASAS, COM_OPCOES, COM_TAMANHO, FORA_DA_CARGA,
                           GERADO_PELO_BANCO, PRIMARIA_OK, TIPOS, Achado, Coluna, Relato, Spec, Tabela,
                           na_carga)
from _carga_plano import ARQ_PLANO, montar_plano, plano_em_bytes, resumo_texto
from _carga_sql import ARQ_SQL, script_sql
from _carga_valores import DATA, EMAIL, LINHAS_PADRAO, URL, montar_valores
from _carga_xlsx import EST_QUEBRA, Aba, xlsx

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

NOME_CONFIG = "power-platform.config.json"
TRILHAS = ("dataverse", "sql-server")
MAX_LINHAS = 200
DATA_BASE_PADRAO = date(2026, 1, 13)
IDIOMA_PADRAO = 1046  # pt-BR: idioma da solução do construtor (.zip)
ABA_CONFERENCIA = tr("Conferência de tipos", "Type check")
ARQ_XLSX = tr("carga-mockup.xlsx", "mockup-load.xlsx")
PASTA_POR_TABELA = tr("carga-mockup-tabelas", "mockup-load-tables")
DOMINIOS_FICTICIOS = ("contoso.com", "fabrikam.com", "example.com", "example.org", "example.net",
                      "exemplo.com", "exemplo.com.br")
IDENT_SQL = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ABA_PROIBIDO = re.compile(r"[:\\/?*\[\]]")
CONTROLES = re.compile(r"[\x00-\x1f\x7f]")
MAX_ABA = 31          # caracteres UTF-16 no nome de aba
MAX_CABECALHO = 255   # caracteres UTF-16 no nome de coluna de uma tabela do Excel


# ---------- leitura do spec ----------

def _texto(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def _inteiro_em(valor: Any, minimo: int, maximo: int) -> int | None:
    if isinstance(valor, int) and not isinstance(valor, bool) and minimo <= valor <= maximo:
        return valor
    return None


def _opcional(item: dict, chave: str) -> str | None:
    valor = item.get(chave)
    if valor is None:
        return None
    return valor.strip() if isinstance(valor, str) else str(valor)


def _u16(texto: str) -> int:
    """Comprimento como o Excel conta: em unidades UTF-16 (emoji vale 2)."""
    return len(texto.encode("utf-16-le")) // 2


def _data(valor: Any) -> date | None:
    if not isinstance(valor, str) or not DATA.fullmatch(valor):
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def ler_spec(dados: Any, r: Relato) -> Spec | None:
    if not isinstance(dados, dict) or not isinstance(dados.get("tabelas"), list) or not dados["tabelas"]:
        r.erro("spec", "C001", tr("a raiz precisa ser um objeto com `tabelas`, uma lista com pelo menos uma tabela",
                                  "the root must be an object with `tabelas`, a list with at least one table"))
        return None
    linhas = _inteiro_em(dados.get("linhas"), 1, MAX_LINHAS)
    if "linhas" in dados and linhas is None:
        r.erro("spec", "C001", tr(f"`linhas` precisa ser inteiro de 1 a {MAX_LINHAS}",
                                  f"`linhas` must be an integer from 1 to {MAX_LINHAS}"))
    data_base = DATA_BASE_PADRAO
    if "data_base" in dados:
        data_base = _data(dados["data_base"]) or DATA_BASE_PADRAO
        if _data(dados["data_base"]) is None:
            r.erro("spec", "C001", tr("`data_base` precisa ser uma data AAAA-MM-DD", "`data_base` must be a date in YYYY-MM-DD format"))
        elif date.max - data_base < timedelta(days=6 * MAX_LINHAS):  # de 3 em 3, pulando os dias 1 a 12
            r.erro("spec", "C001", tr("`data_base` perto demais do fim do calendário: as datas geradas não cabem",
                                      "`data_base` too close to the end of the calendar: the generated dates do not fit"))
            data_base = DATA_BASE_PADRAO
    trilha = dados.get("trilha")
    if trilha is not None and trilha not in TRILHAS:
        r.erro("spec", "C002", tr(f"`trilha` precisa ser {' ou '.join(TRILHAS)}", f"`trilha` must be {' or '.join(TRILHAS)}"))
        trilha = None
    tabelas = (ler_tabela(item, n, r) for n, item in enumerate(dados["tabelas"], start=1))
    return Spec(tuple(t for t in tabelas if t), linhas, data_base, trilha)


def ler_tabela(item: Any, numero: int, r: Relato) -> Tabela | None:
    if not isinstance(item, dict) or not _texto(item.get("nome")):
        r.erro(f"tabelas[{numero}]", "C003", tr("tabela sem `nome`", "table without `nome`"))
        return None
    nome = item["nome"].strip()
    if not isinstance(item.get("colunas"), list) or not item["colunas"]:
        r.erro(nome, "C003", tr("tabela sem `colunas`", "table without `colunas`"))
        return None
    linhas = None
    if "linhas" in item:
        linhas = _inteiro_em(item["linhas"], 1, MAX_LINHAS)
        if linhas is None:
            r.erro(nome, "C003", tr(f"`linhas` precisa ser inteiro de 1 a {MAX_LINHAS}",
                                    f"`linhas` must be an integer from 1 to {MAX_LINHAS}"))
    colunas = (ler_coluna(c, nome, k, r) for k, c in enumerate(item["colunas"], start=1))
    return Tabela(nome, tuple(c for c in colunas if c), linhas,
                  _opcional(item, "sql"), _opcional(item, "pk"), _opcional(item, "logico"))


def _flags(item: dict, lugar: str, r: Relato) -> dict[str, bool]:
    flags = {}
    for flag in ("obrigatoria", "primaria", "chave"):
        valor = item.get(flag, False)
        if not isinstance(valor, bool):
            r.erro(lugar, "C004", tr(f"`{flag}` precisa ser true ou false", f"`{flag}` must be true or false"))
            valor = False
        flags[flag] = valor
    return flags


def _medidas(item: dict, tipo: str, lugar: str, r: Relato) -> tuple[int | None, int]:
    tamanho, casas = None, CASAS_PADRAO
    if "tamanho" in item:
        tamanho = _inteiro_em(item["tamanho"], 1, 1_048_576)
        if tamanho is None or tipo not in COM_TAMANHO:
            r.erro(lugar, "C004", tr("`tamanho` é inteiro positivo e só vale para coluna de texto",
                                     "`tamanho` is a positive integer and only applies to a text column"))
            tamanho = None
    if "casas" in item:
        casas = _inteiro_em(item["casas"], 0, 10)
        if casas is None or tipo not in COM_CASAS:
            r.erro(lugar, "C004", tr("`casas` é inteiro de 0 a 10 e só vale para decimal e moeda",
                                     "`casas` is an integer from 0 to 10 and only applies to decimal and moeda"))
            casas = CASAS_PADRAO
    return tamanho, casas


def _opcoes(item: dict, tipo: str, lugar: str, r: Relato) -> tuple[str, ...]:
    if tipo not in COM_OPCOES:
        return ()
    opcoes = item.get("opcoes")
    validas = isinstance(opcoes, list) and opcoes and all(_texto(o) for o in opcoes)
    if not validas or len({o.strip().casefold() for o in opcoes}) != len(opcoes):
        r.erro(lugar, "C006", tr("Choice precisa de `opcoes`: lista de rótulos de texto, sem repetição",
                                     "Choice needs `opcoes`: a list of text labels, without repetition"))
        return ()
    return tuple(o.strip() for o in opcoes)


def ler_coluna(item: Any, tabela: str, numero: int, r: Relato) -> Coluna | None:
    if not isinstance(item, dict) or not _texto(item.get("nome")):
        r.erro(f"{tabela}.colunas[{numero}]", "C004", tr("coluna sem `nome`", "column without `nome`"))
        return None
    nome = item["nome"].strip()
    lugar = f"{tabela}.{nome}"
    if CONTROLES.search(nome):
        r.erro(lugar, "C004", tr("nome com quebra de linha ou caractere de controle", "name with a line break or control character"))
        return None
    if _u16(nome) > MAX_CABECALHO:
        r.erro(lugar, "C004", tr(f"nome com mais de {MAX_CABECALHO} caracteres: o Excel não abre",
                                     f"name with more than {MAX_CABECALHO} characters: Excel will not open it"))
        return None
    tipo = item.get("tipo")
    if not isinstance(tipo, str) or tipo not in TIPOS:
        r.erro(lugar, "C004", tr(f"tipo `{tipo}` desconhecido; use um de: {', '.join(TIPOS)}",
                                     f"unknown type `{tipo}`; use one of: {', '.join(TIPOS)}"))
        return None
    flags = _flags(item, lugar, r)
    tamanho, casas = _medidas(item, tipo, lugar, r)
    alvo = None
    if tipo == "lookup":
        alvo = item["alvo"].strip() if _texto(item.get("alvo")) else None
        if alvo is None:
            r.erro(lugar, "C006", tr("Lookup precisa de `alvo`: o nome de outra tabela do spec",
                                         "Lookup needs `alvo`: the name of another table in the spec"))
    exemplos = None
    if "exemplos" in item:
        if isinstance(item["exemplos"], list) and item["exemplos"]:
            exemplos = tuple(item["exemplos"])
        else:
            r.erro(lugar, "C008", tr("`exemplos` precisa ser uma lista com pelo menos um valor",
                                        "`exemplos` must be a list with at least one value"))
    return Coluna(nome, tipo, flags["obrigatoria"], flags["primaria"], flags["chave"], tamanho, casas,
                  _opcoes(item, tipo, lugar, r), alvo, exemplos, _opcional(item, "sql"), _opcional(item, "logico"))


# ---------- estrutura ----------

def _ident_sql(nome: str | None, partes: int) -> bool:
    if not nome:
        return False
    pedacos = nome.split(".")
    return len(pedacos) <= partes and all(IDENT_SQL.fullmatch(p) for p in pedacos)


def _checar_nomes_tabelas(spec: Spec, r: Relato) -> None:
    vistos: set[str] = set()
    for t in spec.tabelas:
        chave = t.nome.casefold()
        if chave in vistos:
            r.erro(t.nome, "C003", tr("tabela repetida (o nome da aba não diferencia maiúscula)",
                                      "repeated table (the sheet name is case-insensitive)"))
        vistos.add(chave)
        invalido = (_u16(t.nome) > MAX_ABA or ABA_PROIBIDO.search(t.nome) or t.nome.startswith("'")
                    or t.nome.endswith("'") or CONTROLES.search(t.nome))
        if invalido:
            r.erro(t.nome, "C003", tr("nome de aba inválido: até 31 caracteres, sem : \\ / ? * [ ] e sem aspa nas pontas",
                                      "invalid sheet name: up to 31 characters, without : \\ / ? * [ ] and no quote at the ends"))
        if chave in {ABA_CONFERENCIA.casefold(), "history"}:
            r.erro(t.nome, "C003", tr("nome reservado para aba", "name reserved for a sheet"))


def _checar_colunas(t: Tabela, trilha: str, r: Relato) -> None:
    vistos: set[str] = set()
    for c in t.colunas:
        if c.nome.casefold() in vistos:
            r.erro(f"{t.nome}.{c.nome}", "C004", tr("coluna repetida (o Excel não diferencia maiúscula)",
                                                "repeated column (Excel is case-insensitive)"))
        vistos.add(c.nome.casefold())
    primarias = [c for c in t.colunas if c.primaria]
    if trilha == "dataverse" and len(primarias) != 1:
        r.erro(t.nome, "C005", tr(f"a tabela precisa de uma coluna `primaria` (o nome principal do Dataverse); tem {len(primarias)}",
                                  f"the table needs one `primaria` column (the Dataverse primary name); it has {len(primarias)}"))
    elif len(primarias) > 1:
        r.erro(t.nome, "C005", tr(f"no máximo uma coluna `primaria`; tem {len(primarias)}",
                                  f"at most one `primaria` column; it has {len(primarias)}"))
    for c in primarias:
        if c.tipo not in PRIMARIA_OK:
            r.erro(f"{t.nome}.{c.nome}", "C005", tr(f"a primária precisa ser {', '.join(sorted(PRIMARIA_OK))}, não `{c.tipo}`",
                                                f"the primary must be {', '.join(sorted(PRIMARIA_OK))}, not `{c.tipo}`"))
    chaves = [c for c in t.colunas if c.chave]
    if len(chaves) > 1:
        r.erro(t.nome, "C005", tr("uma `chave` por tabela; chave composta se cria à mão",
                                  "one `chave` per table; a composite key is created by hand"))
    for c in chaves:
        if c.tipo not in CHAVE_OK:
            r.erro(f"{t.nome}.{c.nome}", "C005", tr(f"`chave` não vale para `{c.tipo}`", f"`chave` does not apply to `{c.tipo}`"))


def _checar_sql(t: Tabela, r: Relato) -> None:
    if not _ident_sql(t.sql, 2):
        r.erro(t.nome, "C009", tr("a trilha SQL precisa de `sql` com o nome da tabela no DDL (`schema.Tabela`)",
                                  "the SQL track needs `sql` with the table name in the DDL (`schema.Table`)"))
    if t.pk is not None and not _ident_sql(t.pk, 1):
        r.erro(t.nome, "C009", tr(f"`pk` inválida: `{t.pk}`", f"invalid `pk`: `{t.pk}`"))
    for c in t.colunas:
        if na_carga(c, "sql-server") and not _ident_sql(c.sql, 1):
            r.erro(f"{t.nome}.{c.nome}", "C009", tr("a trilha SQL precisa de `sql` com o nome da coluna no DDL",
                                                "the SQL track needs `sql` with the column name in the DDL"))


def _checar_alvos(spec: Spec, trilha: str, r: Relato) -> None:
    por_nome = {t.nome.casefold(): t for t in spec.tabelas}
    for t in spec.tabelas:
        for c in t.colunas:
            if c.tipo != "lookup" or c.alvo is None:
                continue
            lugar, alvo = f"{t.nome}.{c.nome}", por_nome.get(c.alvo.casefold())
            if alvo is None:
                r.erro(lugar, "C006", tr(f"o alvo `{c.alvo}` não é tabela do spec", f"the target `{c.alvo}` is not a table in the spec"))
                continue
            ref = alvo.referencia(trilha)
            if ref is None:
                r.erro(lugar, "C006", tr(f"`{alvo.nome}` não tem `chave` nem `primaria`: o Lookup não tem como apontar",
                                     f"`{alvo.nome}` has no `chave` or `primaria`: the Lookup has nothing to point to"))
            elif trilha == "sql-server" and ref.tipo in GERADO_PELO_BANCO:
                r.erro(lugar, "C009", tr(f"o Lookup acharia a linha por `{ref.nome}` ({ref.tipo}), que o banco gera; "
                                         f"marque outra coluna de `{alvo.nome}` como `chave`",
                                         f"the Lookup would find the row by `{ref.nome}` ({ref.tipo}), which the "
                                         f"database generates; mark another column of `{alvo.nome}` as `chave`"))


def conferir_estrutura(spec: Spec, trilha: str, r: Relato) -> None:
    _checar_nomes_tabelas(spec, r)
    for t in spec.tabelas:
        _checar_colunas(t, trilha, r)
        if not any(na_carga(c, trilha) for c in t.colunas):
            r.erro(t.nome, "C003", tr("nenhuma coluna entra na carga (todas são geradas pelo banco ou criadas à mão)",
                                      "no column goes into the load (all are generated by the database or created by hand)"))
        if trilha == "sql-server":
            _checar_sql(t, r)
    _checar_alvos(spec, trilha, r)


def _no_ciclo(pendentes: list[Tabela], deps: dict[str, set[str]]) -> list[str]:
    """Das tabelas que sobraram, tira as que só dependem do ciclo sem fazer parte dele."""
    restantes = [t.nome for t in pendentes]
    while True:
        apontadas = {d for nome in restantes for d in deps[nome]}
        fora = [nome for nome in restantes if nome not in apontadas]
        if not fora:
            return restantes
        restantes = [nome for nome in restantes if nome not in fora]


def ordem_de_carga(spec: Spec) -> tuple[list[Tabela], list[str]]:
    """Ordem em que cada tabela só aponta para tabela já carregada; devolve também as que formam ciclo."""
    por_nome = {t.nome.casefold(): t for t in spec.tabelas}
    deps = {
        t.nome: {por_nome[c.alvo.casefold()].nome for c in t.colunas
                 if c.tipo == "lookup" and c.alvo and c.alvo.casefold() in por_nome} - {t.nome}
        for t in spec.tabelas
    }
    ordem: list[Tabela] = []
    feitas: set[str] = set()
    pendentes = list(spec.tabelas)
    while pendentes:
        pronta = next((t for t in pendentes if deps[t.nome] <= feitas), None)
        if pronta is None:
            return ordem, _no_ciclo(pendentes, deps)
        ordem.append(pronta)
        feitas.add(pronta.nome)
        pendentes.remove(pronta)
    return ordem, []


# ---------- avisos ----------

def _dominio_real(valor: Any) -> str | None:
    if not isinstance(valor, str):
        return None
    for achado in (*EMAIL.finditer(valor), *URL.finditer(valor)):
        dominio = achado.group(1).lower()
        if not any(dominio == d or dominio.endswith("." + d) for d in DOMINIOS_FICTICIOS):
            return dominio
    return None


def _avisar_fora(c: Coluna, lugar: str, trilha: str, flow: bool, r: Relato) -> None:
    if flow and c.tipo == "calculada":
        r.aviso(lugar, "C010", tr("o construtor não cria coluna calculada: crie à mão no maker, depois das colunas "
                                  "que ela usa",
                                  "the builder does not create calculated columns: create it by hand in the maker, "
                                  "after the columns it uses"))
    elif not flow and (c.tipo in FORA_DA_CARGA or (trilha == "dataverse" and c.tipo == "calculada")):
        r.aviso(lugar, "C010", tr(f"`{c.tipo}` fica fora da carga: a importação não aceita; crie a coluna à mão",
                                  f"`{c.tipo}` stays out of the load: the import does not accept it; create the column by hand"))


def avisar(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], trilha: str, r: Relato,
           flow: bool = False) -> None:
    for t in ordem:
        n = len(linhas[t.nome])
        for c in t.colunas:
            lugar = f"{t.nome}.{c.nome}"
            _avisar_fora(c, lugar, trilha, flow, r)
            dominio = next((d for d in map(_dominio_real, (l.get(c.nome) for l in linhas[t.nome])) if d), None)
            if dominio:
                r.aviso(lugar, "C012", tr(f"`{dominio}` não é domínio fictício (contoso.com, example.com): "
                                          "carga mockup só leva dado inventado",
                                          f"`{dominio}` is not a fictitious domain (contoso.com, example.com): "
                                          "the mockup load only takes made-up data"))
            if trilha != "dataverse" or flow:
                continue
            if c.tipo == "choice" and len(c.opcoes) > n:
                r.aviso(lugar, "C011", tr(f"{len(c.opcoes)} opções e {n} linha(s): a planilha não mostra todas; "
                                          "se o Dataverse deduzir Escolha, crie as que faltam",
                                          f"{len(c.opcoes)} options and {n} row(s): the spreadsheet does not show all "
                                          "of them; if Dataverse infers a Choice, create the missing ones"))
            if c.tipo == "lookup":
                r.aviso(lugar, "C014", tr(f"Lookup para `{c.alvo}`: a importação cria coluna de texto. Crie a Pesquisa "
                                          "e apague a de texto antes da carga real (texto não vira Lookup)",
                                          f"Lookup to `{c.alvo}`: the import creates a text column. Create the Lookup "
                                          "and delete the text one before the real load (text does not turn into a "
                                          "Lookup)"))
            elif c.tipo == "choice":
                r.aviso(lugar, "C014", tr("Choice: pode vir como texto ou só com as opções que apareceram; confira "
                                          f"as opções ({', '.join(c.opcoes)}) antes da carga real",
                                          "Choice: it may come as text or with only the options that appeared; check "
                                          f"the options ({', '.join(c.opcoes)}) before the real load"))
    total = sum(1 for t in ordem for c in t.colunas if not (flow and c.tipo == "calculada"))
    if trilha == "dataverse" and flow:
        r.aviso("spec", "C018", tr(f"o construtor cria as {total} colunas com o tipo do spec: depois de rodar o flow, "
                                   "prove com --conferir e o export do ambiente (0 erro(s)) antes do dado real; a "
                                   "planilha fica de referência",
                                   f"the builder creates the {total} columns with the spec's type: after running the "
                                   "flow, prove it with --conferir and the environment export (0 error(s)) before "
                                   "the real data; the spreadsheet stays as a reference"))
    elif trilha == "dataverse":
        r.aviso("spec", "C013", tr(f"o Dataverse deduz o tipo de cada coluna pelos dados e erra com frequência: depois "
                                   f"de importar, confira as {total} colunas (aba `{ABA_CONFERENCIA}`) e rode "
                                   "--conferir com o export do ambiente antes de carregar dado real",
                                   f"Dataverse infers each column's type from the data and often gets it wrong: after "
                                   f"importing, check the {total} columns (sheet `{ABA_CONFERENCIA}`) and run "
                                   "--conferir with the environment export before loading real data"))


# ---------- abas ----------

def aba_da_tabela(t: Tabela, linhas: list[dict[str, Any]], trilha: str) -> Aba:
    colunas = [c for c in t.colunas if na_carga(c, trilha)]
    return Aba(t.nome, tuple(c.nome for c in colunas),
               tuple(tuple(linha[c.nome] for c in colunas) for linha in linhas),
               tuple(TIPOS[c.tipo].estilo for c in colunas))


def _escolha(c: Coluna) -> str:
    rotulo = TIPOS[c.tipo].rotulo
    if c.opcoes:
        rotulo += ": " + "; ".join(c.opcoes)
    if c.tipo == "lookup":
        rotulo += f" → {c.alvo}"
    if c.tamanho:
        rotulo += tr(f", até {c.tamanho} caracteres", f", up to {c.tamanho} characters")
    if c.primaria:
        rotulo += tr(" · nome principal (não muda depois de criada)", " · primary name (cannot change once created)")
    if c.chave:
        rotulo += tr(" · chave alternativa", " · alternate key")
    return rotulo


def aba_conferencia(ordem: list[Tabela]) -> Aba:
    linhas = []
    for t in ordem:
        for c in t.colunas:
            marcas = [m for m, sim in ((tr("primária", "primary"), c.primaria), (tr("chave", "key"), c.chave),
                       (tr("obrigatória", "required"), c.obrigatoria))
                      if sim]
            linhas.append((t.nome, c.nome, " · ".join([c.tipo, *marcas]), _escolha(c), TIPOS[c.tipo].erro_comum,
                           None, None))
    return Aba(
        ABA_CONFERENCIA,
        tr(("Tabela", "Coluna", "Tipo no modelo", "Escolha no Dataverse", "O que costuma vir errado", "Veio como",
            "Conferido"),
           ("Table", "Column", "Type in the model", "Choice in Dataverse", "What usually goes wrong", "Came as",
            "Checked")),
        tuple(linhas), (EST_QUEBRA,) * 7,
        titulo=(tr("Confira cada coluna depois de importar: o Dataverse deduz o tipo pelos dados e erra com frequência.",
                   "Check each column after importing: Dataverse infers the type from the data and often gets it wrong."),
                tr("Escolha (Choice) e Pesquisa (Lookup) chegam como texto: recrie com o tipo certo antes da carga real. "
                   "Prova: montar-carga-mockup.py <spec> --conferir <export.json> com 0 erro(s).",
                   "Choice and Lookup arrive as text: recreate them with the right type before the real load. "
                   "Proof: montar-carga-mockup.py <spec> --conferir <export.json> with 0 error(s).")),
        larguras=(16, 24, 22, 44, 44, 18, 12),
    )


# ---------- CLI ----------

def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_CONFIG
        if candidato.is_file():
            return candidato
    return None


def _rotulo(caminho: Path) -> str:
    try:
        return caminho.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return caminho.as_posix()


def _saida_utf8() -> None:
    """Console do Windows em cp1252 quebraria os acentos dos nomes de coluna."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _uso(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 2


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=tr("Monta a carga mockup das tabelas (/pp:arquitetura): .xlsx com dados fictícios para o "
                       "Dataverse deduzir os tipos e, na trilha SQL, o script de INSERT para o banco de DEV.",
                       "Builds the mockup load for the tables (/pp-en:architecture): an .xlsx with fictitious data "
                       "for Dataverse to infer the types and, on the SQL track, the INSERT script for the DEV "
                       "database."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=tr(
            f"Tipos: {', '.join(TIPOS)}.\n\n"
            "Códigos: C001 spec, C002 trilha, C003 tabela, C004 coluna, C005 primária e chave, C006 Choice e\n"
            "Lookup, C007 dependência circular, C008 exemplo, C009 nome SQL, C010 coluna fora da carga,\n"
            "C011 opção que não aparece, C012 domínio real, C013 confira a tipagem, C014 Choice/Lookup vira\n"
            "texto, C015 falha ao gravar; --conferir: C101 tabela ausente, C102 coluna ausente, C103 tipo\n"
            "diferente, C104 o que o export não prova, C105 nome principal; --flow: C016 nome lógico, C017\n"
            "limite do Dataverse, C018 prove com --conferir depois do construtor.\n"
            "Sem --saida e sem --conferir: só valida e mostra o plano.",
            f"Types: {', '.join(TIPOS)}.\n\n"
            "Codes: C001 spec, C002 track, C003 table, C004 column, C005 primary and key, C006 Choice and\n"
            "Lookup, C007 circular dependency, C008 example, C009 SQL name, C010 column outside the load,\n"
            "C011 option that does not show up, C012 real domain, C013 check the typing, C014 Choice/Lookup\n"
            "becomes text, C015 write failure; --conferir: C101 missing table, C102 missing column, C103\n"
            "different type, C104 what the export does not prove, C105 primary name; --flow: C016 logical\n"
            "name, C017 Dataverse limit, C018 prove it with --conferir after the builder.\n"
            "Without --saida and without --conferir: only validates and shows the plan."
        ),
    )
    ap.add_argument("spec", type=Path, help=tr("carga-mockup.json (molde em assets/carga-mockup-molde.json)",
                    "mockup-load.json (template in assets/mockup-load-template.json)"))
    ap.add_argument("--trilha", choices=TRILHAS, help=tr("sobrepõe `trilha_dados` do config e `trilha` do spec",
                                                      "overrides `trilha_dados` from the config and `trilha` from the spec"))
    ap.add_argument("--saida", type=Path, help=tr(f"pasta onde gravar {ARQ_XLSX} (e {ARQ_SQL} na trilha SQL)",
                                                  f"folder where to write {ARQ_XLSX} (and {ARQ_SQL} on the SQL track)"))
    ap.add_argument("--uma-por-tabela", action="store_true",
                    help=tr(f"grava também {PASTA_POR_TABELA}/NN-<tabela>.xlsx, um arquivo por tabela",
                         f"also writes {PASTA_POR_TABELA}/NN-<table>.xlsx, one file per table"))
    ap.add_argument("--linhas", type=int, help=tr(f"linhas por tabela, de 1 a {MAX_LINHAS} (default {LINHAS_PADRAO})",
                                         f"rows per table, from 1 to {MAX_LINHAS} (default {LINHAS_PADRAO})"))
    ap.add_argument("--conferir", type=Path, metavar="EXPORT_JSON",
                    help=tr("export da Web API (EntityDefinitions + Attributes): compara os tipos criados com o spec",
                       "Web API export (EntityDefinitions + Attributes): compares the created types with the spec"))
    ap.add_argument("--flow", action="store_true",
                    help=tr(f"trilha Dataverse: grava também {ARQ_PLANO} e o flow construtor (.zip e escopo para colar)",
                         f"Dataverse track: also writes {ARQ_PLANO} and the builder flow (.zip and scope to paste)"))
    ap.add_argument("--idioma", type=int, default=IDIOMA_PADRAO,
                    help=tr(f"idioma da solução do construtor: o idioma base do ambiente (default {IDIOMA_PADRAO} pt-BR; "
                            "1033 inglês)",
                            f"language of the builder solution: the environment's base language (default "
                            f"{IDIOMA_PADRAO}, pt-BR; 1033 English)"))
    ap.add_argument("--config", type=Path, help=tr(f"caminho do {NOME_CONFIG} (default: procura para cima)",
                                                    f"path of {NOME_CONFIG} (default: searches upward)"))
    return ap.parse_args(argv)


def _ler_json(caminho: Path, o_que: str) -> Any:
    if not caminho.is_file():
        raise ValueError(tr(f"{o_que} inexistente: {caminho}", f"{o_que} not found: {caminho}"))
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
        json.dumps(dados, ensure_ascii=False).encode("utf-8")  # recusa já na entrada o surrogate solto
    except (ValueError, OSError, RecursionError) as erro:
        raise ValueError(tr(f"{o_que} ilegível ({caminho}): {erro}", f"{o_que} unreadable ({caminho}): {erro}")) from erro
    return dados


def _trilha_do_config(caminho: Path | None) -> str | None:
    caminho = caminho or achar_config(Path.cwd())
    if caminho is None:
        print(tr("# config: nenhuma encontrada -- defaults genéricos", "# config: none found -- generic defaults"))
        return None
    config = _ler_json(caminho, "config")
    if not isinstance(config, dict):
        raise ValueError(tr(f"config inválida ({caminho}): a raiz precisa ser um objeto",
                            f"invalid config ({caminho}): the root must be an object"))
    trilha = config.get("trilha_dados")
    if trilha is not None and trilha not in TRILHAS:
        raise ValueError(tr(f"config inválida ({caminho}): `trilha_dados` precisa ser {' ou '.join(TRILHAS)}",
                            f"invalid config ({caminho}): `trilha_dados` must be {' or '.join(TRILHAS)}"))
    print(f"# config: {caminho.name}")
    return trilha


def decidir_trilha(opcao: str | None, do_config: str | None, spec: Spec | None, r: Relato) -> str | None:
    efetiva = opcao or do_config or (spec.trilha if spec else None)
    if efetiva is None:
        r.erro("spec", "C002", tr("trilha indefinida: passe --trilha, grave `trilha_dados` no config ou `trilha` no spec",
                                  "track undefined: pass --trilha, set `trilha_dados` in the config or `trilha` in the spec"))
    elif spec and spec.trilha and spec.trilha != efetiva:
        r.erro("spec", "C002", tr(f"o spec diz `{spec.trilha}` e o projeto está em `{efetiva}`: uma trilha só",
                                  f"the spec says `{spec.trilha}` and the project is on `{efetiva}`: one track only"))
    return efetiva


def _plano(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]]) -> None:
    print(tr(f"# ordem de carga: {' → '.join(t.nome for t in ordem)}", f"# load order: {' → '.join(t.nome for t in ordem)}"))
    for t in ordem:
        colunas = ", ".join(
            f"{c.nome} ({c.tipo}{tr(', primária', ', primary') if c.primaria else ''}"
            f"{tr(', chave', ', key') if c.chave else ''})" for c in t.colunas)
        n = len(linhas.get(t.nome, []))
        print(tr(f"# {t.nome}: {n} linha(s) · {colunas}", f"# {t.nome}: {n} row(s) · {colunas}"))


def _nome_arquivo(nome: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", nome).strip(" .") or tr("tabela", "table")


def gravar_atomico(destino: Path, dados: bytes) -> None:
    """Grava num .tmp e troca: interrupção no meio nunca deixa arquivo truncado com o nome final."""
    temporario = destino.with_name(destino.name + ".tmp")
    try:
        temporario.write_bytes(dados)
        os.replace(temporario, destino)
    finally:
        temporario.unlink(missing_ok=True)


def gravar_saidas(saida: Path, ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], trilha: str,
                  uma_por_tabela: bool, origem: str, plano: dict[str, Any] | None = None,
                  idioma: int = IDIOMA_PADRAO) -> list[Achado]:
    abas = [aba_da_tabela(t, linhas[t.nome], trilha) for t in ordem]
    arquivos = [(saida / ARQ_XLSX, lambda: xlsx(abas + ([aba_conferencia(ordem)] if trilha == "dataverse" else [])))]
    if trilha == "sql-server":
        arquivos.append((saida / ARQ_SQL, lambda: script_sql(ordem, linhas, origem).encode("utf-8-sig")))
    if uma_por_tabela:
        for n, (t, aba) in enumerate(zip(ordem, abas), start=1):
            destino = saida / PASTA_POR_TABELA / f"{n:02d}-{_nome_arquivo(t.nome)}.xlsx"
            arquivos.append((destino, lambda aba=aba: xlsx([aba])))
    if plano is not None:
        arquivos.append((saida / ARQ_PLANO, lambda: plano_em_bytes(plano)))
        arquivos += [(saida / caminho, conteudo) for caminho, conteudo in arquivos_do_construtor(idioma)]
    return _gravar_todos(saida, arquivos)


def _gravar_todos(saida: Path, arquivos: list[tuple[Path, Any]]) -> list[Achado]:
    """Monta todos os bytes antes de gravar o primeiro arquivo: falha ao montar não deixa saída pela metade."""
    try:
        prontos = [(destino, conteudo()) for destino, conteudo in arquivos]
    except (OSError, ValueError) as erro:
        return [Achado(_rotulo(saida), "-", "ERRO", "C015", tr(f"não montou as saídas: {erro}", f"could not build the outputs: {erro}"))]
    achados = []
    for destino, dados in prontos:
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            gravar_atomico(destino, dados)
            print(tr(f"# gravado: {_rotulo(destino)}", f"# written: {_rotulo(destino)}"))
        except OSError as erro:
            dica = tr(" (o arquivo está aberto no Excel?)", " (is the file open in Excel?)") if isinstance(erro, PermissionError) else ""
            achados.append(Achado(_rotulo(destino), "-", "ERRO", "C015",
                                  tr(f"não gravou: {erro.strerror or erro}{dica}", f"could not write: {erro.strerror or erro}{dica}")))
    return achados


def _fechar(achados: list[Achado]) -> int:
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(tr(f"{erros} erro(s), {len(achados) - erros} aviso(s)", f"{erros} error(s), {len(achados) - erros} warning(s)"))
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    if args.linhas is not None and not 1 <= args.linhas <= MAX_LINHAS:
        return _uso(tr(f"--linhas precisa ser de 1 a {MAX_LINHAS}", f"--linhas must be from 1 to {MAX_LINHAS}"))
    if args.saida is not None and args.saida.exists() and not args.saida.is_dir():
        return _uso(tr(f"--saida precisa ser uma pasta: {args.saida}", f"--saida must be a folder: {args.saida}"))
    if not 1 <= args.idioma <= 99999:
        return _uso(tr("--idioma é o código do idioma base do ambiente, como 1046 (pt-BR) ou 1033 (inglês)",
                       "--idioma is the environment base language code, such as 1046 (pt-BR) or 1033 (English)"))
    if args.flow and args.conferir:
        return _uso(tr("--flow e --conferir são etapas diferentes: gere o plano, rode o flow e só depois confira",
                       "--flow and --conferir are different steps: generate the plan, run the flow and only then check"))
    try:
        dados = _ler_json(args.spec, "spec")
        do_config = _trilha_do_config(args.config) if args.config or not args.trilha else None
        export = _ler_json(args.conferir, "export") if args.conferir else None
    except ValueError as erro:
        return _uso(str(erro))
    r = Relato(_rotulo(args.spec))
    spec = ler_spec(dados, r)
    trilha = decidir_trilha(args.trilha, do_config, spec, r)
    print(tr(f"# trilha: {trilha or '?'}", f"# track: {trilha or '?'}"))
    if spec is None or trilha is None:
        return _fechar(r.achados)
    if args.conferir and trilha != "dataverse":
        return _uso(tr("--conferir só vale na trilha dataverse: no SQL o tipo é o do DDL",
                       "--conferir only applies to the dataverse track: in SQL the type is the DDL one"))
    if args.flow and trilha != "dataverse":
        return _uso(tr("--flow só vale na trilha dataverse: no SQL a estrutura vem do DDL e a carga do .sql",
                       "--flow only applies to the dataverse track: in SQL the structure comes from the DDL and the load from the .sql"))
    conferir_estrutura(spec, trilha, r)
    ordem, ciclo = ordem_de_carga(spec)
    if ciclo:
        r.erro("spec", "C007", tr(f"dependência circular de Lookup entre {', '.join(ciclo)}: carregue uma delas sem "
                                  "o Lookup e preencha depois, ou quebre o ciclo no modelo",
                                  f"circular Lookup dependency between {', '.join(ciclo)}: load one of them without "
                                  "the Lookup and fill it in later, or break the cycle in the model"))
    if r.tem_erro:
        return _fechar(r.achados)
    if export is not None:
        entidades = entidades_do_export(export)
        if entidades is None:
            return _uso(tr("export sem entidades: use a resposta de EntityDefinitions com $expand=Attributes",
                           "export without entities: use the EntityDefinitions response with $expand=Attributes"))
        print(tr(f"# conferência: {_rotulo(args.conferir)} × {r.arquivo}", f"# check: {_rotulo(args.conferir)} × {r.arquivo}"))
        ambiente = Relato(_rotulo(args.conferir))
        conferir_ambiente(ordem, entidades, ambiente)
        return _fechar(r.achados + ambiente.achados)
    linhas = montar_valores(ordem, spec, args.linhas, trilha, r)
    _plano(ordem, linhas)
    plano = montar_plano(ordem, linhas, args.spec.name, r) if args.flow and not r.tem_erro else None
    if plano is not None:
        print(tr(f"# construtor: {resumo_texto(plano)}", f"# builder: {resumo_texto(plano)}"))
    if not r.tem_erro:
        avisar(ordem, linhas, trilha, r, args.flow)
    if args.saida is not None and not r.tem_erro:
        r.achados.extend(gravar_saidas(args.saida, ordem, linhas, trilha, args.uma_por_tabela, args.spec.name,
                                       plano, args.idioma))
    return _fechar(r.achados)


if __name__ == "__main__":
    sys.exit(main())
