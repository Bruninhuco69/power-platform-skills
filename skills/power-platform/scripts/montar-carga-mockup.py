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

NOME_CONFIG = "power-platform.config.json"
TRILHAS = ("dataverse", "sql-server")
MAX_LINHAS = 200
DATA_BASE_PADRAO = date(2026, 1, 13)
IDIOMA_PADRAO = 1046  # pt-BR: idioma da solução do construtor (.zip)
ABA_CONFERENCIA = "Conferência de tipos"
ARQ_XLSX = "carga-mockup.xlsx"
PASTA_POR_TABELA = "carga-mockup-tabelas"
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
        r.erro("spec", "C001", "a raiz precisa ser um objeto com `tabelas`, uma lista com pelo menos uma tabela")
        return None
    linhas = _inteiro_em(dados.get("linhas"), 1, MAX_LINHAS)
    if "linhas" in dados and linhas is None:
        r.erro("spec", "C001", f"`linhas` precisa ser inteiro de 1 a {MAX_LINHAS}")
    data_base = DATA_BASE_PADRAO
    if "data_base" in dados:
        data_base = _data(dados["data_base"]) or DATA_BASE_PADRAO
        if _data(dados["data_base"]) is None:
            r.erro("spec", "C001", "`data_base` precisa ser uma data AAAA-MM-DD")
        elif date.max - data_base < timedelta(days=6 * MAX_LINHAS):  # de 3 em 3, pulando os dias 1 a 12
            r.erro("spec", "C001", "`data_base` perto demais do fim do calendário: as datas geradas não cabem")
            data_base = DATA_BASE_PADRAO
    trilha = dados.get("trilha")
    if trilha is not None and trilha not in TRILHAS:
        r.erro("spec", "C002", f"`trilha` precisa ser {' ou '.join(TRILHAS)}")
        trilha = None
    tabelas = (ler_tabela(item, n, r) for n, item in enumerate(dados["tabelas"], start=1))
    return Spec(tuple(t for t in tabelas if t), linhas, data_base, trilha)


def ler_tabela(item: Any, numero: int, r: Relato) -> Tabela | None:
    if not isinstance(item, dict) or not _texto(item.get("nome")):
        r.erro(f"tabelas[{numero}]", "C003", "tabela sem `nome`")
        return None
    nome = item["nome"].strip()
    if not isinstance(item.get("colunas"), list) or not item["colunas"]:
        r.erro(nome, "C003", "tabela sem `colunas`")
        return None
    linhas = None
    if "linhas" in item:
        linhas = _inteiro_em(item["linhas"], 1, MAX_LINHAS)
        if linhas is None:
            r.erro(nome, "C003", f"`linhas` precisa ser inteiro de 1 a {MAX_LINHAS}")
    colunas = (ler_coluna(c, nome, k, r) for k, c in enumerate(item["colunas"], start=1))
    return Tabela(nome, tuple(c for c in colunas if c), linhas,
                  _opcional(item, "sql"), _opcional(item, "pk"), _opcional(item, "logico"))


def _flags(item: dict, lugar: str, r: Relato) -> dict[str, bool]:
    flags = {}
    for flag in ("obrigatoria", "primaria", "chave"):
        valor = item.get(flag, False)
        if not isinstance(valor, bool):
            r.erro(lugar, "C004", f"`{flag}` precisa ser true ou false")
            valor = False
        flags[flag] = valor
    return flags


def _medidas(item: dict, tipo: str, lugar: str, r: Relato) -> tuple[int | None, int]:
    tamanho, casas = None, CASAS_PADRAO
    if "tamanho" in item:
        tamanho = _inteiro_em(item["tamanho"], 1, 1_048_576)
        if tamanho is None or tipo not in COM_TAMANHO:
            r.erro(lugar, "C004", "`tamanho` é inteiro positivo e só vale para coluna de texto")
            tamanho = None
    if "casas" in item:
        casas = _inteiro_em(item["casas"], 0, 10)
        if casas is None or tipo not in COM_CASAS:
            r.erro(lugar, "C004", "`casas` é inteiro de 0 a 10 e só vale para decimal e moeda")
            casas = CASAS_PADRAO
    return tamanho, casas


def _opcoes(item: dict, tipo: str, lugar: str, r: Relato) -> tuple[str, ...]:
    if tipo not in COM_OPCOES:
        return ()
    opcoes = item.get("opcoes")
    validas = isinstance(opcoes, list) and opcoes and all(_texto(o) for o in opcoes)
    if not validas or len({o.strip().casefold() for o in opcoes}) != len(opcoes):
        r.erro(lugar, "C006", "Choice precisa de `opcoes`: lista de rótulos de texto, sem repetição")
        return ()
    return tuple(o.strip() for o in opcoes)


