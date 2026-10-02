"""`--conferir` do `montar-carga-mockup.py`: o tipo que o Dataverse criou × o tipo do spec.

Entrada: o export da Web API (`EntityDefinitions` + `$expand=Attributes`), o mesmo do
`extrair-nomes-as-built.py` da skill `dataverse`. O que o export não traz (comportamento da data,
opções da Choice, destino da Pesquisa, formato do texto) vira AVISO C104 para conferir no maker.
"""
from __future__ import annotations

from typing import Any

from _carga_modelo import TIPOS, Coluna, Relato, Tabela, Tipo

ROTULO_ATRIBUTO = {
    "String": "Texto de linha única (String)", "Memo": "Várias linhas de texto (Memo)",
    "Integer": "Número inteiro (Integer)", "BigInt": "Número inteiro grande (BigInt)",
    "Decimal": "Número decimal (Decimal)", "Double": "Ponto flutuante (Double)", "Money": "Moeda (Money)",
    "Boolean": "Sim/Não (Boolean)", "DateTime": "Data e hora (DateTime)", "Picklist": "Escolha (Picklist)",
    "Lookup": "Pesquisa (Lookup)",
}
O_QUE_CONFERIR = {
    "data": "confira no maker o comportamento Somente data: o export não traz, e Data e hora com fuso muda o dia",
    "data_hora": "confira o comportamento (Local do usuário ou Independente de fuso horário): o export não traz",
    "email": "confira o formato Email da coluna de texto: o export não traz",
    "url": "confira o formato URL da coluna de texto: o export não traz",
    "telefone": "confira o formato Telefone da coluna de texto: o export não traz",
    "autonumero": "confira se o formato é Numeração automática: o export não traz",
}
Indice = tuple[dict[str, dict], dict[str, list[dict]]]


def _rotulo_label(label: Any) -> str:
    if not isinstance(label, dict):
        return ""
    local = label.get("UserLocalizedLabel") or {}
    if isinstance(local, dict) and local.get("Label"):
        return str(local["Label"])
    for item in label.get("LocalizedLabels") or []:
        if isinstance(item, dict) and item.get("Label"):
            return str(item["Label"])
    return ""


def entidades_do_export(dados: Any) -> list[dict] | None:
    """Aceita `{"value": [...]}`, uma lista de entidades ou uma entidade só."""
    if isinstance(dados, dict) and isinstance(dados.get("value"), list):
        itens = dados["value"]
    elif isinstance(dados, dict) and "LogicalName" in dados:
        itens = [dados]
    elif isinstance(dados, list):
        itens = dados
    else:
        return None
    entidades = [i for i in itens if isinstance(i, dict) and i.get("LogicalName")]
    return entidades if entidades and len(entidades) == len(itens) else None


def _indice(itens: list[dict]) -> Indice:
    por_logico: dict[str, dict] = {}
    por_exibicao: dict[str, list[dict]] = {}
    for item in itens:
        por_logico.setdefault(str(item.get("LogicalName", "")).casefold(), item)
        por_exibicao.setdefault(_rotulo_label(item.get("DisplayName")).casefold(), []).append(item)
    return por_logico, por_exibicao


def _achar(logico: str | None, nome: str, indice: Indice, tipo: Tipo | None = None) -> dict | None:
    """Pelo nome lógico, se o spec o deu; senão pelo de exibição. Com o mesmo nome de exibição, prefere o
    atributo que não é auxiliar de outro (`AttributeOf`, como o `<lookup>name`) e depois o do tipo esperado."""
    por_logico, por_exibicao = indice
    if logico:
        return por_logico.get(logico.casefold())
    candidatos = por_exibicao.get(nome.casefold(), [])
    proprios = [a for a in candidatos if not a.get("AttributeOf")] or candidatos
    do_tipo = [a for a in proprios if tipo and str(a.get("AttributeType") or "") in tipo.atributos]
    return (do_tipo or proprios or [None])[0]


def _conferir_coluna(c: Coluna, atributo: dict, entidade: dict, lugar: str, r: Relato) -> None:
    tipo = TIPOS[c.tipo]
    if c.tipo == "calculada":
        r.aviso(lugar, "C104", "coluna calculada: confira a fórmula no maker (o export não prova)")
        return
    bruto = str(atributo.get("AttributeType") or "")
    nome_do_tipo = atributo.get("AttributeTypeName")
    nome_tipo = str(nome_do_tipo.get("Value") or "") if isinstance(nome_do_tipo, dict) else ""
    if bruto not in tipo.atributos or tipo.nome_tipo not in nome_tipo:
        veio = ROTULO_ATRIBUTO.get(bruto) or f"`{bruto or '?'}` ({nome_tipo})"
        dica = ("Texto não vira Escolha nem Pesquisa: crie a coluna com o tipo certo, apague a que veio errada e "
                "exporte de novo." if c.tipo in {"choice", "lookup"} else
                "Recrie a coluna com o tipo do modelo enquanto só há linha mockup; com dado real, é migração.")
        r.erro(lugar, "C103", f"veio {veio}, o modelo pede {tipo.rotulo}. {dica}")
    elif c.tipo == "choice":
        r.aviso(lugar, "C104", f"confira as opções no maker: {', '.join(c.opcoes)} (o export não traz o OptionSet)")
    elif c.tipo == "lookup":
        r.aviso(lugar, "C104", f"confira se a Pesquisa aponta para `{c.alvo}` (o export não traz o destino)")
    elif c.tipo in O_QUE_CONFERIR:
        r.aviso(lugar, "C104", O_QUE_CONFERIR[c.tipo])
    principal = str(entidade.get("PrimaryNameAttribute") or "")
    if c.primaria and str(atributo.get("LogicalName")) != principal:
        r.erro(lugar, "C105", f"o nome principal da tabela é `{principal}`, não esta coluna. Ele não muda depois de "
                              f"criado: recrie a tabela escolhendo `{c.nome}` como coluna principal")


def conferir_ambiente(ordem: list[Tabela], entidades: list[dict], r: Relato) -> None:
    indice = _indice(entidades)
    for t in ordem:
        entidade = _achar(t.logico, t.nome, indice)
        if entidade is None:
            r.erro(t.nome, "C101", "a tabela não está no export: confira o nome de exibição ou informe `logico` no spec")
            continue
        atributos = _indice([a for a in entidade.get("Attributes") or [] if isinstance(a, dict)])
        for c in t.colunas:
            lugar = f"{t.nome}.{c.nome}"
            atributo = _achar(c.logico, c.nome, atributos, TIPOS[c.tipo])
            if atributo is None:
                r.erro(lugar, "C102", "a coluna não está na tabela do ambiente: crie-a, corrija o nome de exibição "
                                      "ou informe `logico` no spec")
                continue
            _conferir_coluna(c, atributo, entidade, lugar, r)
