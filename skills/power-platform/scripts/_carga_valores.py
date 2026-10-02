"""Valores da carga mockup: ordem de carga não, só os dados fictícios de cada linha.

Para cada coluna da carga, gera o valor que ajuda a dedução de tipo do Dataverse a acertar (código com
letra, decimal com fração, data de verdade) ou converte os `exemplos` do spec, acusando o que não serve
(C008). Usado pelo `montar-carga-mockup.py` para a planilha, o script SQL e o plano do construtor.
"""
from __future__ import annotations

import calendar
import json
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from _carga_modelo import TEXTUAIS, Coluna, Relato, Spec, Tabela, na_carga
from _carga_xlsx import sem_acento

LINHAS_PADRAO = 10
EMAIL = re.compile(r"[\w.+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})")
URL = re.compile(r"https?://([^/\s:?#]+)\S*")
DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
DATA_HORA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?")
MAX_CELULA = 32767    # caracteres numa célula
MAX_DIGITOS = 28      # contexto padrão do Decimal
DIA_MINIMO = 13       # dia e mês trocados na importação viram mês inválido (erro visível), não data errada
TEXTO_LONGO = ("texto de exemplo com mais de cem caracteres, para a importação reconhecer a coluna "
               "como texto de várias linhas e não cortar o conteúdo.")


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", sem_acento(texto).lower()).strip("-") or "item"


def _letras(numero: int, largura: int) -> str:
    n, saida = numero - 1, ""
    for _ in range(largura):
        saida = chr(65 + n % 26) + saida
        n //= 26
    return saida


def _codigo(nome: str, i: int, tamanho: int | None) -> str:
    sigla = re.sub(r"[^A-Z]", "", sem_acento(nome).upper())[:3] or "COD"
    codigo = f"{sigla}{i:03d}"
    return _letras(i, tamanho) if tamanho and len(codigo) > tamanho else codigo


def _quantum(casas: int) -> Decimal:
    return Decimal(1).scaleb(-casas)


def _data_sem_troca(base: date, k: int) -> date:
    """A k-ésima data (0, 1, 2...) a partir de `base`, pulando os dias 1 a 12 de cada mês."""
    d = base if base.day >= DIA_MINIMO else base.replace(day=DIA_MINIMO)
    while True:
        restantes = calendar.monthrange(d.year, d.month)[1] - d.day
        if k <= restantes:
            return d + timedelta(days=k)
        k -= restantes + 1
        d = (d.replace(day=28) + timedelta(days=4)).replace(day=DIA_MINIMO)


def _gerar(t: Tabela, c: Coluna, i: int, data_base: date, chaves_alvo: list[Any]) -> Any:
    """Valor fictício pensado para a dedução de tipo acertar: código com letra, decimal com fração..."""
    corte = (lambda s: s[:c.tamanho]) if c.tamanho else (lambda s: s)
    geradores = {
        "lookup": lambda: chaves_alvo[(i - 1) % len(chaves_alvo)] if chaves_alvo else None,
        "choice": lambda: c.opcoes[(i - 1) % len(c.opcoes)],
        "sim_nao": lambda: i % 2 == 1,
        "inteiro": lambda: i * 3,
        "decimal": lambda: (Decimal(i * 12) + Decimal("0.75")).quantize(_quantum(c.casas)),
        "moeda": lambda: (Decimal(i * 150) + Decimal("0.90")).quantize(_quantum(c.casas)),
        "data": lambda: _data_sem_troca(data_base, 3 * (i - 1)),
        "data_hora": lambda: datetime.combine(_data_sem_troca(data_base, i - 1), time(8 + (i - 1) % 10, 30)),
        "email": lambda: f"usuario{i:02d}@contoso.com",
        "telefone": lambda: corte(f"(11) 90000-{i:04d}"),
        "url": lambda: f"https://contoso.com/{_slug(t.nome)}/{i}",
        "codigo": lambda: _codigo(c.nome, i, c.tamanho),
        "autonumero": lambda: _codigo(c.nome, i, None),
        "texto_longo": lambda: corte(f"{c.nome} {i:02d}: {TEXTO_LONGO}"),
    }
    gerador = geradores.get(c.tipo)
    return gerador() if gerador else corte(f"{t.nome if c.primaria else c.nome} {i:02d}")


