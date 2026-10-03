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

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

ATRIBUTOS_SISTEMA = {
    "createdon", "createdby", "createdonbehalfby", "modifiedon", "modifiedby", "modifiedonbehalfby",
    "ownerid", "owninguser", "owningteam", "owningbusinessunit", "statecode", "statuscode",
    "versionnumber", "importsequencenumber", "overriddencreatedon", "timezoneruleversionnumber",
    "utcconversiontimezonecode", "processid", "stageid", "traversedpath",
}
IDENTIFICADOR_NU = re.compile(r"^[^\W\d]\w*$")

# AttributeType da Web API -> (tipo no Power Fx, como comparar/gravar)
TIPOS = {
    "String": (tr("Texto", "Single line of text"),
               tr("texto = texto; delega `=`, `StartsWith`", "text = text; delegates `=`, `StartsWith`")),
    "Memo": (tr("Texto", "Multiple lines of text"),
             tr("texto longo; não filtrar por igualdade", "long text; do not filter by equality")),
    "Integer": (tr("Número", "Whole number"), tr("número = número", "number = number")),
    "BigInt": (tr("Número", "Whole number (BigInt)"), tr("número = número", "number = number")),
    "Decimal": (tr("Número", "Decimal number"), tr("número = número", "number = number")),
    "Double": (tr("Número", "Float"), tr("número = número", "number = number")),
    "Money": (tr("Número", "Currency"),
              tr("número; aritmética na coluna não delega", "number; arithmetic on the column does not delegate")),
    "Boolean": (tr("Booleano (Yes/No)", "Yes/No (Boolean)"),
                tr("`col = true`; também `'col (Tabela)'.Yes`", "`col = true`; also `'col (Table)'.Yes`")),
    "DateTime": (tr("Data/hora", "Date and time"),
                 tr("comparar com data; `Today()`/`Now()` guardados em variável",
                    "compare with a date; keep `Today()`/`Now()` in a variable")),
    "Picklist": (tr("Choice", "Choice"),
                 tr("`col = 'col (Tabela)'.Opção` ou `col.Value`; grava o registro da opção",
                    "`col = 'col (Table)'.Option` or `col.Value`; writes the option record")),
    "State": (tr("Choice", "Choice"), tr("`col = 'col (Tabela)'.Opção`", "`col = 'col (Table)'.Option`")),
    "Status": (tr("Choice", "Choice"), tr("`col = 'col (Tabela)'.Opção`", "`col = 'col (Table)'.Option`")),
    "Lookup": (tr("Registro (Lookup)", "Lookup"),
               tr("comparar com registro ou `col.'chave'`; grava o registro",
                  "compare with a record or `col.'key'`; writes the record")),
    "Customer": (tr("Registro (Lookup)", "Customer (Lookup)"),
                 tr("polimórfico; ver `references/nomes-e-tipos.md`", "polymorphic; see `references/names-and-types.md`")),
    "Owner": (tr("Registro (Lookup)", "Owner (Lookup)"),
              tr("polimórfico; ver `references/nomes-e-tipos.md`", "polymorphic; see `references/names-and-types.md`")),
    "Uniqueidentifier": (tr("GUID", "Unique identifier (GUID)"),
                         tr("comparar com GUID; `Text()` ao enviar para flow", "compare with a GUID; `Text()` when sending to a flow")),
    "Virtual": (tr("Virtual", "Virtual"),
                tr("ver `AttributeTypeName`; MultiSelect = tabela de Choices",
                   "see `AttributeTypeName`; MultiSelect = table of Choices")),
}
TIPO_DESCONHECIDO = ("?", tr("tipo não mapeado — conferir no maker", "type not mapped — check in the maker"))


