"""O JSON de fluxo en-US tem o mesmo código do pt-BR: só muda texto humano.

Chaves, ordem, tipos e valores que não são texto ficam iguais. Livre: o valor de description, title e
summary. Numa expressão (`@...`), literal com espaço, acento ou pontuação é texto; literal com cara de nome
(ação, variável, chave) fica igual. Numa string com `@{...}`, só os trechos `@{...}` contam. String simples
é livre se no pt-BR é frase (espaço ou acento); senão é código. `palavras` lista os literais de uma palavra
que são texto visível ({(pt, en)}): a exceção conferida à mão.
"""
from __future__ import annotations

import re

LIVRES = {"description", "title", "summary"}
LITERAL = re.compile(r"'(?:[^']|'')*'")
TRECHO = re.compile(r"@\{[^}]*\}")
NOME = re.compile(r"[A-Za-z0-9_.$/{}\[\]-]*")


def _esqueleto(texto: str, palavras: dict[str, str]) -> str:
    def literal(m: re.Match) -> str:
        valor = m.group(0)[1:-1]
        if valor in palavras or valor in palavras.values() or not NOME.fullmatch(valor):
            return "''"
        return m.group(0)

    def sem_texto(t: str) -> str:
        return LITERAL.sub(literal, t)

    return sem_texto(texto) if texto.startswith("@") else "".join(sem_texto(t) for t in TRECHO.findall(texto))


def diferencas(pt, en, palavras: dict[str, str] | None = None, caminho: str = "$") -> list[str]:
    palavras = palavras or {}
    if type(pt) is not type(en):
        return [f"{caminho}: tipo"]
    if isinstance(pt, dict):
        if list(pt) != list(en):
            return [f"{caminho}: chaves"]
        return [d for k in pt for d in diferencas(pt[k], en[k], palavras, f"{caminho}.{k}")]
    if isinstance(pt, list):
        if len(pt) != len(en):
            return [f"{caminho}: tamanho"]
        return [d for i, (a, b) in enumerate(zip(pt, en)) for d in diferencas(a, b, palavras, f"{caminho}[{i}]")]
    if pt == en or (isinstance(pt, str) and caminho.rsplit(".", 1)[-1] in LIVRES):
        return []
    if isinstance(pt, str):
        if "@" in pt and (pt.startswith("@") or "@{" in pt):
            return [] if _esqueleto(pt, palavras) == _esqueleto(en, palavras) else [f"{caminho}: {pt!r} -> {en!r}"]
        if not NOME.fullmatch(pt) or palavras.get(pt) == en:
            return []
    return [f"{caminho}: {pt!r} -> {en!r}"]
