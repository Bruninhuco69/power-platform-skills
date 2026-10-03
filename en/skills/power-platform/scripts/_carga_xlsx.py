"""Gravador mínimo de .xlsx para o `montar-carga-mockup.py` (SpreadsheetML com zipfile, sem dependência).

Uma tabela do Excel por aba, cabeçalho congelado, valor tipado na célula (texto, número, data, booleano).
A mesma entrada dá os mesmos bytes: data fixa nas entradas do zip e nenhuma propriedade com hora.
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from xml.sax.saxutils import escape, quoteattr

XML_PROIBIDO = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
EPOCA_EXCEL = date(1899, 12, 30)

# estilos de célula (índice em cellXfs do styles.xml)
GERAL, CABECALHO, EST_DATA, EST_DATA_HORA, EST_DECIMAL, EST_MOEDA, EST_TEXTO, EST_QUEBRA = range(8)


@dataclass(frozen=True)
class Aba:
    nome: str
    cabecalho: tuple[str, ...]
    linhas: tuple[tuple[Any, ...], ...]
    estilos: tuple[int, ...]
    titulo: tuple[str, ...] = ()
    larguras: tuple[float, ...] | None = None


def sem_acento(texto: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(ch))


def _letra_coluna(numero: int) -> str:
    saida = ""
    while numero:
        numero, resto = divmod(numero - 1, 26)
        saida = chr(65 + resto) + saida
    return saida


def _xml_texto(texto: str) -> str:
    return escape(XML_PROIBIDO.sub("", texto))


def _serial(valor: date) -> str:
    if isinstance(valor, datetime):
        dias = (valor.date() - EPOCA_EXCEL).days
        fracao = (valor.hour * 3600 + valor.minute * 60 + valor.second) / 86400
        return f"{dias + fracao:.10f}".rstrip("0").rstrip(".")
    return str((valor - EPOCA_EXCEL).days)


def _celula(ref: str, valor: Any, estilo: int) -> str:
    s = f' s="{estilo}"' if estilo else ""
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return f'<c r="{ref}" t="b"{s}><v>{int(valor)}</v></c>'
    if isinstance(valor, (int, Decimal)):
        return f'<c r="{ref}"{s}><v>{format(valor, "f") if isinstance(valor, Decimal) else valor}</v></c>'
    if isinstance(valor, date):
        return f'<c r="{ref}"{s}><v>{_serial(valor)}</v></c>'
    return f'<c r="{ref}" t="inlineStr"{s}><is><t xml:space="preserve">{_xml_texto(str(valor))}</t></is></c>'


def _largura(aba: Aba, indice: int) -> float:
    """Largura em caracteres: cabeçalho com folga para o botão do filtro; booleano como o Excel pt-BR mostra."""
    if aba.larguras:
        return aba.larguras[indice]
    medidas = [len(aba.cabecalho[indice]) + 4]
    for linha in aba.linhas:
        valor = linha[indice]
        if isinstance(valor, bool):
            medidas.append(15)  # "VERDADEIRO" em maiúscula: a unidade de largura é a do dígito, mais estreito
        elif valor is not None:
            medidas.append(len(str(valor)) + 2)
    return float(min(60, max(10, *medidas)))


def _folha(aba: Aba, ativa: bool) -> str:
    cab_linha = len(aba.titulo) + 1
    ultima = _letra_coluna(len(aba.cabecalho))
    fim = cab_linha + len(aba.linhas)
    linhas = [f'<row r="{n}">{_celula(f"A{n}", texto, CABECALHO if n == 1 else GERAL)}</row>'
              for n, texto in enumerate(aba.titulo, start=1)]
    cab = "".join(_celula(f"{_letra_coluna(k)}{cab_linha}", nome, CABECALHO)
                  for k, nome in enumerate(aba.cabecalho, start=1))
    linhas.append(f'<row r="{cab_linha}">{cab}</row>')
    for n, linha in enumerate(aba.linhas, start=cab_linha + 1):
        celulas = "".join(_celula(f"{_letra_coluna(k)}{n}", v, aba.estilos[k - 1])
                          for k, v in enumerate(linha, start=1))
        linhas.append(f'<row r="{n}">{celulas}</row>')
    cols = "".join(f'<col min="{k}" max="{k}" width="{_largura(aba, k - 1):g}" customWidth="1"/>'
                   for k in range(1, len(aba.cabecalho) + 1))
    selecionada = ' tabSelected="1"' if ativa else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="A1:{ultima}{fim}"/>'
        f'<sheetViews><sheetView workbookViewId="0"{selecionada}><pane ySplit="{cab_linha}" '
        f'topLeftCell="A{cab_linha + 1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f'<sheetFormatPr defaultRowHeight="15"/><cols>{cols}</cols>'
        f'<sheetData>{"".join(linhas)}</sheetData>'
        '<tableParts count="1"><tablePart r:id="rId1"/></tableParts></worksheet>'
    )


def _nome_tabela_excel(nome: str, usados: set[str]) -> str:
    base = "t_" + (re.sub(r"[^A-Za-z0-9_]+", "_", sem_acento(nome)).strip("_") or "tabela")
    candidato, n = base, 2
    while candidato.casefold() in usados:
        candidato, n = f"{base}_{n}", n + 1
    usados.add(candidato.casefold())
    return candidato


def _tabela_excel(aba: Aba, numero: int, nome: str) -> str:
    cab_linha = len(aba.titulo) + 1
    ref = f"A{cab_linha}:{_letra_coluna(len(aba.cabecalho))}{cab_linha + len(aba.linhas)}"
    colunas = "".join(f'<tableColumn id="{k}" name={quoteattr(XML_PROIBIDO.sub("", c))}/>'
                      for k, c in enumerate(aba.cabecalho, start=1))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<table xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" id="{numero}" '
        f'name="{nome}" displayName="{nome}" ref="{ref}" totalsRowShown="0">'
        f'<autoFilter ref="{ref}"/><tableColumns count="{len(aba.cabecalho)}">{colunas}</tableColumns>'
        '<tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" showLastColumn="0" '
        'showRowStripes="1" showColumnStripes="0"/></table>'
    )


ESTILOS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<numFmts count="3"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/>'
    '<numFmt numFmtId="165" formatCode="yyyy-mm-dd hh:mm"/>'
    '<numFmt numFmtId="166" formatCode="&quot;R$&quot; #,##0.00"/></numFmts>'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/><family val="2"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/><family val="2"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="8">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="166" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="49" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">'
    '<alignment vertical="top" wrapText="1"/></xf>'
    '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
TIPO_CONTEUDO = "application/vnd.openxmlformats-officedocument.spreadsheetml"


def _relacoes(itens: list[tuple[str, str]]) -> str:
    corpo = "".join(f'<Relationship Id="rId{n}" Type="{tipo}" Target="{alvo}"/>'
                    for n, (tipo, alvo) in enumerate(itens, start=1))
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<Relationships xmlns="{NS_PKG}">{corpo}</Relationships>')


def xlsx(abas: list[Aba]) -> bytes:
    """Pasta de trabalho com uma tabela do Excel por aba. Bytes iguais para a mesma entrada."""
    usados: set[str] = set()
    n = len(abas)
    sobrescritas = "".join(
        f'<Override PartName="/xl/worksheets/sheet{k}.xml" ContentType="{TIPO_CONTEUDO}.worksheet+xml"/>'
        f'<Override PartName="/xl/tables/table{k}.xml" ContentType="{TIPO_CONTEUDO}.table+xml"/>'
        for k in range(1, n + 1))
    partes = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{TIPO_CONTEUDO}.sheet.main+xml"/>'
            f'<Override PartName="/xl/styles.xml" ContentType="{TIPO_CONTEUDO}.styles+xml"/>'
            f'{sobrescritas}</Types>'),
        "_rels/.rels": _relacoes([(f"{NS_REL}/officeDocument", "xl/workbook.xml")]),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{NS_REL}">'
            '<bookViews><workbookView activeTab="0"/></bookViews><sheets>'
            + "".join(f'<sheet name={quoteattr(a.nome)} sheetId="{k}" r:id="rId{k}"/>'
                      for k, a in enumerate(abas, start=1))
            + '</sheets></workbook>'),
        "xl/_rels/workbook.xml.rels": _relacoes(
            [(f"{NS_REL}/worksheet", f"worksheets/sheet{k}.xml") for k in range(1, n + 1)]
            + [(f"{NS_REL}/styles", "styles.xml")]),
        "xl/styles.xml": ESTILOS_XML,
    }
    for k, aba in enumerate(abas, start=1):
        partes[f"xl/worksheets/sheet{k}.xml"] = _folha(aba, k == 1)
        partes[f"xl/worksheets/_rels/sheet{k}.xml.rels"] = _relacoes([(f"{NS_REL}/table", f"../tables/table{k}.xml")])
        partes[f"xl/tables/table{k}.xml"] = _tabela_excel(aba, k, _nome_tabela_excel(aba.nome, usados))
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, conteudo in partes.items():
            z.writestr(zipfile.ZipInfo(nome, date_time=(1980, 1, 1, 0, 0, 0)), conteudo.encode("utf-8"),
                       compress_type=zipfile.ZIP_DEFLATED)
    return memoria.getvalue()