@dataclass(frozen=True)
class Achado:
    caminho: str
    linha: int
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        nivel = tr(self.nivel, {"ERRO": "ERROR", "AVISO": "WARNING"}.get(self.nivel, self.nivel))
        return f"{self.caminho}:{self.linha}: {nivel} {self.codigo} {self.mensagem}"


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
        return (bruto, tr("Choice (múltipla)", "Choices (MultiSelect)"),
                tr("`col` é tabela; `'Opção' in col.Value`", "`col` is a table; `'Option' in col.Value`"))
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
                                  tr(f"`{logico}` sem `Attributes` — refazer a consulta com $expand=Attributes", f"`{logico}` without `Attributes` — redo the query with $expand=Attributes")))
            continue
        exibicoes: dict[str, int] = {}
        for atributo in atributos_de_negocio(entidade, prefixo):
            exib = rotulo(atributo.get("DisplayName"))
            if not exib:
                achados.append(Achado(caminho, numero, "AVISO", "A001",
                                      tr(f"`{logico}.{atributo.get('LogicalName')}` sem nome de exibição", f"`{logico}.{atributo.get('LogicalName')}` without a display name")))
            exibicoes[exib] = exibicoes.get(exib, 0) + 1
            if atributo.get("AttributeType") == "Picklist" and not opcoes_do_atributo(atributo):
                achados.append(Achado(caminho, numero, "AVISO", "A003",
                                      tr(f"`{logico}.{atributo.get('LogicalName')}` é Choice e as opções não vieram", f"`{logico}.{atributo.get('LogicalName')}` is a Choice and the options did not come")))
        for exib, qtd in exibicoes.items():
            if exib and qtd > 1:
                achados.append(Achado(caminho, numero, "AVISO", "D001",
                                      tr(f"`{logico}`: nome de exibição `{exib}` repetido {qtd}x — Power Fx ambíguo", f"`{logico}`: display name `{exib}` repeated {qtd}x — ambiguous in Power Fx")))
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
            notas.append(tr("chave primária", "primary key"))
            if exib == exib_tabela:
                notas.append(tr("exibição = nome da tabela: usar aspas", "display name = table name: use quotes"))
        if atributo.get("LogicalName") == entidade.get("PrimaryNameAttribute"):
            notas.append(tr("nome principal", "primary name"))
        if atributo.get("Targets"):
            notas.append(tr("aponta para ", "points to ") + ", ".join(f"`{t}`" for t in atributo["Targets"]))
        opcoes = opcoes_do_atributo(atributo)
        if opcoes:
            notas.append(tr("opções: ", "options: ") + "; ".join(opcoes))
            como = f"`'{exib} ({exib_tabela})'`: " + como
        linhas.append(f"| `{exib}` | `{atributo.get('LogicalName')}` | {bruto} | {pf} | {como} | {'; '.join(notas)} |")
    return linhas


