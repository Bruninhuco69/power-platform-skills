#!/usr/bin/env python3
"""Gera o NOMES-AS-BUILT.md a partir de um JSON exportado da Web API do Dataverse.

Entrada: arquivo local com a resposta de
    GET <org>/api/data/v9.2/EntityDefinitions?$select=LogicalName,SchemaName,EntitySetName,
        PrimaryIdAttribute,PrimaryNameAttribute,DisplayName&$expand=Attributes($select=LogicalName,
        SchemaName,AttributeType,AttributeTypeName,DisplayName,RequiredLevel)
Formatos aceitos: `{"value": [entidade, ...]}`, uma lista de entidades ou uma entidade só.
Choices e Lookups: a expansão de `Attributes` só traz as propriedades comuns. As opções de Choice
(`OptionSet`/`GlobalOptionSet`) e os destinos de Lookup (`Targets`) vêm de consultas com cast por
tabela; entregue-as com `--complemento <nome lógico da tabela>=<arquivo.json>` (repetível) e o
script as funde nos atributos de mesmo `LogicalName`.

Só lê o arquivo de entrada. Sem rede. Escreve apenas com --saida (nunca sobre a entrada).
Sem --saida o script só valida a entrada e relata os achados.

Saída de achados (stderr): `caminho:linha: ERRO|AVISO CÓDIGO mensagem` e, na última linha,
`N erro(s), M aviso(s)`. Exit: 0 sem erro, 1 com erro, 2 uso incorreto.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ATRIBUTOS_SISTEMA = {
    "createdon", "createdby", "createdonbehalfby", "modifiedon", "modifiedby", "modifiedonbehalfby",
    "ownerid", "owninguser", "owningteam", "owningbusinessunit", "statecode", "statuscode",
    "versionnumber", "importsequencenumber", "overriddencreatedon", "timezoneruleversionnumber",
    "utcconversiontimezonecode", "processid", "stageid", "traversedpath",
}
IDENTIFICADOR_NU = re.compile(r"^[^\W\d]\w*$")

# AttributeType da Web API -> (tipo no Power Fx, como comparar/gravar)
TIPOS = {
    "String": ("Texto", "texto = texto; delega `=`, `StartsWith`"),
    "Memo": ("Texto", "texto longo; não filtrar por igualdade"),
    "Integer": ("Número", "número = número"),
    "BigInt": ("Número", "número = número"),
    "Decimal": ("Número", "número = número"),
    "Double": ("Número", "número = número"),
    "Money": ("Número", "número; aritmética na coluna não delega"),
    "Boolean": ("Booleano (Yes/No)", "`col = true`; também `'col (Tabela)'.Yes`"),
    "DateTime": ("Data/hora", "comparar com data; `Today()`/`Now()` guardados em variável"),
    "Picklist": ("Choice", "`col = 'col (Tabela)'.Opção` ou `col.Value`; grava o registro da opção"),
    "State": ("Choice", "`col = 'col (Tabela)'.Opção`"),
    "Status": ("Choice", "`col = 'col (Tabela)'.Opção`"),
    "Lookup": ("Registro (Lookup)", "comparar com registro ou `col.'chave'`; grava o registro"),
    "Customer": ("Registro (Lookup)", "polimórfico; ver `references/nomes-e-tipos.md`"),
    "Owner": ("Registro (Lookup)", "polimórfico; ver `references/nomes-e-tipos.md`"),
    "Uniqueidentifier": ("GUID", "comparar com GUID; `Text()` ao enviar para flow"),
    "Virtual": ("Virtual", "ver `AttributeTypeName`; MultiSelect = tabela de Choices"),
}
TIPO_DESCONHECIDO = ("?", "tipo não mapeado — conferir no maker")


@dataclass(frozen=True)
class Achado:
    caminho: str
    linha: int
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        return f"{self.caminho}:{self.linha}: {self.nivel} {self.codigo} {self.mensagem}"


def rotulo(label: object) -> str:
    """Texto de um Label da Web API (`UserLocalizedLabel.Label` ou o 1º `LocalizedLabels`)."""
    if not isinstance(label, dict):
        return ""
    local = label.get("UserLocalizedLabel") or {}
    if isinstance(local, dict) and local.get("Label"):
        return str(local["Label"])
    for item in label.get("LocalizedLabels") or []:
        if isinstance(item, dict) and item.get("Label"):
            return str(item["Label"])
    return ""


def identificador_powerfx(nome: str) -> str:
    """Nome como se escreve em Power Fx: aspas simples quando não é identificador nu."""
    if IDENTIFICADOR_NU.match(nome):
        return nome
    return "'" + nome.replace("'", "''") + "'"


def extrair_entidades(dados: object) -> list[dict] | None:
    if isinstance(dados, dict) and isinstance(dados.get("value"), list):
        itens = dados["value"]
    elif isinstance(dados, dict) and "LogicalName" in dados:
        itens = [dados]
    elif isinstance(dados, list):
        itens = dados
    else:
        return None
    entidades = [i for i in itens if isinstance(i, dict) and i.get("LogicalName")]
    return entidades if len(entidades) == len(itens) else None


def tipo_do_atributo(atributo: dict) -> tuple[str, str, str]:
    bruto = str(atributo.get("AttributeType") or "")
    nome_tipo = (atributo.get("AttributeTypeName") or {}).get("Value", "")
    if bruto == "Virtual" and "MultiSelect" in str(nome_tipo):
        return bruto, "Choice (múltipla)", "`col` é tabela; `'Opção' in col.Value`"
    pf, como = TIPOS.get(bruto, TIPO_DESCONHECIDO)
    return bruto, pf, como


def opcoes_do_atributo(atributo: dict) -> list[str]:
    conjunto = atributo.get("OptionSet") or atributo.get("GlobalOptionSet") or {}
    saida = []
    for opcao in conjunto.get("Options") or [] if isinstance(conjunto, dict) else []:
        texto = rotulo(opcao.get("Label"))
        if texto:
            saida.append(f"{texto}={opcao.get('Value')}")
    return saida


def atributos_de_negocio(entidade: dict, prefixo: str) -> list[dict]:
    primarios = {entidade.get("PrimaryIdAttribute"), entidade.get("PrimaryNameAttribute")}
    saida = []
    for atributo in entidade.get("Attributes") or []:
        logico = str(atributo.get("LogicalName") or "")
        if logico in primarios or (logico not in ATRIBUTOS_SISTEMA and logico.startswith(prefixo)):
            saida.append(atributo)
    return saida


def validar(entidades: list[dict], prefixo: str, caminho: str) -> list[Achado]:
    achados: list[Achado] = []
    for numero, entidade in enumerate(entidades, start=1):
        logico = entidade["LogicalName"]
        if not entidade.get("Attributes"):
            achados.append(Achado(caminho, numero, "ERRO", "E002",
                                  f"`{logico}` sem `Attributes` — refazer a consulta com $expand=Attributes"))
            continue
        exibicoes: dict[str, int] = {}
        for atributo in atributos_de_negocio(entidade, prefixo):
            exib = rotulo(atributo.get("DisplayName"))
            if not exib:
                achados.append(Achado(caminho, numero, "AVISO", "A001",
                                      f"`{logico}.{atributo.get('LogicalName')}` sem nome de exibição"))
            exibicoes[exib] = exibicoes.get(exib, 0) + 1
            if atributo.get("AttributeType") == "Picklist" and not opcoes_do_atributo(atributo):
                achados.append(Achado(caminho, numero, "AVISO", "A003",
                                      f"`{logico}.{atributo.get('LogicalName')}` é Choice e as opções não vieram"))
        for exib, qtd in exibicoes.items():
            if exib and qtd > 1:
                achados.append(Achado(caminho, numero, "AVISO", "D001",
                                      f"`{logico}`: nome de exibição `{exib}` repetido {qtd}x — Power Fx ambíguo"))
    return achados


def linha_tabela(entidade: dict) -> str:
    exib = rotulo(entidade.get("DisplayName")) or entidade["LogicalName"]
    return (f"| `{identificador_powerfx(exib)}` | `{entidade['LogicalName']}` | "
            f"`{entidade.get('EntitySetName', '?')}` | `{entidade.get('PrimaryIdAttribute', '?')}` | "
            f"`{entidade.get('PrimaryNameAttribute', '?')}` |")


def linhas_colunas(entidade: dict, prefixo: str) -> list[str]:
    exib_tabela = rotulo(entidade.get("DisplayName")) or entidade["LogicalName"]
    linhas = []
    for atributo in sorted(atributos_de_negocio(entidade, prefixo), key=lambda a: a.get("LogicalName", "")):
        bruto, pf, como = tipo_do_atributo(atributo)
        exib = rotulo(atributo.get("DisplayName")) or "?"
        notas = []
        if atributo.get("LogicalName") == entidade.get("PrimaryIdAttribute"):
            notas.append("chave primária")
            if exib == exib_tabela:
                notas.append("exibição = nome da tabela: usar aspas")
        if atributo.get("LogicalName") == entidade.get("PrimaryNameAttribute"):
            notas.append("nome principal")
        if atributo.get("Targets"):
            notas.append("aponta para " + ", ".join(f"`{t}`" for t in atributo["Targets"]))
        opcoes = opcoes_do_atributo(atributo)
        if opcoes:
            notas.append("opções: " + "; ".join(opcoes))
            como = f"`'{exib} ({exib_tabela})'`: " + como
        linhas.append(f"| `{exib}` | `{atributo.get('LogicalName')}` | {bruto} | {pf} | {como} | {'; '.join(notas)} |")
    return linhas


def montar_markdown(entidades: list[dict], prefixo: str, origem: str) -> str:
    partes = [
        "# Nomes as-built do Dataverse",
        "",
        "Gerado por `scripts/extrair-nomes-as-built.py` a partir de uma exportação da Web API "
        f"(`{origem}`). **Gerado — não editar à mão**: refaça a exportação e gere de novo.",
        "",
        f"- Prefixo do publisher: `{prefixo or '(não informado)'}`",
        "- Ambiente: `<ambiente>` — exportado em `AAAA-MM-DD`",
        "",
        "## 1. Tabelas",
        "",
        "| Fonte de dados no Power Fx | Nome lógico | EntitySet (Web API/`$batch`) | Chave primária | Nome principal |",
        "|---|---|---|---|---|",
        *[linha_tabela(e) for e in entidades],
        "",
        "Em Power Fx, `SortByColumns`, `DisplayFields`, `SearchFields`, `ShowColumns` e afins recebem o "
        "**nome lógico** entre aspas; as demais fórmulas usam o **nome de exibição**.",
    ]
    for numero, entidade in enumerate(entidades, start=2):
        partes += [
            "",
            f"## {numero}. `{entidade['LogicalName']}`",
            "",
            "| Exibição (Power Fx) | Nome lógico (string, OData) | AttributeType | Tipo no Power Fx | Como comparar | Notas |",
            "|---|---|---|---|---|---|",
            *linhas_colunas(entidade, prefixo),
        ]
    return "\n".join(partes) + "\n"


def fundir_complemento(entidade: dict, complemento: object) -> dict:
    """Nova entidade com `OptionSet`/`GlobalOptionSet`/`Targets` do complemento fundidos nos atributos."""
    itens = complemento.get("value") if isinstance(complemento, dict) else complemento
    extras = {i["LogicalName"]: i for i in itens or [] if isinstance(i, dict) and i.get("LogicalName")}
    campos = ("OptionSet", "GlobalOptionSet", "Targets")
    atributos = [
        {**a, **{c: extras[a.get("LogicalName")][c] for c in campos if c in extras.get(a.get("LogicalName"), {})}}
        for a in entidade.get("Attributes") or []
    ]
    return {**entidade, "Attributes": atributos}


def aplicar_complementos(entidades: list[dict], pares: list[str]) -> tuple[list[dict], list[Achado]]:
    achados: list[Achado] = []
    resultado = list(entidades)
    for par in pares:
        tabela, _, arquivo = par.partition("=")
        indice = next((i for i, e in enumerate(resultado) if e["LogicalName"] == tabela), None)
        if indice is None:
            achados.append(Achado(par, 1, "ERRO", "E004", f"--complemento: tabela `{tabela}` não está na entrada"))
            continue
        try:
            dados = json.loads(Path(arquivo).read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as erro:
            achados.append(Achado(arquivo or par, 1, "ERRO", "E005", f"--complemento ilegível: {erro}"))
            continue
        resultado[indice] = fundir_complemento(resultado[indice], dados)
    return resultado, achados


def carregar(caminho: Path) -> tuple[list[dict] | None, str]:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as erro:
        return None, f"não foi possível ler o JSON: {erro}"
    entidades = extrair_entidades(dados)
    if entidades is None:
        return None, "formato não reconhecido (esperado `{value: [...]}`, lista ou entidade com LogicalName)"
    return entidades, ""


def filtrar_prefixo(entidades: list[dict], prefixo: str) -> list[dict]:
    if not prefixo:
        return entidades
    return [e for e in entidades if str(e["LogicalName"]).startswith(prefixo)]


def relatar(achados: list[Achado]) -> int:
    for achado in achados:
        print(achado.formatar(), file=sys.stderr)
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(f"{erros} erro(s), {len(achados) - erros} aviso(s)", file=sys.stderr)
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera NOMES-AS-BUILT.md a partir de JSON da Web API (EntityDefinitions).")
    parser.add_argument("entrada", type=Path, help="JSON exportado (EntityDefinitions com Attributes)")
    parser.add_argument("--prefixo", default="", help="prefixo do publisher, ex.: `<prefixo>_` (filtra tabelas e colunas)")
    parser.add_argument("--complemento", action="append", default=[], metavar="TABELA=ARQUIVO",
                        help="JSON de consulta com cast (Choice/Lookup) para a tabela; repetível")
    parser.add_argument("--saida", help="arquivo .md a escrever; `-` imprime no stdout. Sem a flag, só valida")
    args = parser.parse_args(argv)

    if not args.entrada.is_file():
        print(f"arquivo inexistente: {args.entrada}", file=sys.stderr)
        return 2
    if args.saida and args.saida != "-" and Path(args.saida).resolve() == args.entrada.resolve():
        print("--saida não pode ser o próprio arquivo de entrada", file=sys.stderr)
        return 2

    caminho = args.entrada.name
    entidades, erro = carregar(args.entrada)
    if entidades is None:
        return relatar([Achado(caminho, 1, "ERRO", "E001", erro)])
    selecionadas = filtrar_prefixo(entidades, args.prefixo)
    if not selecionadas:
        return relatar([Achado(caminho, 1, "ERRO", "E003", f"nenhuma tabela com o prefixo `{args.prefixo}`")])

    selecionadas, achados = aplicar_complementos(selecionadas, args.complemento)
    achados = achados + validar(selecionadas, args.prefixo, caminho)
    codigo = relatar(achados)
    if args.saida and codigo == 0:
        texto = montar_markdown(selecionadas, args.prefixo, caminho)
        if args.saida == "-":
            sys.stdout.write(texto)
        else:
            Path(args.saida).write_text(texto, encoding="utf-8")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
