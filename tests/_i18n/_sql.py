"""O SQL en-US tem o mesmo código do pt-BR: só muda comentário e texto humano.

`codigo(texto)` devolve os tokens do SQL sem comentário (`--` e `/* */`, aninhado). Literal de string
com cara de nome (`'GRAVADO'`, `'dbo.usp_X'`, `'%'`) fica igual; literal com espaço, acento ou
pontuação de frase é texto e vira `''`. `blocos_sql(md)` lê os blocos ```sql / ```tsql de um .md.
"""
from __future__ import annotations

import re

NOME = re.compile(r"[A-Za-z0-9_.$/{}\[\]@%#:<>*-]*")
FENCE = re.compile(r"^```+\s*t?sql\b[^\n]*\n(.*?)^```+\s*$", re.I | re.M | re.S)
TOKEN = re.compile(r"'[^']*'|\[[^\]]*\]|[A-Za-z0-9_@#$.]+|\S")


def _sem_comentario_e_texto(sql: str) -> str:
    saida, i, n = [], 0, len(sql)
    while i < n:
        if sql.startswith("--", i):
            fim = sql.find("\n", i)
            i = n if fim < 0 else fim
        elif sql.startswith("/*", i):
            nivel, i = 1, i + 2
            while i < n and nivel:
                if sql.startswith("/*", i):
                    nivel, i = nivel + 1, i + 2
                elif sql.startswith("*/", i):
                    nivel, i = nivel - 1, i + 2
                else:
                    i += 1
            saida.append(" ")
        elif sql[i] == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'" and sql.startswith("''", j):
                    j += 2
                elif sql[j] == "'":
                    break
                else:
                    j += 1
            valor = sql[i + 1:j]
            saida.append(f"'{valor}'" if NOME.fullmatch(valor) else "''")
            i = j + 1
        else:
            saida.append(sql[i])
            i += 1
    return "".join(saida)


def codigo(sql: str) -> list[str]:
    return TOKEN.findall(_sem_comentario_e_texto(sql))


def blocos_sql(texto_md: str) -> list[str]:
    return FENCE.findall(texto_md.replace("\r\n", "\n"))
