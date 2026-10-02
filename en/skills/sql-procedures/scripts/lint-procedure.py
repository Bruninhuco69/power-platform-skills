#!/usr/bin/env python3
"""Lint de procedures e funcoes T-SQL (skill `sql-procedures`).

Le arquivos `.sql` e `.md` (blocos ```sql cercados), separa cada
CREATE/ALTER/CREATE OR ALTER PROCEDURE|FUNCTION e aplica regras de estilo e de
seguranca. Nao executa nada e nao escreve em disco.

Uso:
    python lint-procedure.py <arquivo|pasta> [...]
    python lint-procedure.py                       # usa pastas.procedures do config
    python lint-procedure.py x.sql --padrao-nome "^usp_[A-Za-z0-9_]+$"
    python lint-procedure.py x.sql --colunas-retorno ""      # desliga P004

Codigos:
    P001 SET NOCOUNT ON ausente            (ERRO em escrita, AVISO em leitura)
    P002 SET XACT_ABORT ON ausente         (ERRO, procedure de escrita)
    P003 BEGIN TRAN sem COMMIT             (ERRO)
    P004 retorno sem status/description/id/url   (AVISO, procedure de escrita)
    P005 nome fora do padrao               (AVISO)
    P006 CAST/CONVERT de data para INT     (AVISO, arredonda)
    P007 SELECT *                          (AVISO)
    P008 objeto sem schema                 (AVISO)
    P009 SQL dinamico com concatenacao     (ERRO)
    P010 NOLOCK / READUNCOMMITTED          (AVISO)
    P011 OUTPUT sem INTO em escrita        (AVISO)

Para dispensar um achado numa linha: comentario `-- lint-ok` (todos) ou
`-- lint-ok P009` (so aquele codigo), na linha do achado.

Configuracao (`power-platform.config.json`, procurado do diretorio atual para
cima, ou `--config`): `pastas.procedures`, `ignorar`, `padrao_nome_procedure`,
`colunas_retorno_procedure`.

Saida: `caminho:linha: ERRO|AVISO CODIGO mensagem` e, no fim,
`N erro(s), M aviso(s)`. Exit: 0 sem erro, 1 com erro, 2 uso incorreto.
"""
from __future__ import annotations

import argparse
import bisect
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

CONFIG_NOME = "power-platform.config.json"
PADRAO_NOME_PROCEDURE = r"^(usp|SP)_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+$"
PADRAO_NOME_FUNCAO = r"^(tvf|ufn|fn)_\w+$"
COLUNAS_RETORNO_PADRAO = ("status", "description", "id", "url")
EXTENSOES = {".sql", ".md"}
PASTAS_IGNORADAS = {"__pycache__", ".git", ".venv", "node_modules"}

IDENT = r"(?:\[[^\]]+\]|[A-Za-z_#@][\w$#@]*)"
QUALIFICADO = rf"{IDENT}(?:\s*\.\s*{IDENT})*"

RE_CRIAR = re.compile(
    rf"\b(?:CREATE\s+OR\s+ALTER|CREATE|ALTER)\s+(PROCEDURE|PROC|FUNCTION)\s+({QUALIFICADO})", re.I)
RE_GO = re.compile(r"^[ \t]*GO[ \t]*$", re.I | re.M)
RE_ESCRITA = re.compile(r"\b(?:INSERT|UPDATE|DELETE|MERGE)\b", re.I)
RE_NOCOUNT = re.compile(r"\bSET\s+NOCOUNT\s+ON\b", re.I)
RE_XACT = re.compile(r"\bSET\s+XACT_ABORT\s+ON\b", re.I)
RE_BEGIN_TRAN = re.compile(r"\bBEGIN\s+TRAN(?:SACTION)?\b", re.I)
RE_COMMIT = re.compile(r"\bCOMMIT\b", re.I)
RE_SELECT_STAR = re.compile(
    r"\bSELECT\s+(?:DISTINCT\s+)?(?:TOP\s*(?:\(\s*\w+\s*\)|\d+)\s+)?(?:\w+\.)?\*", re.I)
