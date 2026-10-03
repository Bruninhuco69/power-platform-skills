"""Tipos de coluna, estruturas do spec e achados do `montar-carga-mockup.py`."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from _carga_xlsx import EST_DATA, EST_DATA_HORA, EST_DECIMAL, EST_MOEDA, EST_TEXTO, GERAL

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

CASAS_PADRAO = 2


@dataclass(frozen=True)
class Tipo:
    rotulo: str                  # o que escolher no Dataverse
    erro_comum: str              # o que a dedução de tipo costuma fazer errado
    atributos: frozenset[str]    # AttributeType esperado no export da Web API
    estilo: int = GERAL
    nome_tipo: str = ""          # trecho do AttributeTypeName quando o AttributeType é Virtual


def _t(rotulo: str, erro: str, *atributos: str, estilo: int = GERAL, nome_tipo: str = "") -> Tipo:
    return Tipo(rotulo, erro, frozenset(atributos), estilo, nome_tipo)


FORA_PLANILHA = tr("fora da planilha: a importação não aceita; crie à mão",
                  "outside the spreadsheet: the import does not accept it; create it by hand")
TIPOS: dict[str, Tipo] = {
    "texto": _t(tr("Texto de linha única (String)", "Single line of text (String)"),
                tr("tamanho máximo menor que o do modelo", "maximum length smaller than the model's"), "String"),
    "texto_longo": _t(tr("Várias linhas de texto (Memo)", "Multiple lines of text (Memo)"),
                      tr("vem como texto de linha única e corta o conteúdo",
                         "comes as single-line text and truncates the content"), "Memo"),
    "codigo": _t(tr("Texto de linha única (String), nunca número", "Single line of text (String), never number"),
                 tr("vem como número e perde o zero à esquerda", "comes as a number and loses the leading zero"),
                 "String", estilo=EST_TEXTO),
    "inteiro": _t(tr("Número inteiro (Integer)", "Whole number (Integer)"),
                  tr("vem como número decimal ou como texto", "comes as a decimal number or as text"),
                  "Integer", "BigInt"),
    "decimal": _t(tr("Número decimal (Decimal)", "Decimal number (Decimal)"),
                  tr("vem como número inteiro (arredonda), ponto flutuante ou texto",
                     "comes as a whole number (rounds), floating point or text"),
                  "Decimal", estilo=EST_DECIMAL),
    "moeda": _t(tr("Moeda (Money)", "Currency (Money)"), tr("vem como número decimal", "comes as a decimal number"),
                "Money", estilo=EST_MOEDA),
    "data": _t(tr("Data e hora com comportamento Somente data (DateTime)", "Date and time with Date only behavior (DateTime)"),
               tr("vem com hora (o fuso muda o dia) ou como texto", "comes with a time (the time zone changes the day) or as text"),
               "DateTime", estilo=EST_DATA),
    "data_hora": _t(tr("Data e hora (DateTime)", "Date and time (DateTime)"),
                    tr("vem como Somente data e perde a hora, ou como texto",
                       "comes as Date only and loses the time, or as text"),
                    "DateTime", estilo=EST_DATA_HORA),
    "sim_nao": _t(tr("Sim/Não (Boolean)", "Yes/No (Boolean)"),
                  tr("vem como texto ou como Escolha com Sim e Não", "comes as text or as a Choice with Yes and No"),
                  "Boolean"),
    "choice": _t(tr("Escolha (Picklist)", "Choice (Picklist)"),
                 tr("vem como texto, ou como Escolha só com as opções que apareceram",
                    "comes as text, or as a Choice with only the options that appeared"),
                 "Picklist"),
    "lookup": _t(tr("Pesquisa (Lookup)", "Lookup"),
                  tr("vem como texto: a importação não cria o relacionamento",
                     "comes as text: the import does not create the relationship"), "Lookup"),
    "email": _t(tr("Texto com formato Email (String)", "Text with Email format (String)"),
                 tr("vem como texto sem o formato Email", "comes as text without the Email format"), "String"),
    "telefone": _t(tr("Texto com formato Telefone (String)", "Text with Phone format (String)"),
                   tr("vem como número e perde parênteses e zeros", "comes as a number and loses parentheses and zeros"),
                   "String", estilo=EST_TEXTO),
    "url": _t(tr("Texto com formato URL (String)", "Text with URL format (String)"),
               tr("vem como texto sem o formato URL", "comes as text without the URL format"), "String"),
    "autonumero": _t(tr("Numeração automática (String)", "Autonumber (String)"),
                     tr("vem como texto comum: troque para Numeração automática", "comes as plain text: switch to Autonumber"),
                     "String", estilo=EST_TEXTO),
    "escolhas": _t(tr("Escolhas, várias opções (MultiSelect)", "Choices, multiple options (MultiSelect)"), FORA_PLANILHA,
                   "Virtual", nome_tipo="MultiSelect"),
    "imagem": _t(tr("Imagem", "Image"), FORA_PLANILHA, "Virtual", nome_tipo="Image"),
    "arquivo": _t(tr("Arquivo", "File"), FORA_PLANILHA, "Virtual", nome_tipo="File"),
    "calculada": _t(tr("Fórmula ou calculada", "Formula or calculated"),
                    tr("fora da planilha: crie à mão, depois das colunas que ela usa",
                       "outside the spreadsheet: create it by hand, after the columns it uses")),
}
TEXTUAIS = {"texto", "texto_longo", "codigo", "telefone", "email", "url", "autonumero"}
PRIMARIA_OK = {"texto", "codigo", "autonumero"}
CHAVE_OK = {"texto", "codigo", "inteiro", "email", "telefone", "url", "autonumero"}
COM_TAMANHO = TEXTUAIS - {"autonumero"}
COM_CASAS = {"decimal", "moeda"}
COM_OPCOES = {"choice", "escolhas"}
FORA_DA_CARGA = {"escolhas", "imagem", "arquivo"}
GERADO_PELO_BANCO = {"autonumero", "calculada"}  # SQL: IDENTITY/DEFAULT e coluna calculada ficam fora do INSERT


@dataclass(frozen=True)
class Achado:
    arquivo: str
    lugar: str
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        nivel = {"ERRO": tr("ERRO", "ERROR"), "AVISO": tr("AVISO", "WARNING")}.get(self.nivel, self.nivel)
        return f"{self.arquivo}:{self.lugar}: {nivel} {self.codigo} {self.mensagem}"


@dataclass(frozen=True)
class Coluna:
    nome: str
    tipo: str
    obrigatoria: bool = False
    primaria: bool = False
    chave: bool = False
    tamanho: int | None = None
    casas: int = CASAS_PADRAO
    opcoes: tuple[str, ...] = ()
    alvo: str | None = None
    exemplos: tuple[Any, ...] | None = None
    sql: str | None = None
    logico: str | None = None

    @property
    def exige_valor(self) -> bool:
        return self.obrigatoria or self.primaria or self.chave


@dataclass(frozen=True)
class Tabela:
    nome: str
    colunas: tuple[Coluna, ...]
    linhas: int | None = None
    sql: str | None = None
    pk: str | None = None
    logico: str | None = None

    def primaria(self) -> Coluna | None:
        return next((c for c in self.colunas if c.primaria), None)

    def chave(self) -> Coluna | None:
        return next((c for c in self.colunas if c.chave), None)

    def referencia(self, trilha: str) -> Coluna | None:
        """Coluna pela qual um Lookup acha a linha: no Dataverse, o nome principal; no SQL, a chave."""
        if trilha == "dataverse":
            return self.primaria()
        return self.chave() or self.primaria()


@dataclass(frozen=True)
class Spec:
    tabelas: tuple[Tabela, ...]
    linhas: int | None
    data_base: date
    trilha: str | None


class Relato:
    """Junta os achados de um arquivo de entrada."""

    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self.achados: list[Achado] = []

    def erro(self, lugar: str, codigo: str, mensagem: str) -> None:
        self.achados.append(Achado(self.arquivo, lugar, "ERRO", codigo, mensagem))

    def aviso(self, lugar: str, codigo: str, mensagem: str) -> None:
        self.achados.append(Achado(self.arquivo, lugar, "AVISO", codigo, mensagem))

    @property
    def tem_erro(self) -> bool:
        return any(a.nivel == "ERRO" for a in self.achados)


def na_carga(c: Coluna, trilha: str) -> bool:
    """A coluna vai para a planilha e para o INSERT? Fora: o que a importação não aceita e o que o banco gera."""
    if c.tipo in FORA_DA_CARGA:
        return False
    if trilha == "sql-server":
        return c.tipo not in GERADO_PELO_BANCO
    return c.tipo != "calculada"