def _converter_texto(c: Coluna, bruto: Any) -> tuple[Any, str | None]:
    if not isinstance(bruto, str):
        perde = " (número perde o zero à esquerda)" if c.tipo in {"codigo", "telefone"} else ""
        return None, "use texto entre aspas" + perde
    if c.tamanho and len(bruto) > c.tamanho:
        return None, f"passa do `tamanho` {c.tamanho}"
    if len(bruto) > MAX_CELULA:
        return None, f"passa de {MAX_CELULA} caracteres, o limite de uma célula do Excel"
    if c.tipo == "email" and not EMAIL.fullmatch(bruto):
        return None, "e-mail inválido"
    if c.tipo == "url" and not URL.fullmatch(bruto):
        return None, "URL precisa começar com http:// ou https://"
    return bruto, None


def _converter_numero(c: Coluna, bruto: Any) -> tuple[Any, str | None]:
    if isinstance(bruto, bool) or not isinstance(bruto, (int, float)):
        return None, "precisa ser número, sem aspas e com ponto decimal"
    if c.tipo == "inteiro":
        return (bruto, None) if isinstance(bruto, int) else (None, "precisa ser número inteiro")
    valor = Decimal(str(bruto))
    if not valor.is_finite():
        return None, "precisa ser número finito"
    if -valor.as_tuple().exponent > c.casas:
        return None, f"tem mais de {c.casas} casa(s) decimal(is)"
    try:
        quantizado = valor.quantize(_quantum(c.casas))
    except InvalidOperation:
        quantizado = None
    if quantizado is None or len(quantizado.as_tuple().digits) > MAX_DIGITOS:
        return None, f"número grande demais (mais de {MAX_DIGITOS} dígitos)"
    return quantizado, None


def _converter_data(c: Coluna, bruto: Any) -> tuple[Any, str | None]:
    formato, padrao = ("AAAA-MM-DD", DATA) if c.tipo == "data" else ("AAAA-MM-DDTHH:MM", DATA_HORA)
    if not isinstance(bruto, str) or not padrao.fullmatch(bruto):
        return None, f"use {formato}"
    try:
        return (date.fromisoformat(bruto) if c.tipo == "data" else datetime.fromisoformat(bruto)), None
    except ValueError:
        return None, "data inexistente"


def converter(c: Coluna, bruto: Any, chaves_alvo: list[Any]) -> tuple[Any, str | None]:
    """Exemplo do spec → valor tipado, ou o motivo de recusa."""
    if bruto is None:
        return None, ("a coluna exige valor" if c.exige_valor else None)
    if c.tipo in TEXTUAIS:
        return _converter_texto(c, bruto)
    if c.tipo in {"inteiro", "decimal", "moeda"}:
        return _converter_numero(c, bruto)
    if c.tipo in {"data", "data_hora"}:
        return _converter_data(c, bruto)
    if c.tipo == "sim_nao":
        return (bruto, None) if isinstance(bruto, bool) else (None, "use true ou false")
    if c.tipo == "choice":
        return (bruto, None) if bruto in c.opcoes else (None, f"não é opção; use {', '.join(c.opcoes)}")
    achado = next((v for v in chaves_alvo if v is not None and str(v) == str(bruto)), None)
    return (achado, None) if achado is not None else (None, f"não existe em `{c.alvo}`")