def ler_coluna(item: Any, tabela: str, numero: int, r: Relato) -> Coluna | None:
    if not isinstance(item, dict) or not _texto(item.get("nome")):
        r.erro(f"{tabela}.colunas[{numero}]", "C004", "coluna sem `nome`")
        return None
    nome = item["nome"].strip()
    lugar = f"{tabela}.{nome}"
    if CONTROLES.search(nome):
        r.erro(lugar, "C004", "nome com quebra de linha ou caractere de controle")
        return None
    if _u16(nome) > MAX_CABECALHO:
        r.erro(lugar, "C004", f"nome com mais de {MAX_CABECALHO} caracteres: o Excel não abre")
        return None
    tipo = item.get("tipo")
    if not isinstance(tipo, str) or tipo not in TIPOS:
        r.erro(lugar, "C004", f"tipo `{tipo}` desconhecido; use um de: {', '.join(TIPOS)}")
        return None
    flags = _flags(item, lugar, r)
    tamanho, casas = _medidas(item, tipo, lugar, r)
    alvo = None
    if tipo == "lookup":
        alvo = item["alvo"].strip() if _texto(item.get("alvo")) else None
        if alvo is None:
            r.erro(lugar, "C006", "Lookup precisa de `alvo`: o nome de outra tabela do spec")
    exemplos = None
    if "exemplos" in item:
        if isinstance(item["exemplos"], list) and item["exemplos"]:
            exemplos = tuple(item["exemplos"])
        else:
            r.erro(lugar, "C008", "`exemplos` precisa ser uma lista com pelo menos um valor")
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
            r.erro(t.nome, "C003", "tabela repetida (o nome da aba não diferencia maiúscula)")
        vistos.add(chave)
        invalido = (_u16(t.nome) > MAX_ABA or ABA_PROIBIDO.search(t.nome) or t.nome.startswith("'")
                    or t.nome.endswith("'") or CONTROLES.search(t.nome))
        if invalido:
            r.erro(t.nome, "C003", "nome de aba inválido: até 31 caracteres, sem : \\ / ? * [ ] e sem aspa nas pontas")
        if chave in {ABA_CONFERENCIA.casefold(), "history"}:
            r.erro(t.nome, "C003", "nome reservado para aba")


def _checar_colunas(t: Tabela, trilha: str, r: Relato) -> None:
    vistos: set[str] = set()
    for c in t.colunas:
        if c.nome.casefold() in vistos:
            r.erro(f"{t.nome}.{c.nome}", "C004", "coluna repetida (o Excel não diferencia maiúscula)")
        vistos.add(c.nome.casefold())
    primarias = [c for c in t.colunas if c.primaria]
    if trilha == "dataverse" and len(primarias) != 1:
        r.erro(t.nome, "C005", f"a tabela precisa de uma coluna `primaria` (o nome principal do Dataverse); tem {len(primarias)}")
    elif len(primarias) > 1:
        r.erro(t.nome, "C005", f"no máximo uma coluna `primaria`; tem {len(primarias)}")
    for c in primarias:
        if c.tipo not in PRIMARIA_OK:
            r.erro(f"{t.nome}.{c.nome}", "C005", f"a primária precisa ser {', '.join(sorted(PRIMARIA_OK))}, não `{c.tipo}`")
    chaves = [c for c in t.colunas if c.chave]
    if len(chaves) > 1:
        r.erro(t.nome, "C005", "uma `chave` por tabela; chave composta se cria à mão")
    for c in chaves:
        if c.tipo not in CHAVE_OK:
            r.erro(f"{t.nome}.{c.nome}", "C005", f"`chave` não vale para `{c.tipo}`")


def _checar_sql(t: Tabela, r: Relato) -> None:
    if not _ident_sql(t.sql, 2):
        r.erro(t.nome, "C009", "a trilha SQL precisa de `sql` com o nome da tabela no DDL (`schema.Tabela`)")
    if t.pk is not None and not _ident_sql(t.pk, 1):
        r.erro(t.nome, "C009", f"`pk` inválida: `{t.pk}`")
    for c in t.colunas:
        if na_carga(c, "sql-server") and not _ident_sql(c.sql, 1):
            r.erro(f"{t.nome}.{c.nome}", "C009", "a trilha SQL precisa de `sql` com o nome da coluna no DDL")


