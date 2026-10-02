"""Script T-SQL da carga mockup (trilha SQL Server), para o `montar-carga-mockup.py`.

Os identificadores chegam validados (`schema.Tabela`, nome de coluna ASCII); aqui só se põe colchete.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from _carga_modelo import Coluna, Tabela, na_carga

ARQ_SQL = "carga-mockup.sql"


def _q(nome: str) -> str:
    return ".".join(f"[{p}]" for p in nome.split("."))


def _literal(valor: Any) -> str:
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, Decimal):
        return format(valor, "f")
    if isinstance(valor, datetime):
        return f"'{valor:%Y-%m-%dT%H:%M:%S}'"
    if isinstance(valor, date):
        return f"'{valor:%Y%m%d}'"  # AAAAMMDD não depende do SET DATEFORMAT nem do idioma da sessão
    return "N'" + str(valor).replace("'", "''") + "'"


def _valor_sql(c: Coluna, valor: Any, por_nome: dict[str, Tabela]) -> str:
    if c.tipo != "lookup" or valor is None:
        return _literal(valor)
    alvo = por_nome[(c.alvo or "").casefold()]
    ref = alvo.referencia("sql-server")
    if not alvo.pk or ref is None:
        return _literal(valor)
    return f"(SELECT {_q(alvo.pk)} FROM {_q(alvo.sql or '')} WHERE {_q(ref.sql or '')} = {_literal(valor)})"


def _guarda(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]]) -> list[str]:
    for t in ordem:
        ref = t.referencia("sql-server")
        if ref and ref.sql and linhas[t.nome] and linhas[t.nome][0].get(ref.nome) is not None:
            mensagem = f"A carga mockup já foi aplicada neste banco (a linha mockup de {t.nome} existe). Nada foi gravado."
            return [
                f"IF EXISTS (SELECT 1 FROM {_q(t.sql or '')} WHERE {_q(ref.sql)} = {_literal(linhas[t.nome][0][ref.nome])})",
                f"    THROW 50001, {_literal(mensagem)}, 1;",
            ]
    return ["-- sem guarda de reexecução: nenhuma tabela tem chave ou primária na carga"]


def script_sql(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], origem: str) -> str:
    por_nome = {t.nome.casefold(): t for t in ordem}
    partes = [
        f"-- {ARQ_SQL}: gerado por montar-carga-mockup.py a partir de {origem}. Não edite: ajuste o spec e gere de novo.",
        "-- Dados FICTÍCIOS para o banco de DEV. Nunca rode em HML ou PRD.",
        f"-- Ordem de carga (chaves estrangeiras): {' → '.join(t.nome for t in ordem)}.",
        "-- Rode uma vez. Para recarregar, apague antes as linhas mockup: a guarda abaixo para se achar a primeira.",
        "SET NOCOUNT ON;",
        "SET XACT_ABORT ON;",
        "",
        *_guarda(ordem, linhas),
        "",
        "BEGIN TRANSACTION;",
    ]
    for t in ordem:
        colunas = [c for c in t.colunas if na_carga(c, "sql-server")]
        nomes = ", ".join(_q(c.sql or "") for c in colunas)
        partes += ["", f"-- {t.nome}: {len(linhas[t.nome])} linha(s)"]
        for linha in linhas[t.nome]:
            valores = ", ".join(_valor_sql(c, linha[c.nome], por_nome) for c in colunas)
            partes.append(f"INSERT INTO {_q(t.sql or '')} ({nomes}) SELECT {valores};")
    partes += ["", "COMMIT TRANSACTION;"]
    return "\n".join(partes) + "\n"