RE_EXISTS_ANTES = re.compile(r"EXISTS\s*\(\s*$", re.I)
RE_NOLOCK = re.compile(r"\b(?:NOLOCK|READUNCOMMITTED)\b", re.I)
RE_CAST = re.compile(r"\bCAST\s*\(", re.I)
RE_CONVERT = re.compile(r"\bCONVERT\s*\(", re.I)
RE_TIPO_INT = re.compile(r"^\s*(?:INT|INTEGER)\s*$", re.I)
RE_DATA = re.compile(
    r"(?<![A-Za-z])(?:dt|dta|data|date|getdate|getutcdate|sysdatetime|sysutcdatetime|current_timestamp)\w*",
    re.I)
RE_DATEDIFF = re.compile(r"^\s*DATEDIFF\s*\(", re.I)
RE_EXEC_PAREN = re.compile(r"\bEXEC(?:UTE)?\s*\(", re.I)
RE_SPEXEC = re.compile(r"\bsp_executesql\b\s*([^,;]*)", re.I)
RE_OUTPUT = re.compile(r"\bOUTPUT\s+(?:INSERTED|DELETED)\.|\bOUTPUT\s+\$action", re.I)
RE_FIM_OUTPUT = re.compile(r"\b(?:FROM|WHERE|VALUES|SELECT)\b|;", re.I)
RE_REF = re.compile(
    rf"\b(FROM|JOIN|INTO|UPDATE|MERGE(?:\s+INTO)?|INSERT(?:\s+INTO)?|DELETE(?:\s+FROM)?|EXEC(?:UTE)?)"
    rf"\s+({QUALIFICADO})(\s*\()?", re.I)
RE_CTE = re.compile(rf"(?:\bWITH|,)\s*({IDENT})\s*(?:\([^)]*\))?\s*AS\s*\(", re.I)
RE_ALIAS_AS = re.compile(rf"\bAS\s+({IDENT})", re.I)
RE_ALIAS_BARE = re.compile(rf"\b(?:FROM|JOIN)\s+{QUALIFICADO}\s+({IDENT})", re.I)
RE_LINT_OK = re.compile(r"lint-ok(?:[ \t]+((?:P\d{3}[,\s]*)+))?", re.I)
RE_FENCE_ABRE = re.compile(r"^\s*```+\s*(?:t?sql)\b", re.I)
RE_FENCE_FECHA = re.compile(r"^\s*```+\s*$")

PALAVRAS_NAO_ALIAS = {
    "set", "where", "with", "on", "inner", "left", "right", "cross", "outer", "join", "select",
    "values", "output", "using", "order", "group", "having", "union", "option", "full", "when",
    "as", "from", "into", "and", "or", "not", "where", "apply", "natural", "pivot", "unpivot",
}
OBJETOS_SEM_SCHEMA_OK = {
    "select", "values", "inserted", "deleted", "openjson", "string_split", "openquery",
    "openrowset", "openxml", "generate_series", "table",
}


class ErroUso(Exception):
    """Erro de uso (entrada invalida): vira exit 2."""


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


@dataclass(frozen=True)
class Opcoes:
    padrao_nome: re.Pattern
    padrao_funcao: re.Pattern
    colunas_retorno: tuple[str, ...]


@dataclass(frozen=True)
class Objeto:
    tipo: str          # PROCEDURE | FUNCTION
    nome: str          # sem schema, sem colchetes
    qualificado: str
    inicio: int
    corpo: str         # texto mascarado do objeto
    deslocamento: int  # posicao de `corpo` dentro do texto mascarado do segmento
    modelo: bool = False   # nome com placeholder (`usp_APP_<Entidade>`): so documentacao