def _checar_alvos(spec: Spec, trilha: str, r: Relato) -> None:
    por_nome = {t.nome.casefold(): t for t in spec.tabelas}
    for t in spec.tabelas:
        for c in t.colunas:
            if c.tipo != "lookup" or c.alvo is None:
                continue
            lugar, alvo = f"{t.nome}.{c.nome}", por_nome.get(c.alvo.casefold())
            if alvo is None:
                r.erro(lugar, "C006", f"o alvo `{c.alvo}` não é tabela do spec")
                continue
            ref = alvo.referencia(trilha)
            if ref is None:
                r.erro(lugar, "C006", f"`{alvo.nome}` não tem `chave` nem `primaria`: o Lookup não tem como apontar")
            elif trilha == "sql-server" and ref.tipo in GERADO_PELO_BANCO:
                r.erro(lugar, "C009", f"o Lookup acharia a linha por `{ref.nome}` ({ref.tipo}), que o banco gera; "
                                      f"marque outra coluna de `{alvo.nome}` como `chave`")


def conferir_estrutura(spec: Spec, trilha: str, r: Relato) -> None:
    _checar_nomes_tabelas(spec, r)
    for t in spec.tabelas:
        _checar_colunas(t, trilha, r)
        if not any(na_carga(c, trilha) for c in t.colunas):
            r.erro(t.nome, "C003", "nenhuma coluna entra na carga (todas são geradas pelo banco ou criadas à mão)")
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
        r.aviso(lugar, "C010", "o construtor não cria coluna calculada: crie à mão no maker, depois das colunas "
                               "que ela usa")
    elif not flow and (c.tipo in FORA_DA_CARGA or (trilha == "dataverse" and c.tipo == "calculada")):
        r.aviso(lugar, "C010", f"`{c.tipo}` fica fora da carga: a importação não aceita; crie a coluna à mão")


def avisar(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], trilha: str, r: Relato,
           flow: bool = False) -> None:
    for t in ordem:
        n = len(linhas[t.nome])
        for c in t.colunas:
            lugar = f"{t.nome}.{c.nome}"
            _avisar_fora(c, lugar, trilha, flow, r)
            dominio = next((d for d in map(_dominio_real, (l.get(c.nome) for l in linhas[t.nome])) if d), None)
            if dominio:
                r.aviso(lugar, "C012", f"`{dominio}` não é domínio fictício (contoso.com, example.com): "
                                       "carga mockup só leva dado inventado")
            if trilha != "dataverse" or flow:
                continue
            if c.tipo == "choice" and len(c.opcoes) > n:
                r.aviso(lugar, "C011", f"{len(c.opcoes)} opções e {n} linha(s): a planilha não mostra todas; "
                                       "se o Dataverse deduzir Escolha, crie as que faltam")
            if c.tipo == "lookup":
                r.aviso(lugar, "C014", f"Lookup para `{c.alvo}`: a importação cria coluna de texto. Crie a Pesquisa "
                                       "e apague a de texto antes da carga real (texto não vira Lookup)")
            elif c.tipo == "choice":
                r.aviso(lugar, "C014", "Choice: pode vir como texto ou só com as opções que apareceram; confira "
                                       f"as opções ({', '.join(c.opcoes)}) antes da carga real")
    total = sum(1 for t in ordem for c in t.colunas if not (flow and c.tipo == "calculada"))
    if trilha == "dataverse" and flow:
        r.aviso("spec", "C018", f"o construtor cria as {total} colunas com o tipo do spec: depois de rodar o flow, "
                                "prove com --conferir e o export do ambiente (0 erro(s)) antes do dado real; a "
                                "planilha fica de referência")
    elif trilha == "dataverse":
        r.aviso("spec", "C013", f"o Dataverse deduz o tipo de cada coluna pelos dados e erra com frequência: depois "
                                f"de importar, confira as {total} colunas (aba `{ABA_CONFERENCIA}`) e rode "
                                "--conferir com o export do ambiente antes de carregar dado real")


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
        rotulo += f", até {c.tamanho} caracteres"
    if c.primaria:
        rotulo += " · nome principal (não muda depois de criada)"
    if c.chave:
        rotulo += " · chave alternativa"
    return rotulo