def _valores_da_coluna(t: Tabela, c: Coluna, n: int, data_base: date, chaves_alvo: list[Any],
                       r: Relato) -> list[Any]:
    lugar = f"{t.nome}.{c.nome}"
    if c.exemplos is None:
        gerados = [_gerar(t, c, i, data_base, chaves_alvo) for i in range(1, n + 1)]
        longo = next((v for v in gerados if isinstance(v, str) and c.tamanho and len(v) > c.tamanho), None)
        if longo is not None:
            r.erro(lugar, "C008", f"o valor gerado `{longo}` passa do `tamanho` {c.tamanho}: dê `exemplos` que caibam")
        return gerados
    valores = []
    for k, bruto in enumerate(c.exemplos, start=1):
        valor, problema = converter(c, bruto, chaves_alvo)
        if problema:
            r.erro(lugar, "C008", f"exemplo {k} ({json.dumps(bruto, ensure_ascii=False)}): {problema}")
        valores.append(valor)
    if (c.primaria or c.chave) and len(valores) < n:
        r.erro(lugar, "C008", f"{len(valores)} exemplo(s) para {n} linhas numa coluna de valor único: "
                              "dê mais exemplos ou ajuste `linhas` da tabela")
    return [valores[i % len(valores)] for i in range(n)]


def _autorreferencia(t: Tabela, c: Coluna, colunas: dict[str, list[Any]], n: int, ref: Coluna | None,
                     data_base: date, r: Relato) -> list[Any]:
    """Lookup para a própria tabela: a 1ª linha fica vazia, as outras apontam para ela."""
    proprias = colunas.get(ref.nome, []) if ref else []
    if c.exemplos is not None:
        return _valores_da_coluna(t, c, n, data_base, proprias, r)
    if c.obrigatoria:
        r.erro(f"{t.nome}.{c.nome}", "C008", "Lookup obrigatório para a própria tabela: a 1ª linha não tem a quem "
                                             "apontar na carga; deixe opcional ou dê `exemplos`")
    return [None] + [proprias[0] if proprias else None] * (n - 1)


def _checar_unicos(t: Tabela, colunas: dict[str, list[Any]], r: Relato) -> None:
    for c in t.colunas:
        if not (c.primaria or c.chave) or c.nome not in colunas:
            continue
        vistos: set[str] = set()
        for valor in colunas[c.nome]:
            normal = str(valor).casefold().rstrip()  # o banco e a chave alternativa comparam assim
            if valor is not None and normal in vistos:
                r.erro(f"{t.nome}.{c.nome}", "C008", f"valor repetido `{valor}`: Lookup e chave alternativa "
                                                     "precisam de valor único (sem diferenciar maiúscula)")
                break
            vistos.add(normal)


def linhas_da_tabela(t: Tabela, n: int, data_base: date, trilha: str, chaves: dict[str, list[Any]],
                     por_nome: dict[str, Tabela], r: Relato) -> list[dict[str, Any]]:
    colunas_da_carga = [c for c in t.colunas if na_carga(c, trilha)]
    colunas: dict[str, list[Any]] = {}
    proprios = [c for c in colunas_da_carga if c.tipo == "lookup" and por_nome.get((c.alvo or "").casefold()) is t]
    for c in colunas_da_carga:
        if c in proprios:
            continue
        alvo = por_nome.get((c.alvo or "").casefold())
        colunas[c.nome] = _valores_da_coluna(t, c, n, data_base, chaves.get(alvo.nome, []) if alvo else [], r)
    for c in proprios:
        colunas[c.nome] = _autorreferencia(t, c, colunas, n, t.referencia(trilha), data_base, r)
    _checar_unicos(t, colunas, r)
    return [{c.nome: colunas[c.nome][i] for c in colunas_da_carga} for i in range(n)]


def montar_valores(ordem: list[Tabela], spec: Spec, linhas_cli: int | None, trilha: str,
                   r: Relato) -> dict[str, list[dict[str, Any]]]:
    por_nome = {t.nome.casefold(): t for t in ordem}
    linhas: dict[str, list[dict[str, Any]]] = {}
    chaves: dict[str, list[Any]] = {}
    for t in ordem:
        n = t.linhas or linhas_cli or spec.linhas or LINHAS_PADRAO
        linhas[t.nome] = linhas_da_tabela(t, n, spec.data_base, trilha, chaves, por_nome, r)
        ref = t.referencia(trilha)
        chaves[t.nome] = [linha.get(ref.nome) for linha in linhas[t.nome]] if ref else []
    return linhas
