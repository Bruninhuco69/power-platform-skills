"""Tipos de coluna, estruturas do spec e achados do `montar-carga-mockup.py`."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from _carga_xlsx import EST_DATA, EST_DATA_HORA, EST_DECIMAL, EST_MOEDA, EST_TEXTO, GERAL

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


TIPOS: dict[str, Tipo] = {
    "texto": _t("Texto de linha única (String)", "tamanho máximo menor que o do modelo", "String"),
    "texto_longo": _t("Várias linhas de texto (Memo)", "vem como texto de linha única e corta o conteúdo", "Memo"),
    "codigo": _t("Texto de linha única (String), nunca número", "vem como número e perde o zero à esquerda",
                 "String", estilo=EST_TEXTO),
    "inteiro": _t("Número inteiro (Integer)", "vem como número decimal ou como texto", "Integer", "BigInt"),
    "decimal": _t("Número decimal (Decimal)", "vem como número inteiro (arredonda), ponto flutuante ou texto",
                  "Decimal", estilo=EST_DECIMAL),
    "moeda": _t("Moeda (Money)", "vem como número decimal", "Money", estilo=EST_MOEDA),
    "data": _t("Data e hora com comportamento Somente data (DateTime)",
               "vem com hora (o fuso muda o dia) ou como texto", "DateTime", estilo=EST_DATA),
    "data_hora": _t("Data e hora (DateTime)", "vem como Somente data e perde a hora, ou como texto",
                    "DateTime", estilo=EST_DATA_HORA),
    "sim_nao": _t("Sim/Não (Boolean)", "vem como texto ou como Escolha com Sim e Não", "Boolean"),
    "choice": _t("Escolha (Picklist)", "vem como texto, ou como Escolha só com as opções que apareceram",
                 "Picklist"),
    "lookup": _t("Pesquisa (Lookup)", "vem como texto: a importação não cria o relacionamento", "Lookup"),
    "email": _t("Texto com formato Email (String)", "vem como texto sem o formato Email", "String"),
    "telefone": _t("Texto com formato Telefone (String)", "vem como número e perde parênteses e zeros",
                   "String", estilo=EST_TEXTO),
    "url": _t("Texto com formato URL (String)", "vem como texto sem o formato URL", "String"),
    "autonumero": _t("Numeração automática (String)", "vem como texto comum: troque para Numeração automática",
                     "String", estilo=EST_TEXTO),
    "escolhas": _t("Escolhas, várias opções (MultiSelect)", "fora da planilha: a importação não aceita; crie à mão",
                   "Virtual", nome_tipo="MultiSelect"),
    "imagem": _t("Imagem", "fora da planilha: a importação não aceita; crie à mão", "Virtual", nome_tipo="Image"),
    "arquivo": _t("Arquivo", "fora da planilha: a importação não aceita; crie à mão", "Virtual", nome_tipo="File"),
    "calculada": _t("Fórmula ou calculada", "fora da planilha: crie à mão, depois das colunas que ela usa"),
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
        return f"{self.arquivo}:{self.lugar}: {self.nivel} {self.codigo} {self.mensagem}"


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