def mascarar(texto: str) -> str:
    """Troca por espacos o conteudo de comentarios e de literais; preserva quebras de linha."""
    saida = list(texto)
    n = len(texto)

    def apagar(a: int, b: int) -> None:
        for k in range(a, min(b, n)):
            if saida[k] != "\n":
                saida[k] = " "

    i = 0
    while i < n:
        c = texto[i]
        if c == "-" and texto.startswith("--", i):
            j = texto.find("\n", i)
            j = n if j == -1 else j
            apagar(i, j)
            i = j
        elif c == "/" and texto.startswith("/*", i):
            profundidade, j = 1, i + 2
            while j < n and profundidade:
                if texto.startswith("/*", j):
                    profundidade, j = profundidade + 1, j + 2
                elif texto.startswith("*/", j):
                    profundidade, j = profundidade - 1, j + 2
                else:
                    j += 1
            apagar(i, j)
            i = j
        elif c == "'":
            j = i + 1
            while j < n:
                if texto[j] == "'":
                    if j + 1 < n and texto[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            apagar(i + 1, j)
            i = j + 1
        elif c == "[":
            j = texto.find("]", i)
            i = n if j == -1 else j + 1
        else:
            i += 1
    return "".join(saida)


def argumentos(texto: str, abre: int) -> tuple[str, int] | None:
    """Conteudo entre o parentese em `abre` e o fecho correspondente."""
    profundidade = 0
    for j in range(abre, len(texto)):
        if texto[j] == "(":
            profundidade += 1
        elif texto[j] == ")":
            profundidade -= 1
            if profundidade == 0:
                return texto[abre + 1:j], j
    return None


def dividir_topo(texto: str, separador: str) -> list[str]:
    """Divide em `separador` (caractere) so no nivel zero de parenteses."""
    partes, atual, profundidade = [], [], 0
    for ch in texto:
        if ch == "(":
            profundidade += 1
        elif ch == ")":
            profundidade -= 1
        if ch == separador and profundidade == 0:
            partes.append("".join(atual))
            atual = []
        else:
            atual.append(ch)
    partes.append("".join(atual))
    return partes


def partir_cast(args: str) -> tuple[str, str] | None:
    """Separa `expr AS tipo` no ultimo AS de nivel zero."""
    profundidade, ultimo = 0, -1
    for m in re.finditer(r"[()]|\bAS\b", args, re.I):
        if m.group() == "(":
            profundidade += 1
        elif m.group() == ")":
            profundidade -= 1
        elif profundidade == 0:
            ultimo = m.start()
    if ultimo < 0:
        return None
    return args[:ultimo], args[ultimo + 2:]


def nome_simples(qualificado: str) -> str:
    ultimo = re.split(r"\s*\.\s*", qualificado.strip())[-1]
    return ultimo.strip("[]")


def tem_schema(qualificado: str) -> bool:
    return len(re.split(r"\s*\.\s*", qualificado.strip())) >= 2


def separar_objetos(mascarado: str) -> list[Objeto]:
    inicios = list(RE_CRIAR.finditer(mascarado))
    gos = [m.start() for m in RE_GO.finditer(mascarado)]
    objetos = []
    for idx, m in enumerate(inicios):
        fim = inicios[idx + 1].start() if idx + 1 < len(inicios) else len(mascarado)
        go = next((g for g in gos if g > m.start()), None)
        if go is not None and go < fim:
            fim = go
        objetos.append(Objeto(
            tipo="FUNCTION" if m.group(1).upper() == "FUNCTION" else "PROCEDURE",
            nome=nome_simples(m.group(2)), qualificado=m.group(2),
            inicio=m.start(), corpo=mascarado[m.start():fim], deslocamento=m.start(),
            modelo=mascarado[m.end():m.end() + 1] == "<"))
    return objetos


Ocorrencia = tuple[int, str, str, str]  # (posicao no corpo, nivel, codigo, mensagem)


def checar_envelope(obj: Objeto, escrita: bool) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    if obj.tipo != "PROCEDURE":
        return achados
    if not RE_NOCOUNT.search(obj.corpo):
        nivel = "ERRO" if escrita else "AVISO"
        achados.append((0, nivel, "P001", tr(
            f"`{obj.nome}` sem `SET NOCOUNT ON`: o rowcount de cada DML vira result set "
            "e o conector pode ler o resultado errado",
            f"`{obj.nome}` without `SET NOCOUNT ON`: each DML's rowcount becomes a result set "
            "and the connector may read the wrong result")))
    if escrita and not RE_XACT.search(obj.corpo):
        achados.append((0, "ERRO", "P002", tr(
            f"`{obj.nome}` grava sem `SET XACT_ABORT ON`: erro em runtime pode deixar "
            "transacao aberta ou escrita parcial",
            f"`{obj.nome}` writes without `SET XACT_ABORT ON`: a runtime error can leave "
            "a transaction open or a partial write")))
    begins = list(RE_BEGIN_TRAN.finditer(obj.corpo))
    if len(begins) > len(RE_COMMIT.findall(obj.corpo)):
        achados.append((begins[0].start(), "ERRO", "P003", tr(
            f"`{obj.nome}`: BEGIN TRAN sem COMMIT correspondente",
            f"`{obj.nome}`: BEGIN TRAN without a matching COMMIT")))
    return achados


def checar_retorno(obj: Objeto, opcoes: Opcoes) -> list[Ocorrencia]:
    faltando = [c for c in opcoes.colunas_retorno
                if not re.search(rf"(?<![@\w]){re.escape(c)}\b", obj.corpo, re.I)]
    if not faltando:
        return []
    return [(0, "AVISO", "P004", tr(
        f"`{obj.nome}` sem as colunas de retorno {', '.join(faltando)} "
        f"(contrato: {', '.join(opcoes.colunas_retorno)}; heuristica por nome de alias)",
        f"`{obj.nome}` missing the return columns {', '.join(faltando)} "
        f"(contract: {', '.join(opcoes.colunas_retorno)}; heuristic based on alias names)"))]


def checar_nome(obj: Objeto, opcoes: Opcoes) -> list[Ocorrencia]:
    padrao = opcoes.padrao_nome if obj.tipo == "PROCEDURE" else opcoes.padrao_funcao
    achados: list[Ocorrencia] = []
    if not padrao.search(obj.nome):
        achados.append((0, "AVISO", "P005", tr(
            f"nome `{obj.nome}` fora do padrao `{padrao.pattern}` "
            "(o nome real vem do ambiente; ajuste o padrao no config se for o caso)",
            f"name `{obj.nome}` does not match the pattern `{padrao.pattern}` "
            "(the real name comes from the environment; adjust the pattern in the config if needed)")))
    if not tem_schema(obj.qualificado):
        achados.append((0, "AVISO", "P008", tr(
            f"`{obj.nome}` criado sem schema (use `dbo.`)",
            f"`{obj.nome}` created without a schema (use `dbo.`)")))
    return achados


def checar_cast_int(obj: Objeto) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    msg = tr("conversao de data para INT arredonda (13h vira o dia seguinte); "
             "use DATEDIFF(day, 0, <col>) para o numero do dia",
             "converting a date to INT rounds (1 pm becomes the next day); "
             "use DATEDIFF(day, 0, <col>) for the day number")
    for m in RE_CAST.finditer(obj.corpo):
        r = argumentos(obj.corpo, m.end() - 1)
        partes = partir_cast(r[0]) if r else None
        if partes and RE_TIPO_INT.match(partes[1]) and RE_DATA.search(partes[0]) \
                and not RE_DATEDIFF.match(partes[0]):
            achados.append((m.start(), "AVISO", "P006", f"CAST(... AS INT): {msg}"))
    for m in RE_CONVERT.finditer(obj.corpo):
        r = argumentos(obj.corpo, m.end() - 1)
        partes = dividir_topo(r[0], ",") if r else []
        if len(partes) >= 2 and RE_TIPO_INT.match(partes[0]) and RE_DATA.search(partes[1]) \
                and not RE_DATEDIFF.match(partes[1]):
            achados.append((m.start(), "AVISO", "P006", f"CONVERT(INT, ...): {msg}"))
    return achados


def checar_select_estrela(obj: Objeto) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    for m in RE_SELECT_STAR.finditer(obj.corpo):
        antes = obj.corpo[max(0, m.start() - 30):m.start()]
        if RE_EXISTS_ANTES.search(antes):
            continue
        achados.append((m.start(), "AVISO", "P007", tr(
            "SELECT *: liste as colunas (o contrato de retorno nao pode mudar com o DDL)",
            "SELECT *: list the columns (the return contract must not change with the DDL)")))
    return achados


def aliases_e_ctes(corpo: str) -> set[str]:
    nomes = {m.group(1).strip("[]").lower() for m in RE_CTE.finditer(corpo)}
    nomes |= {m.group(1).strip("[]").lower() for m in RE_ALIAS_AS.finditer(corpo)}
    for m in RE_ALIAS_BARE.finditer(corpo):
        candidato = m.group(1).strip("[]").lower()
        if candidato not in PALAVRAS_NAO_ALIAS:
            nomes.add(candidato)
    return nomes


def checar_schema(obj: Objeto) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    conhecidos = aliases_e_ctes(obj.corpo)
    for m in RE_REF.finditer(obj.corpo):
        palavra, token, chama = m.group(1).upper(), m.group(2), m.group(3)
        funcao = bool(chama) and palavra in ("FROM", "JOIN")
        if tem_schema(token) or funcao:
            continue
        simples = nome_simples(token).lower()
        if token[0] in "@#" or simples in OBJETOS_SEM_SCHEMA_OK or simples in conhecidos:
            continue
        if m.group(1).upper().startswith("EXEC") and simples.startswith(("sp_", "xp_")):
            continue
        achados.append((m.start(2), "AVISO", "P008", tr(
            f"`{token}` sem schema: qualifique (`dbo.{nome_simples(token)}`)",
            f"`{token}` without a schema: qualify it (`dbo.{nome_simples(token)}`)")))
    return achados


def _atribuicao_com_concat(corpo: str, variavel: str) -> bool:
    return bool(re.search(rf"{re.escape(variavel)}\s*=[^;]*\+", corpo))


def checar_sql_dinamico(obj: Objeto) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    msg = tr("SQL dinamico montado por concatenacao: use sp_executesql com parametros "
             "(e QUOTENAME para nome de objeto)",
             "dynamic SQL built by concatenation: use sp_executesql with parameters "
             "(and QUOTENAME for object names)")
    for m in RE_EXEC_PAREN.finditer(obj.corpo):
        r = argumentos(obj.corpo, m.end() - 1)
        if not r:
            continue
        arg = r[0].strip()
        var = re.match(r"@\w+$", arg)
        if "+" in arg or (var and _atribuicao_com_concat(obj.corpo, arg)):
            achados.append((m.start(), "ERRO", "P009", msg))
    for m in RE_SPEXEC.finditer(obj.corpo):
        arg = m.group(1).strip()
        var = re.match(r"@\w+\b", arg)
        if "+" in arg or (var and _atribuicao_com_concat(obj.corpo, var.group())):
            achados.append((m.start(), "ERRO", "P009", msg))
    return achados


def checar_nolock(obj: Objeto) -> list[Ocorrencia]:
    return [(m.start(), "AVISO", "P010", tr(
        f"{m.group().upper()}: leitura suja (linhas duplicadas ou perdidas); nao use em procedure de negocio",
        f"{m.group().upper()}: dirty read (duplicated or missed rows); do not use in a business procedure"))
            for m in RE_NOLOCK.finditer(obj.corpo)]


def checar_output(obj: Objeto) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    for m in RE_OUTPUT.finditer(obj.corpo):
        fim = RE_FIM_OUTPUT.search(obj.corpo, m.end())
        janela = obj.corpo[m.start():fim.start() if fim else len(obj.corpo)]
        if not re.search(r"\bINTO\b", janela, re.I):
            achados.append((m.start(), "AVISO", "P011", tr(
                "OUTPUT sem INTO devolve linhas ao cliente (vira Table1 e rouba o retorno) "
                "e nao funciona em tabela com trigger; use OUTPUT ... INTO @tabela",
                "OUTPUT without INTO returns rows to the client (becomes Table1 and steals the return) "
                "and does not work on a table with a trigger; use OUTPUT ... INTO @table")))
    return achados


def so_assinatura(obj: Objeto) -> bool:
    """Fragmento de documentacao: CREATE ... AS sem corpo."""
    m = re.search(r"\bAS\b", obj.corpo, re.I)
    return bool(m) and not obj.corpo[m.end():].strip()


def analisar_objeto(obj: Objeto, opcoes: Opcoes) -> list[Ocorrencia]:
    if obj.modelo:
        return []
    if so_assinatura(obj):
        return checar_nome(obj, opcoes)
    escrita = obj.tipo == "PROCEDURE" and bool(RE_ESCRITA.search(obj.corpo))
    achados = checar_envelope(obj, escrita) + checar_nome(obj, opcoes)
    achados += checar_cast_int(obj) + checar_select_estrela(obj) + checar_schema(obj)
    achados += checar_sql_dinamico(obj) + checar_nolock(obj)
    if escrita:
        achados += checar_output(obj)
        if opcoes.colunas_retorno:
            achados += checar_retorno(obj, opcoes)
    return achados


def dispensado(linha_bruta: str, codigo: str) -> bool:
    m = RE_LINT_OK.search(linha_bruta)
    if not m:
        return False
    codigos = m.group(1)
    return codigos is None or codigo in re.findall(r"P\d{3}", codigos.upper())


def analisar_segmento(texto: str, rotulo: str, linha_base: int, opcoes: Opcoes) -> tuple[list[Achado], int]:
    mascarado = mascarar(texto)
    quebras = [i for i, ch in enumerate(texto) if ch == "\n"]
    linhas = texto.split("\n")
    achados: list[Achado] = []
    objetos = separar_objetos(mascarado)
    for obj in objetos:
        for pos, nivel, codigo, mensagem in analisar_objeto(obj, opcoes):
            idx = bisect.bisect_left(quebras, obj.deslocamento + pos)
            if dispensado(linhas[idx] if idx < len(linhas) else "", codigo):
                continue
            achados.append(Achado(rotulo, linha_base + idx + 1, nivel, codigo, mensagem))
    return achados, len(objetos)


def extrair_blocos_sql(texto_md: str) -> list[tuple[str, int]]:
    """Blocos ```sql cercados: (conteudo, linhas antes do bloco)."""
    blocos, dentro, atual, base = [], False, [], 0
    for numero, linha in enumerate(texto_md.split("\n")):
        if not dentro and RE_FENCE_ABRE.match(linha):
            dentro, atual, base = True, [], numero + 1
        elif dentro and RE_FENCE_FECHA.match(linha):
            blocos.append(("\n".join(atual), base))
            dentro = False
        elif dentro:
            atual.append(linha)
    return blocos


def analisar_arquivo(caminho: Path, rotulo: str, opcoes: Opcoes) -> tuple[list[Achado], int]:
    texto = caminho.read_text(encoding="utf-8-sig", errors="replace")
    if caminho.suffix.lower() == ".md":
        achados, total = [], 0
        for conteudo, base in extrair_blocos_sql(texto):
            a, n = analisar_segmento(conteudo, rotulo, base, opcoes)
            achados += a
            total += n
        return achados, total
    return analisar_segmento(texto, rotulo, 0, opcoes)


def casa_glob(relativo: str, padrao: str) -> bool:
    regex, i = "", 0
    while i < len(padrao):
        if padrao.startswith("**/", i):
            regex, i = regex + "(?:.*/)?", i + 3
        elif padrao.startswith("**", i):
            regex, i = regex + ".*", i + 2
        elif padrao[i] == "*":
            regex, i = regex + "[^/]*", i + 1
        elif padrao[i] == "?":
            regex, i = regex + "[^/]", i + 1
        else:
            regex, i = regex + re.escape(padrao[i]), i + 1
    return re.fullmatch(regex, relativo) is not None


def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / CONFIG_NOME
        if candidato.is_file():
            return candidato
    return None


def carregar_config(caminho: Path) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as erro:
        raise ErroUso(tr(f"config invalido ({caminho}): {erro}",
                         f"invalid config ({caminho}): {erro}")) from erro
    if not isinstance(dados, dict):
        raise ErroUso(tr(f"config invalido ({caminho}): a raiz deve ser um objeto JSON",
                         f"invalid config ({caminho}): the root must be a JSON object"))
    return dados


def compilar(padrao: str, origem: str) -> re.Pattern:
    try:
        return re.compile(padrao)
    except re.error as erro:
        raise ErroUso(tr(f"regex invalido em {origem}: {erro}",
                         f"invalid regex in {origem}: {erro}")) from erro


def montar_opcoes(args: argparse.Namespace, cfg: dict) -> Opcoes:
    padrao = args.padrao_nome or cfg.get("padrao_nome_procedure") or PADRAO_NOME_PROCEDURE
    if args.colunas_retorno is not None:
        colunas = [c.strip() for c in args.colunas_retorno.split(",") if c.strip()]
    else:
        bruto = cfg.get("colunas_retorno_procedure", list(COLUNAS_RETORNO_PADRAO))
        colunas = [c.strip() for c in (bruto.split(",") if isinstance(bruto, str) else bruto) if str(c).strip()]
    return Opcoes(compilar(padrao, "--padrao-nome/config"), compilar(PADRAO_NOME_FUNCAO, "padrao"),
                  tuple(colunas))


def coletar_arquivos(alvos: list[Path], base: Path, ignorar: list[str]) -> list[tuple[Path, str]]:
    achados: dict[Path, str] = {}
    for alvo in alvos:
        candidatos = [alvo] if alvo.is_file() else sorted(alvo.rglob("*"))
        for p in candidatos:
            if not p.is_file() or p.suffix.lower() not in EXTENSOES:
                continue
            if any(parte in PASTAS_IGNORADAS for parte in p.parts):
                continue
            try:
                rel = p.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                rel = p.as_posix()
            if any(casa_glob(rel, g) for g in ignorar):
                continue
            achados[p.resolve()] = rel
    return sorted(((p, r) for p, r in achados.items()), key=lambda x: x[1])


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lint-procedure.py", description=tr(
            "Lint de procedures e funcoes T-SQL (.sql e .md com blocos sql).",
            "Lint for T-SQL procedures and functions (.sql and .md with sql blocks)."))
    parser.add_argument("caminhos", nargs="*", type=Path,
                        help=tr("arquivos ou pastas (default: pastas.procedures do config)",
                                "files or folders (default: pastas.procedures from the config)"))
    parser.add_argument("--config", type=Path, help=tr(
        f"arquivo {CONFIG_NOME} (default: procurado para cima)",
        f"{CONFIG_NOME} file (default: searched upward)"))
    parser.add_argument("--padrao-nome", help=tr(
        "regex do nome de procedure (default aceita usp_ e SP_)",
        "regex for the procedure name (default accepts usp_ and SP_)"))
    parser.add_argument("--colunas-retorno",
                        help=tr("colunas exigidas no retorno, separadas por virgula; vazio desliga P004",
                                "columns required in the return, comma-separated; empty turns P004 off"))
    return parser