def montar_markdown(entidades: list[dict], prefixo: str, origem: str) -> str:
    partes = [
        tr("# Nomes as-built do Dataverse", "# Dataverse as-built names"),
        "",
        tr("Gerado por `scripts/extrair-nomes-as-built.py` a partir de uma exportação da Web API "
           f"(`{origem}`). **Gerado — não editar à mão**: refaça a exportação e gere de novo.",
           "Generated by `scripts/extrair-nomes-as-built.py` from a Web API export "
           f"(`{origem}`). **Generated — do not edit by hand**: redo the export and generate again."),
        "",
        tr(f"- Prefixo do publisher: `{prefixo or '(não informado)'}`",
           f"- Publisher prefix: `{prefixo or '(not provided)'}`"),
        tr("- Ambiente: `<ambiente>` — exportado em `AAAA-MM-DD`",
           "- Environment: `<environment>` — exported on `YYYY-MM-DD`"),
        "",
        tr("## 1. Tabelas", "## 1. Tables"),
        "",
        tr("| Fonte de dados no Power Fx | Nome lógico | EntitySet (Web API/`$batch`) | Chave primária | Nome principal |",
           "| Data source in Power Fx | Logical name | EntitySet (Web API/`$batch`) | Primary key | Primary name |"),
        "|---|---|---|---|---|",
        *[linha_tabela(e) for e in entidades],
        "",
        tr("Em Power Fx, `SortByColumns`, `DisplayFields`, `SearchFields`, `ShowColumns` e afins recebem o "
           "**nome lógico** entre aspas; as demais fórmulas usam o **nome de exibição**.",
           "In Power Fx, `SortByColumns`, `DisplayFields`, `SearchFields`, `ShowColumns` and the like take the "
           "**logical name** in quotes; all other formulas use the **display name**."),
    ]
    for numero, entidade in enumerate(entidades, start=2):
        partes += [
            "",
            f"## {numero}. `{entidade['LogicalName']}`",
            "",
            tr("| Exibição (Power Fx) | Nome lógico (string, OData) | AttributeType | Tipo no Power Fx | Como comparar | Notas |",
               "| Display name (Power Fx) | Logical name (string, OData) | AttributeType | Type in Power Fx | How to compare | Notes |"),
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
            achados.append(Achado(par, 1, "ERRO", "E004", tr(f"--complemento: tabela `{tabela}` não está na entrada", f"--complemento: table `{tabela}` is not in the input")))
            continue
        try:
            dados = json.loads(Path(arquivo).read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as erro:
            achados.append(Achado(arquivo or par, 1, "ERRO", "E005", tr(f"--complemento ilegível: {erro}", f"--complemento unreadable: {erro}")))
            continue
        resultado[indice] = fundir_complemento(resultado[indice], dados)
    return resultado, achados


def carregar(caminho: Path) -> tuple[list[dict] | None, str]:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as erro:
        return None, tr(f"não foi possível ler o JSON: {erro}", f"could not read the JSON: {erro}")
    entidades = extrair_entidades(dados)
    if entidades is None:
        return None, tr("formato não reconhecido (esperado `{value: [...]}`, lista ou entidade com LogicalName)", "format not recognized (expected `{value: [...]}`, a list or an entity with LogicalName)")
    return entidades, ""


def filtrar_prefixo(entidades: list[dict], prefixo: str) -> list[dict]:
    if not prefixo:
        return entidades
    return [e for e in entidades if str(e["LogicalName"]).startswith(prefixo)]


def relatar(achados: list[Achado]) -> int:
    for achado in achados:
        print(achado.formatar(), file=sys.stderr)
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(tr(f"{erros} erro(s), {len(achados) - erros} aviso(s)", f"{erros} error(s), {len(achados) - erros} warning(s)"), file=sys.stderr)
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=tr(
        "Gera NOMES-AS-BUILT.md a partir de JSON da Web API (EntityDefinitions).",
        "Generates AS-BUILT-NAMES.md from Web API JSON (EntityDefinitions)."))
    parser.add_argument("entrada", type=Path, help=tr("JSON exportado (EntityDefinitions com Attributes)", "exported JSON (EntityDefinitions with Attributes)"))
    parser.add_argument("--prefixo", default="", help=tr("prefixo do publisher, ex.: `<prefixo>_` (filtra tabelas e colunas)",
                            "publisher prefix, e.g. `<prefix>_` (filters tables and columns)"))
    parser.add_argument("--complemento", action="append", default=[], metavar=tr("TABELA=ARQUIVO", "TABLE=FILE"),
                        help=tr("JSON de consulta com cast (Choice/Lookup) para a tabela; repetível",
                           "query JSON with cast (Choice/Lookup) for the table; repeatable"))
    parser.add_argument("--saida", help=tr("arquivo .md a escrever; `-` imprime no stdout. Sem a flag, só valida",
                            "`.md` file to write; `-` prints to stdout. Without the flag, it only validates"))
    args = parser.parse_args(argv)

    if not args.entrada.is_file():
        print(tr(f"arquivo inexistente: {args.entrada}", f"file not found: {args.entrada}"), file=sys.stderr)
        return 2
    if args.saida and args.saida != "-" and Path(args.saida).resolve() == args.entrada.resolve():
        print(tr("--saida não pode ser o próprio arquivo de entrada", "--saida cannot be the input file itself"),
              file=sys.stderr)
        return 2

    caminho = args.entrada.name
    entidades, erro = carregar(args.entrada)
    if entidades is None:
        return relatar([Achado(caminho, 1, "ERRO", "E001", erro)])
    selecionadas = filtrar_prefixo(entidades, args.prefixo)
    if not selecionadas:
        return relatar([Achado(caminho, 1, "ERRO", "E003", tr(f"nenhuma tabela com o prefixo `{args.prefixo}`", f"no table with the prefix `{args.prefixo}`"))])

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
