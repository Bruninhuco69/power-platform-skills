"""Plano do construtor Dataverse (`montar-carga-mockup.py --flow`): o spec vira, na ordem, os pedidos à
Web API que criam as tabelas, as colunas com o tipo do spec, os relacionamentos e as linhas mockup.

O plano não conhece o ambiente. `{{prefixo}}` (prefixo do publisher da solução), `{{opcao}}` (prefixo de
valor de opção) e `{{idioma}}` (idioma base) ficam no texto, e o flow construtor os troca pelos da
solução escolhida antes de ler o JSON. O ID de cada linha é fixo (uuid5 da tabela e da linha): o filho
já nasce apontando para o pai, e rodar de novo pula o que já existe.

Achados: C016 nome lógico, C017 limite do Dataverse.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from _carga_modelo import Coluna, Relato, Tabela
from _carga_xlsx import sem_acento

ARQ_PLANO = "plano-dataverse.json"
FORMATO = "plano-dataverse/1"
API = "/api/data/v9.2"
PREFIXO, OPCAO, IDIOMA = "{{prefixo}}", "{{opcao}}", "{{idioma}}"
CRM = "Microsoft.Dynamics.CRM."
JSON_UTF8 = "application/json; charset=utf-8"
CRLF = chr(13) + chr(10)
SENTINELA = chr(1)  # marca no JSON montado; vira {{idioma}} ou {{opcao}}NNNN depois do json.dumps
MAX_PARTE = 40
MAX_TEXTO = 4000
MAX_CASAS_MOEDA = 4
DATA_MINIMA = date(1753, 1, 1)  # o Dataverse não guarda data anterior
MAX_LINHAS_LOTE = 100
MAX_CORPO_LOTE = 60_000  # caracteres: cada passo cabe com folga no limite de 131.072 das expressões do flow
MAX_LINHA = 100_000
LIMITES = {
    "inteiro": (Decimal(-2147483648), Decimal(2147483647)),
    "decimal": (Decimal(-100_000_000_000), Decimal(100_000_000_000)),
    "moeda": (Decimal(-922_337_203_685_477), Decimal(922_337_203_685_477)),
}
TAMANHO_PADRAO = {"texto": 100, "codigo": 100, "email": 100, "telefone": 50, "url": 200, "autonumero": 100,
                  "texto_longo": 2000}
FORMATO_TEXTO = {"texto": "Text", "codigo": "Text", "autonumero": "Text", "email": "Email", "telefone": "Phone",
                 "url": "Url"}
SEM_COLUNA = {"lookup", "calculada"}  # o Lookup nasce no relacionamento; a calculada se cria à mão
SEM_DADO = {"autonumero", "imagem", "arquivo", "calculada"}  # o Dataverse gera, ou não cabe numa linha JSON
PARTE_OK = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
PALAVRA = re.compile(r"[A-Za-z0-9]+")
MARCA_OPCAO = re.compile(re.escape(json.dumps(SENTINELA + "OPCAO")[:-1]) + "([0-9]{4})" + '"')
MARCA_IDIOMA = json.dumps(SENTINELA + "IDIOMA")
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "power-platform-skills/carga-mockup")
DESCRICAO = "Criada pelo construtor Dataverse do kit a partir do spec da carga mockup."
ORDEM_FASES = ("tabela", "coluna", "relacionamento", "publicar", "dados", "chave")


def esquema(parte: str) -> str:
    return f"{PREFIXO}_{parte}"


def logico(parte: str) -> str:
    return esquema(parte).lower()


def conjunto(parte: str) -> str:
    """EntitySetName explícito, com a regra de plural da plataforma, para o plano não depender do default."""
    nome = logico(parte)
    if re.search(r"[^aeiou]y$", nome):
        return nome[:-1] + "ies"
    if re.search(r"(s|x|z|ch|sh)$", nome):
        return nome + "es"
    return nome + "s"


def _plural_pt(palavra: str) -> str:
    final = palavra.lower()
    if final.endswith("ão"):
        return palavra[:-2] + "ões"
    if final.endswith("m"):
        return palavra[:-1] + "ns"
    if final.endswith("l") and not final.endswith("il"):
        return palavra[:-1] + "is"
    if final.endswith(("r", "z")):
        return palavra + "es"
    if final[-1:] in "aeiouáéíóúâêôã":
        return palavra + "s"
    return palavra


def plural_exibicao(nome: str) -> str:
    """Nome no plural para a lista: a 1ª palavra em "Tipo de serviço", a última nos demais."""
    palavras = nome.split(" ")
    alvo = 0 if any(p.lower() in {"de", "da", "do", "das", "dos"} for p in palavras[1:]) else len(palavras) - 1
    return " ".join(_plural_pt(p) if k == alvo else p for k, p in enumerate(palavras))


# ---------- nomes ----------

@dataclass(frozen=True)
class Nomes:
    tabelas: dict[str, str]                # nome da tabela → parte do nome lógico depois do prefixo
    colunas: dict[tuple[str, str], str]    # (tabela, coluna) → parte

    def tabela(self, t: Tabela) -> str:
        return self.tabelas[t.nome]

    def coluna(self, t: Tabela, c: Coluna) -> str:
        return self.colunas[(t.nome, c.nome)]


def _parte(nome: str, dado: str | None) -> str | None:
    if dado:
        prefixo, separador, resto = dado.partition("_")
        parte = resto if separador and prefixo else ""
    else:
        parte = "".join(p[:1].upper() + p[1:] for p in PALAVRA.findall(sem_acento(nome)))
    return parte if PARTE_OK.fullmatch(parte) and len(parte) <= MAX_PARTE else None


def _sem_parte(lugar: str, nome: str, dado: str | None, r: Relato) -> None:
    if dado:
        r.erro(lugar, "C016", f"`logico` `{dado}` precisa ser `prefixo_nome`: letras, números e _, até {MAX_PARTE} "
                              "depois do prefixo (o prefixo vem da solução)")
    else:
        r.erro(lugar, "C016", f"não dá para derivar o nome lógico de `{nome}` (letra no início, até {MAX_PARTE} "
                              "caracteres sem acento): informe `logico` no spec, como `abc_pedido`")


def resolver_nomes(ordem: list[Tabela], r: Relato) -> Nomes:
    tabelas: dict[str, str] = {}
    colunas: dict[tuple[str, str], str] = {}
    vistas: dict[str, str] = {}
    for t in ordem:
        parte = _parte(t.nome, t.logico)
        if parte is None:
            _sem_parte(t.nome, t.nome, t.logico, r)
            continue
        if parte.lower() in vistas:
            r.erro(t.nome, "C016", f"vira `{logico(parte)}`, o mesmo nome lógico de `{vistas[parte.lower()]}`: "
                                   "informe `logico` numa delas")
            continue
        vistas[parte.lower()] = t.nome
        tabelas[t.nome] = parte
        usados = {logico(parte) + "id": "a chave primária da tabela"}
        for c in t.colunas:
            if c.tipo == "calculada":
                continue
            lugar, parte_c = f"{t.nome}.{c.nome}", _parte(c.nome, c.logico)
            if parte_c is None:
                _sem_parte(lugar, c.nome, c.logico, r)
            elif logico(parte_c) in usados:
                r.erro(lugar, "C016", f"vira `{logico(parte_c)}`, o mesmo nome lógico de {usados[logico(parte_c)]}: "
                                      "informe `logico`")
            else:
                usados[logico(parte_c)] = f"`{c.nome}`"
                colunas[(t.nome, c.nome)] = parte_c
    return Nomes(tabelas, colunas)


# ---------- limites ----------

def _marcado(texto: Any) -> bool:
    return isinstance(texto, str) and ("{{" in texto or SENTINELA in texto)


def _fora_do_limite(c: Coluna, valores: list[Any]) -> bool:
    if c.tipo not in LIMITES:
        return False
    minimo, maximo = LIMITES[c.tipo]
    return any(v is not None and not minimo <= Decimal(v) <= maximo for v in valores)


def _maior_que_a_coluna(c: Coluna, valores: list[Any]) -> int | None:
    """O tamanho que o construtor cria (o do spec ou o padrão), se algum valor não couber nele."""
    limite = c.tamanho or TAMANHO_PADRAO.get(c.tipo)
    if c.tipo == "autonumero" or limite is None:
        return None
    return limite if any(isinstance(v, str) and len(v) > limite for v in valores) else None


def _antes_do_minimo(valores: list[Any]) -> bool:
    return any(isinstance(v, date) and (v.date() if isinstance(v, datetime) else v) < DATA_MINIMA for v in valores)


def checar_limites(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], r: Relato) -> None:
    for t in ordem:
        if _marcado(t.nome):
            r.erro(t.nome, "C017", "nome com `{{`: o construtor usa `{{` como marcador")
        for c in t.colunas:
            lugar = f"{t.nome}.{c.nome}"
            valores = [linha.get(c.nome) for linha in linhas[t.nome]]
            if c.tipo == "moeda" and c.casas > MAX_CASAS_MOEDA:
                r.erro(lugar, "C017", f"Moeda no Dataverse tem até {MAX_CASAS_MOEDA} casas; use decimal")
            if c.tipo in FORMATO_TEXTO and c.tamanho and c.tamanho > MAX_TEXTO:
                r.erro(lugar, "C017", f"texto de linha única vai até {MAX_TEXTO} caracteres; use texto_longo")
            if any(map(_marcado, (c.nome, *c.opcoes, *valores))):
                r.erro(lugar, "C017", "nome, opção ou valor com `{{` ou caractere de controle: o construtor usa "
                                      "`{{` como marcador")
            if _fora_do_limite(c, valores):
                minimo, maximo = LIMITES[c.tipo]
                r.erro(lugar, "C017", f"valor fora do limite do Dataverse para `{c.tipo}` ({minimo} a {maximo})")
            limite = _maior_que_a_coluna(c, valores)
            if limite:
                r.erro(lugar, "C017", f"valor maior que os {limite} caracteres da coluna que o construtor cria: "
                                      "dê `tamanho` ou encurte os `exemplos`")
            if _antes_do_minimo(valores):
                r.erro(lugar, "C017", f"data anterior a {DATA_MINIMA:%d/%m/%Y}, a menor que o Dataverse guarda")


# ---------- corpo dos pedidos ----------

def _json(dados: Any) -> str:
    """JSON em ASCII (acento escapado), com as sentinelas trocadas pelos marcadores do ambiente."""
    texto = json.dumps(dados, ensure_ascii=True, separators=(",", ":")).replace(MARCA_IDIOMA, IDIOMA)
    return MARCA_OPCAO.sub(lambda m: OPCAO + m.group(1), texto)


def _rotulo(texto: str) -> dict[str, Any]:
    return {"@odata.type": CRM + "Label", "LocalizedLabels": [
        {"@odata.type": CRM + "LocalizedLabel", "Label": texto, "LanguageCode": SENTINELA + "IDIOMA"}]}


def _nivel(c: Coluna) -> dict[str, Any]:
    return {"Value": "ApplicationRequired" if c.exige_valor else "None", "CanBeChanged": True,
            "ManagedPropertyLogicalName": "canmodifyrequirementlevelsettings"}


def _tipo(atributo: str, classe: str, nome_tipo: str) -> dict[str, Any]:
    return {"@odata.type": CRM + classe, "AttributeType": atributo, "AttributeTypeName": {"Value": nome_tipo}}


def _opcoes(c: Coluna) -> dict[str, Any]:
    return {"@odata.type": CRM + "OptionSetMetadata", "IsGlobal": False, "OptionSetType": "Picklist",
            "Options": [{"Value": f"{SENTINELA}OPCAO{k:04d}", "Label": _rotulo(o)} for k, o in enumerate(c.opcoes)]}


def _sigla(nome: str) -> str:
    return re.sub(r"[^A-Z]", "", sem_acento(nome).upper())[:3] or "COD"


def _texto(c: Coluna) -> dict[str, Any]:
    corpo = {**_tipo("String", "StringAttributeMetadata", "StringType"),
             "MaxLength": c.tamanho or TAMANHO_PADRAO[c.tipo], "FormatName": {"Value": FORMATO_TEXTO[c.tipo]}}
    if c.tipo == "autonumero":
        corpo["AutoNumberFormat"] = _sigla(c.nome) + "-{SEQNUM:5}"
    return corpo


def _data(c: Coluna) -> dict[str, Any]:
    so_data = c.tipo == "data"
    return {**_tipo("DateTime", "DateTimeAttributeMetadata", "DateTimeType"),
            "Format": "DateOnly" if so_data else "DateAndTime",
            "DateTimeBehavior": {"Value": "DateOnly" if so_data else "UserLocal"}}


def _sim_nao(_: Coluna) -> dict[str, Any]:
    return {**_tipo("Boolean", "BooleanAttributeMetadata", "BooleanType"), "DefaultValue": False,
            "OptionSet": {"@odata.type": CRM + "BooleanOptionSetMetadata", "OptionSetType": "Boolean",
                          "TrueOption": {"Value": 1, "Label": _rotulo("Sim")},
                          "FalseOption": {"Value": 0, "Label": _rotulo("Não")}}}


TIPADO = {
    "texto_longo": lambda c: {**_tipo("Memo", "MemoAttributeMetadata", "MemoType"), "Format": "TextArea",
                              "ImeMode": "Disabled", "MaxLength": c.tamanho or TAMANHO_PADRAO["texto_longo"]},
    "inteiro": lambda c: {**_tipo("Integer", "IntegerAttributeMetadata", "IntegerType"), "Format": "None",
                          "MinValue": -2147483648, "MaxValue": 2147483647},
    "decimal": lambda c: {**_tipo("Decimal", "DecimalAttributeMetadata", "DecimalType"), "Precision": c.casas,
                          "MinValue": -100_000_000_000, "MaxValue": 100_000_000_000},
    "moeda": lambda c: {**_tipo("Money", "MoneyAttributeMetadata", "MoneyType"), "PrecisionSource": 0,
                        "Precision": c.casas, "MinValue": -922_337_203_685_477, "MaxValue": 922_337_203_685_477},
    "data": _data,
    "data_hora": _data,
    "sim_nao": _sim_nao,
    "choice": lambda c: {**_tipo("Picklist", "PicklistAttributeMetadata", "PicklistType"), "OptionSet": _opcoes(c)},
    "escolhas": lambda c: {**_tipo("Virtual", "MultiSelectPicklistAttributeMetadata", "MultiSelectPicklistType"),
                           "OptionSet": _opcoes(c)},
    # IsPrimaryImage fica de fora: `false` na criação levanta exceção, e a 1ª imagem já nasce primária
    "imagem": lambda c: {"@odata.type": CRM + "ImageAttributeMetadata", "AttributeTypeName": {"Value": "ImageType"},
                         "CanStoreFullImage": True, "MaxSizeInKB": 10240},
    "arquivo": lambda c: {"@odata.type": CRM + "FileAttributeMetadata", "AttributeTypeName": {"Value": "FileType"},
                          "MaxSizeInKB": 32768},
    **{tipo: _texto for tipo in FORMATO_TEXTO},
}


def atributo(c: Coluna, parte: str) -> dict[str, Any]:
    return {**TIPADO[c.tipo](c), "SchemaName": esquema(parte), "DisplayName": _rotulo(c.nome),
            "RequiredLevel": _nivel(c)}


def _filtro(campo: str, valor: str) -> str:
    return f"$filter={campo}%20eq%20'{valor}'"


def _passo(fase: str, rotulo: str, existe: str, url: str, corpo: str, tipo: str = JSON_UTF8) -> dict[str, Any]:
    return {"fase": fase, "rotulo": rotulo, "existe": existe, "metodo": "POST", "url": API + url, "tipo": tipo,
            "corpo": corpo}


def _em_tabela(parte: str) -> str:
    return f"/EntityDefinitions(LogicalName='{logico(parte)}')"


def passo_tabela(t: Tabela, nomes: Nomes) -> dict[str, Any]:
    parte, primaria = nomes.tabela(t), t.primaria()
    assert primaria is not None  # C005 garante uma primária na trilha Dataverse
    corpo = {"@odata.type": CRM + "EntityMetadata", "SchemaName": esquema(parte), "EntitySetName": conjunto(parte),
             "DisplayName": _rotulo(t.nome), "DisplayCollectionName": _rotulo(plural_exibicao(t.nome)),
             "Description": _rotulo(DESCRICAO), "OwnershipType": "UserOwned", "IsActivity": False,
             "HasActivities": False, "HasNotes": False,
             "Attributes": [{**atributo(primaria, nomes.coluna(t, primaria)), "IsPrimaryName": True}]}
    existe = f"{API}/EntityDefinitions?$select=LogicalName&" + _filtro("LogicalName", logico(parte))
    return _passo("tabela", t.nome, existe, "/EntityDefinitions", _json(corpo))


def passo_coluna(t: Tabela, c: Coluna, nomes: Nomes) -> dict[str, Any]:
    parte_t, parte = nomes.tabela(t), nomes.coluna(t, c)
    existe = f"{API}{_em_tabela(parte_t)}/Attributes?$select=LogicalName&" + _filtro("LogicalName", logico(parte))
    return _passo("coluna", f"{t.nome}.{c.nome}", existe, f"{_em_tabela(parte_t)}/Attributes",
                  _json(atributo(c, parte)))


def nome_relacionamento(t: Tabela, c: Coluna, nomes: Nomes) -> str:
    return f"{PREFIXO}_{nomes.tabela(t)}_{nomes.coluna(t, c)}"


def passo_relacionamento(t: Tabela, c: Coluna, alvo: Tabela, nomes: Nomes) -> dict[str, Any]:
    nome, parte_alvo = nome_relacionamento(t, c, nomes), nomes.tabela(alvo)
    lookup = {**_tipo("Lookup", "LookupAttributeMetadata", "LookupType"), "SchemaName": esquema(nomes.coluna(t, c)),
              "DisplayName": _rotulo(c.nome), "RequiredLevel": _nivel(c)}
    cascata = {chave: "NoCascade" for chave in ("Assign", "Merge", "Reparent", "Share", "Unshare", "RollupView")}
    menu = {"Behavior": "UseCollectionName", "Group": "Details", "Order": 10000,
            "Label": _rotulo(plural_exibicao(t.nome))}
    corpo = {"@odata.type": CRM + "OneToManyRelationshipMetadata", "SchemaName": nome,
             "ReferencedEntity": logico(parte_alvo), "ReferencedAttribute": logico(parte_alvo) + "id",
             "ReferencingEntity": logico(nomes.tabela(t)), "ReferencedEntityNavigationPropertyName": nome,
             "ReferencingEntityNavigationPropertyName": esquema(nomes.coluna(t, c)),
             "CascadeConfiguration": {**cascata, "Delete": "Restrict" if c.obrigatoria else "RemoveLink"},
             "AssociatedMenuConfiguration": menu, "Lookup": lookup}
    existe = f"{API}/RelationshipDefinitions?$select=SchemaName&" + _filtro("SchemaName", nome)
    return _passo("relacionamento", f"{t.nome}.{c.nome} → {alvo.nome}", existe, "/RelationshipDefinitions",
                  _json(corpo))


def passo_publicar(ordem: list[Tabela], nomes: Nomes) -> dict[str, Any]:
    entidades = "".join(f"<entity>{logico(nomes.tabela(t))}</entity>" for t in ordem)
    xml = f"<importexportxml><entities>{entidades}</entities></importexportxml>"
    return _passo("publicar", "Publicar as tabelas", "", "/PublishXml", _json({"ParameterXml": xml}))


def passo_chave(t: Tabela, c: Coluna, nomes: Nomes) -> dict[str, Any]:
    parte_t = nomes.tabela(t)
    nome = f"{PREFIXO}_{parte_t}_Chave"
    corpo = {"@odata.type": CRM + "EntityKeyMetadata", "SchemaName": nome, "DisplayName": _rotulo(f"Chave {c.nome}"),
             "KeyAttributes": [logico(nomes.coluna(t, c))]}
    existe = f"{API}{_em_tabela(parte_t)}/Keys?$select=LogicalName&" + _filtro("LogicalName", nome.lower())
    return _passo("chave", f"{t.nome}.{c.nome} (chave)", existe, f"{_em_tabela(parte_t)}/Keys", _json(corpo))


# ---------- dados ----------

def id_da_linha(t: Tabela, numero: int) -> str:
    return str(uuid.uuid5(NAMESPACE, f"linha/{t.nome.casefold()}/{numero}"))


def _primitivo(valor: Any) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, Decimal):
        return format(valor, "f")
    if isinstance(valor, int):
        return str(valor)
    if isinstance(valor, float):
        return json.dumps(valor)
    if isinstance(valor, datetime):
        return json.dumps(valor.isoformat(timespec="seconds") + "Z")
    if isinstance(valor, date):
        return json.dumps(valor.isoformat())
    return json.dumps(str(valor))


@dataclass(frozen=True)
class Contexto:
    nomes: Nomes
    por_nome: dict[str, Tabela]
    posicoes: dict[str, dict[str, int]]  # tabela → valor do nome principal → posição da linha (0 = 1ª)


def _posicoes(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, int]]:
    saida: dict[str, dict[str, int]] = {}
    for t in ordem:
        ref, posicao = t.referencia("dataverse"), {}
        for k, linha in enumerate(linhas[t.nome]):
            if ref and linha.get(ref.nome) is not None:
                posicao.setdefault(str(linha[ref.nome]), k)
        saida[t.nome] = posicao
    return saida


def _ligacao(t: Tabela, c: Coluna, valor: Any, k: int, inicio: int, ctx: Contexto, r: Relato) -> str | None:
    """Valor do `@odata.bind`: o ID fixo da linha do pai (ou de um lote já gravado), ou `$n` (Content-ID) para
    uma linha anterior do mesmo lote."""
    alvo = ctx.por_nome[(c.alvo or "").casefold()]
    destino = ctx.posicoes[alvo.nome].get(str(valor))
    if destino is None:
        return None
    if alvo is not t or destino < inicio:
        return f"/{conjunto(ctx.nomes.tabela(alvo))}({id_da_linha(alvo, destino + 1)})"
    if destino < k:
        return f"${destino - inicio + 1}"
    r.erro(f"{t.nome}.{c.nome}", "C017", f"a linha {k + 1} aponta para a linha {destino + 1} da mesma tabela: no "
                                         "lote só dá para apontar para linha anterior; reordene os `exemplos`")
    return None


def linha_json(t: Tabela, k: int, inicio: int, linha: dict[str, Any], ctx: Contexto, r: Relato) -> str:
    pares = [(logico(ctx.nomes.tabela(t)) + "id", json.dumps(id_da_linha(t, k + 1)))]
    for c in t.colunas:
        if c.tipo in SEM_DADO:
            continue
        nome = logico(ctx.nomes.coluna(t, c))
        valor = linha.get(c.nome)
        if c.tipo == "escolhas":
            pares.append((nome, json.dumps(f"{OPCAO}{k % len(c.opcoes):04d}")))
        elif valor is None:
            continue
        elif c.tipo == "lookup":
            ligacao = _ligacao(t, c, valor, k, inicio, ctx, r)
            if ligacao:
                pares.append((esquema(ctx.nomes.coluna(t, c)) + "@odata.bind", json.dumps(ligacao)))
        elif c.tipo == "choice":
            pares.append((nome, f"{OPCAO}{c.opcoes.index(valor):04d}"))
        else:
            pares.append((nome, _primitivo(valor)))
    return "{" + ",".join(f"{json.dumps(chave)}:{valor}" for chave, valor in pares) + "}"


def _lotes(t: Tabela, linhas_t: list[dict[str, Any]], ctx: Contexto, r: Relato) -> list[tuple[int, list[str]]]:
    """(posição da 1ª linha, corpos) de cada lote: até 100 linhas e cerca de 60 mil caracteres por lote."""
    lotes: list[tuple[int, list[str]]] = []
    inicio, corpos, tamanho = 0, [], 0
    for k, linha in enumerate(linhas_t):
        if corpos and (len(corpos) >= MAX_LINHAS_LOTE or tamanho > MAX_CORPO_LOTE):
            lotes.append((inicio, corpos))
            inicio, corpos, tamanho = k, [], 0
        corpo = linha_json(t, k, inicio, linha, ctx, r)
        if len(corpo) > MAX_LINHA:
            r.erro(t.nome, "C017", f"a linha {k + 1} passa de {MAX_LINHA} caracteres: não cabe num passo do flow; "
                                   "encurte os `exemplos`")
        corpos.append(corpo)
        tamanho += len(corpo)
    return [*lotes, (inicio, corpos)] if corpos else lotes


def lote(t: Tabela, corpos: list[str], nomes: Nomes, numero: int) -> tuple[str, str]:
    """Um `$batch` com um changeset só: o lote entra inteiro ou não entra. CRLF é exigência do formato."""
    chave = f"{t.nome.casefold()}/{numero}"
    fronteira = f"batch_{uuid.uuid5(NAMESPACE, 'lote/' + chave)}"
    mudancas = f"changeset_{uuid.uuid5(NAMESPACE, 'mudancas/' + chave)}"
    pedido = f"POST {API}/{conjunto(nomes.tabela(t))} HTTP/1.1"
    partes: list[str] = []
    for k, corpo in enumerate(corpos, start=1):
        partes += [f"--{mudancas}", "Content-Type: application/http", "Content-Transfer-Encoding: binary",
                   f"Content-ID: {k}", "", pedido, "Content-Type: application/json; type=entry", "", corpo]
    texto = CRLF.join([f"--{fronteira}", f"Content-Type: multipart/mixed; boundary={mudancas}", "", *partes,
                       f"--{mudancas}--", f"--{fronteira}--", ""])
    return f"multipart/mixed; boundary={fronteira}", texto


def passos_dados(t: Tabela, linhas_t: list[dict[str, Any]], ctx: Contexto, r: Relato) -> list[dict[str, Any]]:
    """Um passo por lote; cada um se confere pela 1ª linha dele, então rodar de novo pula o lote já gravado."""
    parte, total = ctx.nomes.tabela(t), len(linhas_t)
    chave = logico(parte) + "id"
    lotes = _lotes(t, linhas_t, ctx, r)
    passos = []
    for numero, (inicio, corpos) in enumerate(lotes, start=1):
        tipo, corpo = lote(t, corpos, ctx.nomes, numero)
        rotulo = (f"{t.nome}: {total} linha(s)" if len(lotes) == 1
                  else f"{t.nome}: linhas {inicio + 1}–{inicio + len(corpos)} de {total}")
        existe = f"{API}/{conjunto(parte)}?$select={chave}&$filter={chave}%20eq%20{id_da_linha(t, inicio + 1)}"
        passos.append(_passo("dados", rotulo, existe, "/$batch", corpo, tipo))
    return passos


# ---------- plano ----------

COMO_USAR = ("Rode o flow Construtor Dataverse: em Plano, este arquivo; em Solução, o nome exclusivo da solução não "
             "gerenciada. Gerado pelo kit: ajuste o spec e gere de novo, não edite à mão.")


def _checar_relacionamentos(lookups: list[tuple[Tabela, Coluna, Tabela]], nomes: Nomes, r: Relato) -> None:
    vistos: set[str] = set()
    for t, c, _ in lookups:
        nome = nome_relacionamento(t, c, nomes).lower()
        if nome in vistos:
            r.erro(f"{t.nome}.{c.nome}", "C016", f"relacionamento `{nome}` repetido: informe `logico` na coluna")
        vistos.add(nome)


def _resumo(passos: list[dict[str, Any]], linhas: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    def contar(fase: str) -> int:
        return sum(p["fase"] == fase for p in passos)
    return {"tabelas": contar("tabela"), "colunas": contar("tabela") + contar("coluna") + contar("relacionamento"),
            "relacionamentos": contar("relacionamento"), "lotes": contar("dados"),
            "linhas": sum(len(v) for v in linhas.values()), "chaves": contar("chave")}


def montar_plano(ordem: list[Tabela], linhas: dict[str, list[dict[str, Any]]], origem: str,
                 r: Relato) -> dict[str, Any] | None:
    nomes = resolver_nomes(ordem, r)
    checar_limites(ordem, linhas, r)
    if r.tem_erro:
        return None
    por_nome = {t.nome.casefold(): t for t in ordem}
    lookups = [(t, c, por_nome[(c.alvo or "").casefold()]) for t in ordem for c in t.colunas if c.tipo == "lookup"]
    _checar_relacionamentos(lookups, nomes, r)
    ctx = Contexto(nomes, por_nome, _posicoes(ordem, linhas))
    passos = [passo_tabela(t, nomes) for t in ordem]
    passos += [passo_coluna(t, c, nomes) for t in ordem for c in t.colunas
               if c.tipo not in SEM_COLUNA and not c.primaria]
    passos += [passo_relacionamento(t, c, alvo, nomes) for t, c, alvo in lookups]
    passos.append(passo_publicar(ordem, nomes))
    passos += [passo for t in ordem for passo in passos_dados(t, linhas[t.nome], ctx, r)]
    passos += [passo_chave(t, c, nomes) for t in ordem for c in (t.chave(),) if c]
    if r.tem_erro:
        return None
    return {"formato": FORMATO, "gerado_por": "montar-carga-mockup.py --flow", "origem": origem,
            "como_usar": COMO_USAR, "resumo": _resumo(passos, linhas),
            "passos": [{"n": n, **p} for n, p in enumerate(passos, start=1)]}


def resumo_texto(plano: dict[str, Any]) -> str:
    s = plano["resumo"]
    return (f"{len(plano['passos'])} passo(s): {s['tabelas']} tabela(s), {s['colunas']} coluna(s), "
            f"{s['relacionamentos']} relacionamento(s), {s['linhas']} linha(s) em {s['lotes']} lote(s), "
            f"{s['chaves']} chave(s)")


def plano_em_bytes(plano: dict[str, Any]) -> bytes:
    """UTF-8 sem BOM: o flow lê com base64ToString e o BOM quebraria o json()."""
    return (json.dumps(plano, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