def aba_conferencia(ordem: list[Tabela]) -> Aba:
    linhas = []
    for t in ordem:
        for c in t.colunas:
            marcas = [m for m, sim in (("primária", c.primaria), ("chave", c.chave), ("obrigatória", c.obrigatoria))
                      if sim]
            linhas.append((t.nome, c.nome, " · ".join([c.tipo, *marcas]), _escolha(c), TIPOS[c.tipo].erro_comum,
                           None, None))
    return Aba(
        ABA_CONFERENCIA,
        ("Tabela", "Coluna", "Tipo no modelo", "Escolha no Dataverse", "O que costuma vir errado", "Veio como",
         "Conferido"),
        tuple(linhas), (EST_QUEBRA,) * 7,
        titulo=("Confira cada coluna depois de importar: o Dataverse deduz o tipo pelos dados e erra com frequência.",
                "Escolha (Choice) e Pesquisa (Lookup) chegam como texto: recrie com o tipo certo antes da carga real. "
                "Prova: montar-carga-mockup.py <spec> --conferir <export.json> com 0 erro(s)."),
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
        description="Monta a carga mockup das tabelas (/pp:arquitetura): .xlsx com dados fictícios para o "
                    "Dataverse deduzir os tipos e, na trilha SQL, o script de INSERT para o banco de DEV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Tipos: {', '.join(TIPOS)}.\n\n"
            "Códigos: C001 spec, C002 trilha, C003 tabela, C004 coluna, C005 primária e chave, C006 Choice e\n"
            "Lookup, C007 dependência circular, C008 exemplo, C009 nome SQL, C010 coluna fora da carga,\n"
            "C011 opção que não aparece, C012 domínio real, C013 confira a tipagem, C014 Choice/Lookup vira\n"
            "texto, C015 falha ao gravar; --conferir: C101 tabela ausente, C102 coluna ausente, C103 tipo\n"
            "diferente, C104 o que o export não prova, C105 nome principal; --flow: C016 nome lógico, C017\n"
            "limite do Dataverse, C018 prove com --conferir depois do construtor.\n"
            "Sem --saida e sem --conferir: só valida e mostra o plano."
        ),
    )
    ap.add_argument("spec", type=Path, help="carga-mockup.json (molde em assets/carga-mockup-molde.json)")
    ap.add_argument("--trilha", choices=TRILHAS, help="sobrepõe `trilha_dados` do config e `trilha` do spec")
    ap.add_argument("--saida", type=Path, help=f"pasta onde gravar {ARQ_XLSX} (e {ARQ_SQL} na trilha SQL)")
    ap.add_argument("--uma-por-tabela", action="store_true",
                    help=f"grava também {PASTA_POR_TABELA}/NN-<tabela>.xlsx, um arquivo por tabela")
    ap.add_argument("--linhas", type=int, help=f"linhas por tabela, de 1 a {MAX_LINHAS} (default {LINHAS_PADRAO})")
    ap.add_argument("--conferir", type=Path, metavar="EXPORT_JSON",
                    help="export da Web API (EntityDefinitions + Attributes): compara os tipos criados com o spec")
    ap.add_argument("--flow", action="store_true",
                    help=f"trilha Dataverse: grava também {ARQ_PLANO} e o flow construtor (.zip e escopo para colar)")
    ap.add_argument("--idioma", type=int, default=IDIOMA_PADRAO,
                    help=f"idioma da solução do construtor: o idioma base do ambiente (default {IDIOMA_PADRAO} pt-BR; "
                         "1033 inglês)")
    ap.add_argument("--config", type=Path, help=f"caminho do {NOME_CONFIG} (default: procura para cima)")
    return ap.parse_args(argv)


def _ler_json(caminho: Path, o_que: str) -> Any:
    if not caminho.is_file():
        raise ValueError(f"{o_que} inexistente: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
        json.dumps(dados, ensure_ascii=False).encode("utf-8")  # recusa já na entrada o surrogate solto
    except (ValueError, OSError, RecursionError) as erro:
        raise ValueError(f"{o_que} ilegível ({caminho}): {erro}") from erro
    return dados


def _trilha_do_config(caminho: Path | None) -> str | None:
    caminho = caminho or achar_config(Path.cwd())
    if caminho is None:
        print("# config: nenhuma encontrada -- defaults genéricos")
        return None
    config = _ler_json(caminho, "config")
    if not isinstance(config, dict):
        raise ValueError(f"config inválida ({caminho}): a raiz precisa ser um objeto")
    trilha = config.get("trilha_dados")
    if trilha is not None and trilha not in TRILHAS:
        raise ValueError(f"config inválida ({caminho}): `trilha_dados` precisa ser {' ou '.join(TRILHAS)}")
    print(f"# config: {caminho.name}")
    return trilha


def decidir_trilha(opcao: str | None, do_config: str | None, spec: Spec | None, r: Relato) -> str | None:
    efetiva = opcao or do_config or (spec.trilha if spec else None)
    if efetiva is None:
        r.erro("spec", "C002", "trilha indefinida: passe --trilha, grave `trilha_dados` no config ou `trilha` no spec")
    elif spec and spec.trilha and spec.trilha != efetiva:
        r.erro("spec", "C002", f"o spec diz `{spec.trilha}` e o projeto está em `{efetiva}`: uma trilha só")
    return efetiva


def _plano(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]]) -> None:
    print(f"# ordem de carga: {' → '.join(t.nome for t in ordem)}")
    for t in ordem:
        colunas = ", ".join(
            f"{c.nome} ({c.tipo}{', primária' if c.primaria else ''}{', chave' if c.chave else ''})" for c in t.colunas)
        print(f"# {t.nome}: {len(linhas.get(t.nome, []))} linha(s) · {colunas}")