def resolver_config(args: argparse.Namespace) -> tuple[dict, Path]:
    if args.config:
        if not args.config.is_file():
            raise ErroUso(tr(f"config inexistente: {args.config}",
                             f"config does not exist: {args.config}"))
        return carregar_config(args.config), args.config.resolve().parent
    achado = achar_config(Path.cwd())
    if achado:
        return carregar_config(achado), achado.parent
    print(tr(f"# sem {CONFIG_NOME}: usando defaults genericos",
             f"# no {CONFIG_NOME}: using generic defaults"))
    return {}, Path.cwd()


def executar(args: argparse.Namespace) -> int:
    cfg, base = resolver_config(args)
    opcoes = montar_opcoes(args, cfg)
    pastas = (cfg.get("pastas") or {}).get("procedures") or ["."]
    alvos = args.caminhos or [base / p for p in pastas]
    inexistentes = [a for a in alvos if not a.exists()]
    if inexistentes:
        raise ErroUso(tr(f"caminho inexistente: {inexistentes[0]}",
                         f"path does not exist: {inexistentes[0]}"))
    arquivos = coletar_arquivos(alvos, base, list(cfg.get("ignorar") or []))
    if not arquivos:
        raise ErroUso(tr("nenhum .sql ou .md encontrado", "no .sql or .md found"))
    achados: list[Achado] = []
    objetos = 0
    for caminho, rotulo in arquivos:
        a, n = analisar_arquivo(caminho, rotulo, opcoes)
        achados += a
        objetos += n
    for achado in sorted(achados, key=lambda x: (x.caminho, x.linha, x.codigo)):
        print(achado.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(tr(f"# {len(arquivos)} arquivo(s), {objetos} objeto(s) analisado(s)",
             f"# {len(arquivos)} file(s), {objetos} object(s) analyzed"))
    print(tr(f"{erros} erro(s), {len(achados) - erros} aviso(s)",
             f"{erros} error(s), {len(achados) - erros} warning(s)"))
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return executar(args)
    except ErroUso as erro:
        print(tr(f"erro: {erro}", f"error: {erro}"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