def _nome_arquivo(nome: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", nome).strip(" .") or "tabela"


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
        return [Achado(_rotulo(saida), "-", "ERRO", "C015", f"não montou as saídas: {erro}")]
    achados = []
    for destino, dados in prontos:
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            gravar_atomico(destino, dados)
            print(f"# gravado: {_rotulo(destino)}")
        except OSError as erro:
            dica = " (o arquivo está aberto no Excel?)" if isinstance(erro, PermissionError) else ""
            achados.append(Achado(_rotulo(destino), "-", "ERRO", "C015", f"não gravou: {erro.strerror or erro}{dica}"))
    return achados


def _fechar(achados: list[Achado]) -> int:
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(f"{erros} erro(s), {len(achados) - erros} aviso(s)")
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    if args.linhas is not None and not 1 <= args.linhas <= MAX_LINHAS:
        return _uso(f"--linhas precisa ser de 1 a {MAX_LINHAS}")
    if args.saida is not None and args.saida.exists() and not args.saida.is_dir():
        return _uso(f"--saida precisa ser uma pasta: {args.saida}")
    if not 1 <= args.idioma <= 99999:
        return _uso("--idioma é o código do idioma base do ambiente, como 1046 (pt-BR) ou 1033 (inglês)")
    if args.flow and args.conferir:
        return _uso("--flow e --conferir são etapas diferentes: gere o plano, rode o flow e só depois confira")
    try:
        dados = _ler_json(args.spec, "spec")
        do_config = _trilha_do_config(args.config) if args.config or not args.trilha else None
        export = _ler_json(args.conferir, "export") if args.conferir else None
    except ValueError as erro:
        return _uso(str(erro))
    r = Relato(_rotulo(args.spec))
    spec = ler_spec(dados, r)
    trilha = decidir_trilha(args.trilha, do_config, spec, r)
    print(f"# trilha: {trilha or '?'}")
    if spec is None or trilha is None:
        return _fechar(r.achados)
    if args.conferir and trilha != "dataverse":
        return _uso("--conferir só vale na trilha dataverse: no SQL o tipo é o do DDL")
    if args.flow and trilha != "dataverse":
        return _uso("--flow só vale na trilha dataverse: no SQL a estrutura vem do DDL e a carga do .sql")
    conferir_estrutura(spec, trilha, r)
    ordem, ciclo = ordem_de_carga(spec)
    if ciclo:
        r.erro("spec", "C007", f"dependência circular de Lookup entre {', '.join(ciclo)}: carregue uma delas sem "
                               "o Lookup e preencha depois, ou quebre o ciclo no modelo")
    if r.tem_erro:
        return _fechar(r.achados)
    if export is not None:
        entidades = entidades_do_export(export)
        if entidades is None:
            return _uso("export sem entidades: use a resposta de EntityDefinitions com $expand=Attributes")
        print(f"# conferência: {_rotulo(args.conferir)} × {r.arquivo}")
        ambiente = Relato(_rotulo(args.conferir))
        conferir_ambiente(ordem, entidades, ambiente)
        return _fechar(r.achados + ambiente.achados)
    linhas = montar_valores(ordem, spec, args.linhas, trilha, r)
    _plano(ordem, linhas)
    plano = montar_plano(ordem, linhas, args.spec.name, r) if args.flow and not r.tem_erro else None
    if plano is not None:
        print(f"# construtor: {resumo_texto(plano)}")
    if not r.tem_erro:
        avisar(ordem, linhas, trilha, r, args.flow)
    if args.saida is not None and not r.tem_erro:
        r.achados.extend(gravar_saidas(args.saida, ordem, linhas, trilha, args.uma_por_tabela, args.spec.name,
                                       plano, args.idioma))
    return _fechar(r.achados)


if __name__ == "__main__":
    sys.exit(main())
