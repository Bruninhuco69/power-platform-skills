#!/usr/bin/env python3
"""Verificador de flows do Power Automate (somente leitura).

Formatos de entrada suportados:
  1. Clipboard do designer novo, nó de ESCOPO  (`nodeId` + `serializedValue`) -- `.json`
     ou `.md` que contenha só o JSON (cerca ``` opcional).
  2. Clipboard do designer novo, nó FOLHA      (`nodeId` + `nodeData`) -- só identidade
     do nó e expressões (um nó folha não traz a árvore do flow).
  3. `definition` de solução exportada: `properties.definition`, `definition` ou a
     definição crua (`actions` / `triggers` na raiz).

Saída: `caminho:ação: ERRO|AVISO Fnnn mensagem` (em JSON de uma linha o "lugar" é o nome
da ação, não a linha). Última linha: `N erro(s), M aviso(s)`.
Exit: 0 sem erro, 1 com erro, 2 uso incorreto.

Configuração: `power-platform.config.json` (procurado do diretório atual para cima, ou
`--config`): `pastas.flows` (onde procurar quando nenhum caminho é dado) e `ignorar` (globs).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOME_CONFIG = "power-platform.config.json"
LIMITE_EXPRESSAO = 8192
ALERTA_EXPRESSAO = int(LIMITE_EXPRESSAO * 0.8)
CAMPOS_RESPOSTA = ("status", "description", "id", "url")
CHAVES_ESCOPO = {"nodeId", "serializedValue", "allConnectionData", "staticResults", "isScopeNode", "mslaNode"}
CHAVES_FOLHA = {"nodeId", "nodeData", "nodeTokenData", "nodeOperationInfo", "nodeConnectionData",
                "isScopeNode", "mslaNode"}
TIPOS_COM_ENVELOPE_BODY = {"Select", "Query"}
NOMES_CONFIG_PADRAO = ("CONFIG",)
CHAVES_TOPO_IGNORADAS = {"metadata", "runAfter", "description", "actions", "else", "cases", "default",
                         "runtimeConfiguration"}
CHAVES_IGNORADAS = {"schema", "host"}
CHAVES_DEV = re.compile(r"(?i)table|entity|tabela|database|banco|server|servidor|procedure|dataset|uri|url")

RE_GUID = re.compile(r"\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b")
RE_SERVIDOR = re.compile(r"(?i)\b[a-z0-9_-]{3,}\\[a-z0-9_-]{2,}\b|\.database\.windows\.net|\.crm\d*\.dynamics\.com")
RE_DEV = re.compile(r"(?i)(?<![a-z])dev(?!ice|elop|olv)")
RE_REF_ACAO = re.compile(r"\b(outputs|body|actions|result)\(\s*'([^']+)'\s*\)")
RE_ITEMS = re.compile(r"\bitems\(\s*'([^']+)'\s*\)")
RE_VARIAVEL_PURA = re.compile(r"^(?:@variables\('([^']+)'\)|@\{variables\('([^']+)'\)\})$")
RE_CONSTANTE = re.compile(r"\bequals\(\s*(-?\d+(?:\.\d+)?|'[^']*')\s*,\s*(-?\d+(?:\.\d+)?|'[^']*')\s*\)")


@dataclass(frozen=True)
class Achado:
    caminho: str
    lugar: str
    nivel: str
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        nivel = tr(self.nivel, {"ERRO": "ERROR", "AVISO": "WARNING"}.get(self.nivel, self.nivel))
        return f"{self.caminho}:{self.lugar}: {nivel} {self.codigo} {self.mensagem}"


@dataclass
class Contexto:
    caminho: str
    achados: list[Achado] = field(default_factory=list)
    fragmento: bool = False
    powerapps: bool = False
    estrito: bool = False
    colagem: bool = False  # envelope do clipboard: o trecho entra no designer por Ctrl+V
    nomes_config: tuple[str, ...] = NOMES_CONFIG_PADRAO

    def erro(self, lugar: str, codigo: str, msg: str) -> None:
        self.achados.append(Achado(self.caminho, lugar, "ERRO", codigo, msg))

    def aviso(self, lugar: str, codigo: str, msg: str) -> None:
        self.achados.append(Achado(self.caminho, lugar, "AVISO", codigo, msg))


# ----------------------------------------------------------------- travessia

@dataclass
class No:
    nome: str
    dados: dict
    irmaos: dict
    foreachs: tuple[str, ...]
    pai: "No | None" = None


def _filhos(nome: str, dados: dict) -> Iterator[tuple[str, dict, str | None]]:
    """(rótulo do bloco, dict de ações, nome do caso quando for caso de Switch)."""
    if isinstance(dados.get("actions"), dict):
        yield "actions", dados["actions"], None
    senao = dados.get("else")
    if isinstance(senao, dict) and isinstance(senao.get("actions"), dict):
        yield "else", senao["actions"], None
    for caso, corpo in (dados.get("cases") or {}).items():
        if isinstance(corpo, dict) and isinstance(corpo.get("actions"), dict):
            yield "case", corpo["actions"], caso
    padrao = dados.get("default")
    if isinstance(padrao, dict) and isinstance(padrao.get("actions"), dict):
        yield "default", padrao["actions"], None


def percorrer(acoes: dict, foreachs: tuple[str, ...] = (), pai: No | None = None) -> Iterator[No]:
    for nome, dados in acoes.items():
        if not isinstance(dados, dict):
            continue
        no = No(nome, dados, acoes, foreachs, pai)
        yield no
        pilha = foreachs + (nome,) if dados.get("type") == "Foreach" else foreachs
        for _, filhos, _caso in _filhos(nome, dados):
            yield from percorrer(filhos, pilha, no)


def textos_de(valor: Any, rotulo: str = "") -> Iterator[tuple[str, str]]:
    """Strings de um nó (sem filhos, metadata, runAfter...), com o caminho da chave."""
    if isinstance(valor, str):
        yield rotulo, valor
    elif isinstance(valor, dict):
        for chave, sub in valor.items():
            if chave in CHAVES_IGNORADAS or (not rotulo and chave in CHAVES_TOPO_IGNORADAS):
                continue
            yield from textos_de(sub, f"{rotulo}.{chave}" if rotulo else chave)
    elif isinstance(valor, list):
        for i, sub in enumerate(valor):
            yield from textos_de(sub, f"{rotulo}[{i}]")


def eh_expressao(texto: str) -> bool:
    return texto.startswith("@") or "@{" in texto


def dividir_argumentos(expr: str, abre: int) -> list[str]:
    """Argumentos de nível 0 da chamada cujo `(` está em expr[abre]."""
    args, atual, nivel, i, em_texto = [], [], 0, abre + 1, False
    while i < len(expr):
        c = expr[i]
        if em_texto:
            atual.append(c)
            if c == "'":
                if i + 1 < len(expr) and expr[i + 1] == "'":
                    atual.append("'")
                    i += 1
                else:
                    em_texto = False
        elif c == "'":
            em_texto = True
            atual.append(c)
        elif c in "([{":
            nivel += 1
            atual.append(c)
        elif c in ")]}":
            if nivel == 0:
                args.append("".join(atual))
                return args
            nivel -= 1
            atual.append(c)
        elif c == "," and nivel == 0:
            args.append("".join(atual))
            atual = []
        else:
            atual.append(c)
        i += 1
    return args


# ------------------------------------------------------------------- regras

def checar_identidade_e_nomes(ctx: Contexto, acoes: dict, raiz_nome: str | None) -> dict[str, str]:
    """F004 (duplicado) e F008 (caso colidindo). Devolve nome -> tipo ('acao'|'caso')."""
    vistos: dict[str, str] = {}
    if raiz_nome:
        vistos[raiz_nome] = "acao"

    def registrar(nome: str, tipo: str, lugar: str) -> None:
        if nome in vistos:
            if tipo == "acao" and vistos[nome] == "acao":
                ctx.erro(lugar, "F004", tr(f"nome de ação duplicado `{nome}` -- o designer renomeia a segunda para `{nome}_1` e os tokens continuam no original", f"duplicate action name `{nome}` -- the designer renames the second one to `{nome}_1` and the tokens stay on the original"))
            else:
                rotulo = {"acao": tr("ação", "action"), "caso": tr("caso", "case")}
                ctx.erro(lugar, "F008", tr(f"`{nome}` é {rotulo[tipo]} e também {rotulo[vistos[nome]]}: caso de Switch e ação dividem o mesmo espaço de nomes do designer (a colagem falha com `Required property 'case' not found`)", f"`{nome}` is {rotulo[tipo]} and also {rotulo[vistos[nome]]}: a Switch case and an action share the same designer namespace (pasting fails with `Required property 'case' not found`)"))
        else:
            vistos[nome] = tipo

    def visitar(blocos: dict) -> None:
        for nome, dados in blocos.items():
            if not isinstance(dados, dict):
                continue
            registrar(nome, "acao", nome)
            for rotulo, filhos, caso in _filhos(nome, dados):
                if rotulo != "case":
                    visitar(filhos)
            for caso, corpo in (dados.get("cases") or {}).items():
                registrar(caso, "caso", nome)
                if not isinstance(corpo, dict) or corpo.get("case") in (None, ""):
                    ctx.erro(nome, "F008", tr(f"caso `{caso}` sem a propriedade `case` (ou vazia) -- nunca casa", f"case `{caso}` without the `case` property (or empty) -- it never matches"))
                if isinstance(corpo, dict) and isinstance(corpo.get("actions"), dict):
                    visitar(corpo["actions"])

    visitar(acoes)
    return vistos


def checar_run_after(ctx: Contexto, acoes: dict, todos: set[str], raiz_externa: str | None) -> None:
    for no in percorrer(acoes):
        if no.nome == raiz_externa:
            continue  # o runAfter da raiz aponta para um nó que já existe no ponto da colagem
        for alvo in (no.dados.get("runAfter") or {}):
            if alvo in no.irmaos:
                continue
            if alvo in todos:
                ctx.erro(no.nome, "F005", tr(f"runAfter aponta para `{alvo}`, que existe mas não é irmã desta ação (outro nível)", f"runAfter points to `{alvo}`, which exists but is not a sibling of this action (different level)"))
            else:
                ctx.erro(no.nome, "F005", tr(f"runAfter aponta para `{alvo}`, que não existe no flow", f"runAfter points to `{alvo}`, which does not exist in the flow"))


def checar_referencias(ctx: Contexto, acoes: dict, todos: set[str], tipos: dict[str, str]) -> None:
    emitir = ctx.aviso if ctx.fragmento else ctx.erro
    sufixo = tr(" (fragmento: pode existir fora do trecho colado)", " (fragment: it may exist outside the pasted snippet)") if ctx.fragmento else ""
    for no in percorrer(acoes):
        for rotulo, texto in textos_de({k: v for k, v in no.dados.items() if k not in ("actions", "else", "cases", "default")}):
            if not eh_expressao(texto):
                continue
            for m in RE_REF_ACAO.finditer(texto):
                if m.group(2) not in todos:
                    emitir(no.nome, "F006", tr(f"`{m.group(1)}('{m.group(2)}')` em {rotulo}: ação inexistente{sufixo}", f"`{m.group(1)}('{m.group(2)}')` in {rotulo}: action does not exist{sufixo}"))
            for m in RE_ITEMS.finditer(texto):
                alvo = m.group(1)
                if alvo in no.foreachs:
                    continue
                if alvo in todos:
                    ctx.erro(no.nome, "F007", tr(f"`items('{alvo}')` fora do Foreach `{alvo}` (em {rotulo})", f"`items('{alvo}')` outside the Foreach `{alvo}` (in {rotulo})"))
                else:
                    emitir(no.nome, "F007", tr(f"`items('{alvo}')` em {rotulo}: não há Foreach com esse nome{sufixo}", f"`items('{alvo}')` in {rotulo}: there is no Foreach with that name{sufixo}"))
            for m in RE_REF_ACAO.finditer(texto):
                if m.group(1) != "outputs" or tipos.get(m.group(2)) not in TIPOS_COM_ENVELOPE_BODY:
                    continue
                resto = texto[m.end():m.end() + 12].replace(" ", "")
                if resto.startswith(("?['body", "['body")):
                    continue
                ctx.erro(no.nome, "F011", tr(f"`outputs('{m.group(2)}')` em ação {tipos[m.group(2)]}: devolve o envelope, não a lista -- use `body('{m.group(2)}')` (R13)", f"`outputs('{m.group(2)}')` on a {tipos[m.group(2)]} action: returns the envelope, not the list -- use `body('{m.group(2)}')` (R13)"))


def checar_catch(ctx: Contexto, acoes: dict) -> None:
    for no in percorrer(acoes):
        if no.dados.get("type") != "Scope":
            continue
        for alvo, estados in (no.dados.get("runAfter") or {}).items():
            if not isinstance(estados, list) or "Skipped" in estados:
                continue
            if "Failed" in estados or "TimedOut" in estados:
                emite = ctx.erro if re.search(r"(?i)catch", no.nome) else ctx.aviso
                emite(no.nome, "F009", tr(f"escopo de tratamento de erro sem `Skipped` no runAfter de `{alvo}` ({estados}): se um irmão anterior ao Try falhar, o Try fica Skipped e este escopo também -- a execução termina sem Response", f"error-handling scope without `Skipped` in the runAfter of `{alvo}` ({estados}): if a sibling before the Try fails, the Try is Skipped and so is this scope -- the run ends without a Response"))


def checar_respostas(ctx: Contexto, acoes: dict) -> None:
    for no in percorrer(acoes):
        if no.dados.get("type") != "Response":
            continue
        kind = no.dados.get("kind")
        eh_powerapps = kind == "PowerApp" or (ctx.powerapps and kind != "Http")
        corpo = (no.dados.get("inputs") or {}).get("body")
        if eh_powerapps and isinstance(corpo, dict):
            faltam = [c for c in CAMPOS_RESPOSTA if c not in corpo]
            if faltam:
                ctx.erro(no.nome, "F010", tr(f"Response do Power Apps sem {faltam}: os 4 campos saem sempre, mesmo vazios", f"Power Apps Response without {faltam}: all 4 fields are always returned, even when empty"))
        dependentes = [n for n, d in no.irmaos.items() if isinstance(d, dict) and no.nome in (d.get("runAfter") or {})]
        if any(no.irmaos[n].get("type") == "Terminate" for n in dependentes) or not segue(no):
            continue
        if eh_powerapps:
            ctx.erro(no.nome, "F015", tr("Response sem Terminate e o flow continua depois dela: Response não para o flow, o próximo nó roda com a resposta já enviada", "Response without Terminate and the flow continues after it: Response does not stop the flow, the next node runs with the response already sent"))
        else:
            ctx.aviso(no.nome, "F015", tr("resposta HTTP antecipada (o flow continua depois de responder): confirme que é aceite assíncrono e que falhas posteriores chegam ao log", "early HTTP response (the flow continues after responding): confirm it is an asynchronous accept and that later failures reach the log"))


def segue(no: No) -> bool:
    """True se alguma ação pode rodar depois de `no` quando ele termina bem (sobe pelos blocos pai)."""
    for n, d in no.irmaos.items():
        estados = (d.get("runAfter") or {}).get(no.nome) if isinstance(d, dict) else None
        if estados and "Succeeded" in estados:
            return True
    return segue(no.pai) if no.pai else False


def _constante(a: Any, b: Any) -> bool:
    def literal(x: Any) -> bool:
        return not (isinstance(x, str) and x.strip().startswith("@")) and not isinstance(x, (dict, list))
    return literal(a) and literal(b) and a == b


def _folhas_condicao(expr: Any) -> Iterator[Any]:
    if isinstance(expr, dict):
        for chave, sub in expr.items():
            if chave == "equals" and isinstance(sub, list) and len(sub) == 2:
                yield sub
            else:
                yield from _folhas_condicao(sub)
    elif isinstance(expr, list):
        for sub in expr:
            yield from _folhas_condicao(sub)


def checar_condicoes(ctx: Contexto, acoes: dict) -> None:
    for no in percorrer(acoes):
        if no.dados.get("type") != "If":
            continue
        expr = no.dados.get("expression")
        constante = any(_constante(par[0], par[1]) for par in _folhas_condicao(expr))
        if isinstance(expr, str):
            constante = constante or any(m.group(1) == m.group(2) for m in RE_CONSTANTE.finditer(expr))
        if constante:
            ctx.erro(no.nome, "F016", tr("condição compara duas constantes iguais (sempre verdadeira): o ramo `else` é código morto", "condition compares two equal constants (always true): the `else` branch is dead code"))
        if isinstance(expr, str):
            ctx.erro(no.nome, "F020", tr("condição do `If` em texto: o designer novo mostra a condição em branco; escreva como objeto "
                                         "`{\"and\": [{\"equals\": [\"@<expressão>\", \"@true\"]}]}`",
                                         "`If` condition as text: the new designer shows the condition blank; write it as an object "
                                         "`{\"and\": [{\"equals\": [\"@<expression>\", \"@true\"]}]}`"))
        elif isinstance(expr, dict) and (len(expr) != 1 or next(iter(expr)) not in ("and", "or")):
            ctx.aviso(no.nome, "F020", tr("condição sem `and`/`or` na raiz: o designer grava sempre um dos dois, e a forma sem eles "
                                          "não foi vista colando; embrulhe em `{\"and\": [...]}`",
                                          "condition without `and`/`or` at the root: the designer always writes one of the two, and the form without them "
                                          "has not been seen pasting; wrap it in `{\"and\": [...]}`"))


def _variaveis_iniciadas(acoes: dict) -> set[str]:
    return {v.get("name") for no in percorrer(acoes) if no.dados.get("type") == "InitializeVariable"
            for v in (no.dados.get("inputs") or {}).get("variables") or [] if isinstance(v, dict)}


def checar_variaveis(ctx: Contexto, acoes: dict) -> None:
    """F021 (Inicializar variável fora da raiz) e F022 (`@variables('x')` sozinho num campo, só na colagem)."""
    for no in percorrer(acoes):
        if no.dados.get("type") == "InitializeVariable" and no.pai is not None:
            if ctx.colagem:
                ctx.aviso(no.nome, "F021", tr("Inicializar variável dentro do trecho colado: só vale na raiz do flow; arraste para "
                                              "fora (entre o gatilho e o escopo) antes de salvar",
                                              "Initialize variable inside the pasted snippet: it only works at the flow root; drag it "
                                              "out (between the trigger and the scope) before saving"))
            else:
                ctx.erro(no.nome, "F021", tr("Inicializar variável só vale na raiz do flow: dentro de escopo, condição ou laço o "
                                             "flow não salva",
                                             "Initialize variable only works at the flow root: inside a scope, condition or loop the "
                                             "flow does not save"))
    if not ctx.colagem:
        return
    iniciadas = _variaveis_iniciadas(acoes)
    for no in percorrer(acoes):
        for rotulo, texto in textos_de({k: v for k, v in no.dados.items() if k not in ("actions", "else", "cases", "default")}):
            m = RE_VARIAVEL_PURA.match(texto.strip())
            if not m:
                continue
            nome = m.group(1) or m.group(2)
            troca = tr(f"use uma expressão com função (`@skip(variables('{nome}'), 0)`, `@equals(variables('{nome}'), true)`)", f"use an expression with a function (`@skip(variables('{nome}'), 0)`, `@equals(variables('{nome}'), true)`)")
            if nome in iniciadas:
                ctx.erro(no.nome, "F022", tr(f"`variables('{nome}')` sozinho em {rotulo}: vira token de variável, e a variável é "
                                             f"iniciada dentro do trecho colado; o token não resolve e o campo cola em branco: {troca}",
                                             f"`variables('{nome}')` alone in {rotulo}: it becomes a variable token, and the variable is "
                                             f"initialized inside the pasted snippet; the token does not resolve and the field pastes blank: {troca}"))
            else:
                ctx.aviso(no.nome, "F022", tr(f"`variables('{nome}')` sozinho em {rotulo}: vira token de variável na colagem; "
                                             f"confira o campo depois de colar, ou {troca}",
                                             f"`variables('{nome}')` alone in {rotulo}: it becomes a variable token on paste; "
                                             f"check the field after pasting, or {troca}"))


def checar_fazer_ate(ctx: Contexto, acoes: dict) -> None:
    if not ctx.colagem:
        return  # na definição exportada o Until em texto é a forma normal
    for no in percorrer(acoes):
        if no.dados.get("type") == "Until" and isinstance(no.dados.get("expression"), str):
            ctx.aviso(no.nome, "F023", tr("condição do `Fazer até` em texto: ainda não vista colando no designer novo; se vier em "
                                         "branco, abra o modo avançado e cole a mesma expressão",
                                         "`Do until` condition as text: not yet seen pasting in the new designer; if it comes in "
                                         "blank, open advanced mode and paste the same expression"))


def checar_expressoes(ctx: Contexto, acoes: dict) -> None:
    for no in percorrer(acoes):
        for rotulo, texto in textos_de({k: v for k, v in no.dados.items() if k not in ("actions", "else", "cases", "default")}):
            if not eh_expressao(texto):
                continue
            achar_expressoes_longas(ctx, no.nome, rotulo, texto)
            checar_coalesce_string(ctx, no.nome, rotulo, texto)


def achar_expressoes_longas(ctx: Contexto, nome: str, rotulo: str, texto: str) -> None:
    tamanho = len(texto)
    if tamanho > LIMITE_EXPRESSAO:
        ctx.erro(nome, "F013", tr(f"expressão de {tamanho} caracteres em {rotulo} (limite da plataforma: {LIMITE_EXPRESSAO}); extraia para um Compose", f"expression of {tamanho} characters in {rotulo} (platform limit: {LIMITE_EXPRESSAO}); extract it to a Compose"))
    elif tamanho > ALERTA_EXPRESSAO:
        ctx.aviso(nome, "F013", tr(f"expressão de {tamanho} caracteres em {rotulo}: {100 * tamanho // LIMITE_EXPRESSAO}% do limite de {LIMITE_EXPRESSAO}", f"expression of {tamanho} characters in {rotulo}: {100 * tamanho // LIMITE_EXPRESSAO}% of the {LIMITE_EXPRESSAO} limit"))


def checar_coalesce_string(ctx: Contexto, nome: str, rotulo: str, texto: str) -> None:
    for m in re.finditer(r"\bcoalesce\(", texto):
        args = dividir_argumentos(texto, m.end() - 1)
        if len(args) < 2 or not args[0].strip().startswith("string("):
            continue
        fallback = args[1].strip()
        if fallback == "''" and not ctx.estrito:
            continue
        ctx.aviso(nome, "F012", tr(f"`coalesce(string(...), {fallback[:20]})` em {rotulo}: `string(null)` devolve '' (não nulo), o fallback nunca entra (R12)", f"`coalesce(string(...), {fallback[:20]})` in {rotulo}: `string(null)` returns '' (not null), the fallback never applies (R12)"))
        return


def checar_literais_de_ambiente(ctx: Contexto, acoes: dict) -> None:
    for no in percorrer(acoes):
        if no.nome in ctx.nomes_config:
            continue
        achados: dict[str, str] = {}
        corpo = {k: v for k, v in no.dados.items() if k not in ("actions", "else", "cases", "default")}
        for rotulo, texto in textos_de(corpo):
            chave = rotulo.rsplit(".", 1)[-1]
            if RE_GUID.search(texto):
                achados.setdefault("GUID", rotulo)
            if RE_SERVIDOR.search(texto):
                achados.setdefault("servidor", rotulo)
            if CHAVES_DEV.search(chave) and RE_DEV.search(texto):
                achados.setdefault("nome dev*", rotulo)
        for tipo, rotulo in achados.items():
            ctx.aviso(no.nome, "F014", tr(f"{tipo} literal em {rotulo}, fora do CONFIG: use variável de ambiente / connection reference / CONFIG", f"literal {tipo} in {rotulo}, outside CONFIG: use an environment variable / connection reference / CONFIG"))


def checar_conectores(ctx: Contexto, acoes: dict, conexoes: dict | None) -> None:
    for no in percorrer(acoes):
        if no.dados.get("type") != "OpenApiConnection":
            continue
        if conexoes is not None and no.nome not in conexoes:
            ctx.erro(no.nome, "F017", tr("ação de conector sem entrada em `allConnectionData` (R1): a colagem não religa a conexão e a execução é bloqueada", "connector action without an entry in `allConnectionData` (R1): pasting does not rebind the connection and the run is blocked"))
        parametros = (no.dados.get("inputs") or {}).get("parameters") or {}
        for chave, valor in parametros.items():
            if isinstance(valor, str) and valor.startswith("@{") and valor.endswith("}") and valor.count("@{") == 1:
                ctx.aviso(no.nome, "F018", tr(f"parâmetro `{chave}` é `@{{expr}}` (força texto); use `@expr` crua, principalmente em coluna numérica (R5)", f"parameter `{chave}` is `@{{expr}}` (forces text); use a bare `@expr`, especially in a numeric column (R5)"))


# -------------------------------------------------------------- por formato

def analisar_acoes(ctx: Contexto, acoes: dict, raiz_nome: str | None, conexoes: dict | None, raiz_externa: str | None = None) -> None:
    tipos_nomes = checar_identidade_e_nomes(ctx, acoes, raiz_nome)
    todos = set(tipos_nomes)
    tipos = {no.nome: no.dados.get("type", "") for no in percorrer(acoes)}
    checar_run_after(ctx, acoes, todos, raiz_externa)
    checar_referencias(ctx, acoes, todos, tipos)
    checar_catch(ctx, acoes)
    checar_respostas(ctx, acoes)
    checar_condicoes(ctx, acoes)
    checar_variaveis(ctx, acoes)
    checar_fazer_ate(ctx, acoes)
    checar_expressoes(ctx, acoes)
    checar_literais_de_ambiente(ctx, acoes)
    checar_conectores(ctx, acoes, conexoes)


def analisar_escopo(ctx: Contexto, dados: dict) -> None:
    faltam = sorted(CHAVES_ESCOPO - set(dados))
    nid = dados.get("nodeId")
    if faltam:
        ctx.erro(str(nid), "F002", tr(f"envelope de escopo sem as chaves {faltam} (o designer não reconhece a colagem)", f"scope envelope without the keys {faltam} (the designer does not recognize the paste)"))
        return
    if dados.get("isScopeNode") is not True or dados.get("mslaNode") is not True:
        ctx.erro(nid, "F002", tr("`isScopeNode` e `mslaNode` precisam ser true no envelope de escopo", "`isScopeNode` and `mslaNode` must be true in the scope envelope"))
    if not isinstance(nid, str) or not nid or " " in nid:
        ctx.erro(str(nid), "F003", tr("nodeId vazio ou com espaço (o designer troca por `_` e os tokens deixam de casar)", "nodeId empty or containing a space (the designer replaces it with `_` and the tokens stop matching)"))
    raiz = dados["serializedValue"]
    if not isinstance(raiz, dict) or "type" not in raiz:
        ctx.erro(str(nid), "F002", tr("`serializedValue` não é uma definição de ação (falta `type`)", "`serializedValue` is not an action definition (missing `type`)"))
        return
    ctx.fragmento = bool(raiz.get("runAfter")) or raiz.get("type") != "Scope"
    ctx.colagem = True
    conexoes = dados["allConnectionData"] if isinstance(dados["allConnectionData"], dict) else {}
    analisar_acoes(ctx, {nid: raiz}, None, conexoes, raiz_externa=nid)


def analisar_folha(ctx: Contexto, dados: dict) -> None:
    nid = dados.get("nodeId")
    faltam = sorted(CHAVES_FOLHA - set(dados))
    if faltam:
        ctx.erro(str(nid), "F002", tr(f"envelope de nó folha sem as chaves {faltam}", f"leaf-node envelope without the keys {faltam}"))
        return
    if dados.get("mslaNode") is not True:
        ctx.erro(nid, "F002", tr("`mslaNode` ausente/falso: o designer novo não reconhece o nó", "`mslaNode` missing/false: the new designer does not recognize the node"))
    if not isinstance(nid, str) or not nid or " " in nid:
        ctx.erro(str(nid), "F003", tr("nodeId vazio ou com espaço", "nodeId empty or containing a space"))
    no_dados = dados.get("nodeData") or {}
    if no_dados.get("id") != nid:
        ctx.erro(str(nid), "F003", tr(f"nodeData.id `{no_dados.get('id')}` difere do nodeId `{nid}`: a colagem renomeia o nó", f"nodeData.id `{no_dados.get('id')}` differs from nodeId `{nid}`: pasting renames the node"))
    for token in (dados.get("nodeTokenData") or {}).get("tokens", []):
        ator = (token.get("outputInfo") or {}).get("actionName")
        if ator != nid:
            ctx.erro(str(nid), "F003", tr(f"token.outputInfo.actionName `{ator}` difere do nodeId `{nid}`: o designer não resolve o token", f"token.outputInfo.actionName `{ator}` differs from nodeId `{nid}`: the designer does not resolve the token"))
    grupos = ((no_dados.get("nodeInputs") or {}).get("parameterGroups") or {})
    guids: dict[str, str] = {}
    for grupo in grupos.values():
        checar_segmentos(ctx, str(nid), grupo, guids)
        for bruto in grupo.get("rawInputs", []):
            valor = bruto.get("value")
            if isinstance(valor, str) and eh_expressao(valor):
                achar_expressoes_longas(ctx, str(nid), bruto.get("key", "rawInputs"), valor)
                checar_coalesce_string(ctx, str(nid), bruto.get("key", "rawInputs"), valor)


def raw_esperado(segmentos: list) -> str:
    """rawInputs[].value reconstruído dos segmentos do editor (1 token: `@expr`; misto: `@{expr}` + texto)."""
    if len(segmentos) == 1 and segmentos[0].get("type") == "token":
        return "@" + str(segmentos[0].get("value", ""))
    return "".join("@{" + str(sg.get("value", "")) + "}" if sg.get("type") == "token" else str(sg.get("value", ""))
                   for sg in segmentos)


def checar_segmentos(ctx: Contexto, nid: str, grupo: dict, guids: dict[str, str]) -> None:
    """F019: GUID repetido, token.value != value, validationErrors (ERRO); rawInputs fora de sincronia (AVISO:
    o designer pode exportar assim e regenera na colagem, mas o que se gera deve sair coerente)."""
    brutos = {b.get("key"): b for b in grupo.get("rawInputs", []) if isinstance(b, dict)}
    for par in grupo.get("parameters", []):
        chave = par.get("parameterKey", "?")
        segmentos = par.get("value") if isinstance(par.get("value"), list) else []
        ids = [(par.get("id"), f"{chave}.id")] + [(sg.get("id"), f"{chave}.segmento{i}") for i, sg in enumerate(segmentos)]
        for guid, onde in ids:
            if guid and guid in guids and guids[guid] != onde:
                ctx.erro(nid, "F019", tr(f"GUID repetido entre {guids[guid]} e {onde}: colisão corrompe o editor", f"GUID repeated between {guids[guid]} and {onde}: the collision corrupts the editor"))
            elif guid:
                guids[guid] = onde
        for i, sg in enumerate(segmentos):
            if sg.get("type") == "token" and (sg.get("token") or {}).get("value") != sg.get("value"):
                ctx.erro(nid, "F019", tr(f"{chave}.segmento{i}: token.value difere de value (a mesma expressão em dois lugares)", f"{chave}.segmento{i}: token.value differs from value (the same expression in two places)"))
        if par.get("validationErrors"):
            ctx.erro(nid, "F019", tr(f"{chave} tem validationErrors: nó copiado com erro propaga o erro", f"{chave} has validationErrors: a node copied with an error propagates the error"))
        bruto = brutos.get(chave)
        if bruto is None:
            ctx.erro(nid, "F019", tr(f"{chave} sem rawInputs correspondente", f"{chave} without a matching rawInputs"))
        elif bruto.get("value") != raw_esperado(segmentos):
            ctx.aviso(nid, "F019", tr(f"{chave}: rawInputs dessincronizado dos segmentos (esperado {raw_esperado(segmentos)!r}, achado {bruto.get('value')!r})", f"{chave}: rawInputs out of sync with the segments (expected {raw_esperado(segmentos)!r}, found {bruto.get('value')!r})"))


def extrair_definicao(dados: Any) -> dict | None:
    if not isinstance(dados, dict):
        return None
    for caminho in (("properties", "definition"), ("definition",), ()):
        no = dados
        for chave in caminho:
            no = no.get(chave) if isinstance(no, dict) else None
        if isinstance(no, dict) and isinstance(no.get("actions"), dict):
            return no
    return None


def analisar_definicao(ctx: Contexto, definicao: dict) -> None:
    gatilhos = definicao.get("triggers") or {}
    ctx.powerapps = any(isinstance(g, dict) and g.get("kind") in ("PowerApp", "PowerAppV2") for g in gatilhos.values())
    analisar_acoes(ctx, definicao["actions"], None, None)


def ler_json(caminho: Path) -> tuple[Any | None, Achado | None]:
    try:
        texto = caminho.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as erro:
        return None, Achado(str(caminho), "1", "ERRO", "F001", tr(f"não consegui ler o arquivo: {erro}", f"could not read the file: {erro}"))
    texto = texto.strip()
    if caminho.suffix.lower() == ".md":
        if texto.startswith("```"):
            texto = "\n".join(l for l in texto.splitlines() if not l.strip().startswith("```")).strip()
        if not texto.startswith("{"):
            return None, None
    try:
        return json.loads(texto), None
    except json.JSONDecodeError as erro:
        return None, Achado(str(caminho), str(erro.lineno), "ERRO", "F001", tr(f"JSON inválido: {erro.msg} (coluna {erro.colno})", f"invalid JSON: {erro.msg} (column {erro.colno})"))


def verificar_arquivo(caminho: Path, rotulo: str, explicito: bool, estrito: bool, nomes_config: tuple[str, ...]) -> tuple[list[Achado], bool]:
    """Devolve (achados, analisado). `analisado` é False para .md que não é JSON."""
    dados, falha = ler_json(caminho)
    if falha:
        return [Achado(rotulo, falha.lugar, falha.nivel, falha.codigo, falha.mensagem)], True
    if dados is None:
        return [], False
    ctx = Contexto(rotulo, estrito=estrito, nomes_config=nomes_config)
    if isinstance(dados, dict) and "nodeId" in dados and "serializedValue" in dados:
        analisar_escopo(ctx, dados)
    elif isinstance(dados, dict) and "nodeId" in dados and ("nodeData" in dados or "isScopeNode" in dados):
        analisar_folha(ctx, dados)
    elif isinstance(dados, dict) and "nodeId" in dados:
        ctx.erro(str(dados["nodeId"]), "F002", tr("envelope com `nodeId` mas sem `serializedValue` nem `nodeData`", "envelope with `nodeId` but without `serializedValue` or `nodeData`"))
    elif (definicao := extrair_definicao(dados)) is not None:
        analisar_definicao(ctx, definicao)
    else:
        emitir = ctx.erro if explicito else ctx.aviso
        emitir("1", "F002", tr("formato não reconhecido (nem envelope de clipboard nem `definition` de flow)", "format not recognized (neither a clipboard envelope nor a flow `definition`)"))
    return agrupar(ctx.achados), True


def agrupar(achados: list[Achado]) -> list[Achado]:
    """Achados idênticos viram um só, com `(xN)` no fim."""
    contagem: dict[Achado, int] = {}
    for a in achados:
        contagem[a] = contagem.get(a, 0) + 1
    return [Achado(a.caminho, a.lugar, a.nivel, a.codigo, a.mensagem + (f" (x{n})" if n > 1 else ""))
            for a, n in contagem.items()]


# ------------------------------------------------------------------ config

def achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / NOME_CONFIG
        if candidato.is_file():
            return candidato
    return None


def glob_para_regex(padrao: str) -> re.Pattern:
    saida, i = [], 0
    while i < len(padrao):
        if padrao.startswith("**/", i):
            saida.append("(?:.*/)?")
            i += 3
        elif padrao.startswith("**", i):
            saida.append(".*")
            i += 2
        elif padrao[i] == "*":
            saida.append("[^/]*")
            i += 1
        elif padrao[i] == "?":
            saida.append("[^/]")
            i += 1
        else:
            saida.append(re.escape(padrao[i]))
            i += 1
    return re.compile("^" + "".join(saida) + "$")


def descobrir(alvos: list[Path], base: Path, ignorar: list[re.Pattern]) -> list[tuple[Path, bool]]:
    saida: list[tuple[Path, bool]] = []
    for alvo in alvos:
        if alvo.is_file():
            saida.append((alvo, True))
            continue
        for p in sorted(alvo.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in (".json", ".md"):
                continue
            if any(parte in ("__pycache__", ".git", "node_modules") for parte in p.parts):
                continue
            try:
                rel = p.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                rel = p.as_posix()
            if any(r.match(rel) for r in ignorar):
                continue
            saida.append((p, False))
    return saida


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=tr("Verifica flows do Power Automate (clipboard do designer ou definition exportada). Só lê.",
                       "Checks Power Automate flows (designer clipboard or exported definition). Read-only."),
        epilog=tr("Códigos: F001 JSON, F002 envelope, F003 identidade do nó, F004 nome duplicado, F005 runAfter, "
                  "F006 referência a ação, F007 items(), F008 caso de Switch, F009 Catch sem Skipped, F010 Response sem os 4 campos, "
                  "F011 outputs() de Select/Query, F012 coalesce(string()), F013 tamanho de expressão, F014 literal de ambiente, "
                  "F015 Response sem Terminate, F016 condição constante, F017 conexão ausente, F018 @{} em parâmetro de conector, F019 segmentos/rawInputs de nó folha, "
                  "F020 condição de If em texto ou sem and/or, F021 Inicializar variável fora da raiz, "
                  "F022 variável sozinha num campo colado, F023 Fazer até em texto colado.",
                  "Codes: F001 JSON, F002 envelope, F003 node identity, F004 duplicate name, F005 runAfter, "
                  "F006 action reference, F007 items(), F008 Switch case, F009 Catch without Skipped, F010 Response without the 4 fields, "
                  "F011 outputs() of Select/Query, F012 coalesce(string()), F013 expression length, F014 environment literal, "
                  "F015 Response without Terminate, F016 constant condition, F017 missing connection, F018 @{} in connector parameter, F019 leaf-node segments/rawInputs, "
                  "F020 If condition as text or without and/or, F021 Initialize variable outside the root, "
                  "F022 lone variable in a pasted field, F023 Do until as pasted text."))
    ap.add_argument("caminhos", nargs="*", type=Path, help=tr("arquivos ou pastas (default: pastas.flows da config)", "files or folders (default: pastas.flows from the config)"))
    ap.add_argument("--config", type=Path, help=tr(f"caminho do {NOME_CONFIG}", f"path of {NOME_CONFIG}"))
    ap.add_argument("--estrito", action="store_true", help=tr("F012 também para coalesce(string(x), '')", "F012 also for coalesce(string(x), '')"))
    args = ap.parse_args(argv)

    if args.config:
        if not args.config.is_file():
            print(tr(f"config inexistente: {args.config}", f"config not found: {args.config}"), file=sys.stderr)
            return 2
        config_path: Path | None = args.config
    else:
        config_path = achar_config(Path.cwd())
    config: dict = {}
    if config_path:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as erro:
            print(tr(f"config inválida ({config_path}): {erro}", f"invalid config ({config_path}): {erro}"), file=sys.stderr)
            return 2
        print(f"# config: {config_path.name}")
    else:
        print(tr("# config: nenhuma encontrada -- defaults genéricos", "# config: none found -- generic defaults"))
    base = config_path.parent if config_path else Path.cwd()
    ignorar = [glob_para_regex(g) for g in config.get("ignorar", [])]

    alvos = args.caminhos
    if not alvos:
        alvos = [base / p for p in (config.get("pastas") or {}).get("flows", ["."])]
    inexistentes = [a for a in alvos if not a.exists()]
    if inexistentes:
        print(tr(f"caminho inexistente: {inexistentes[0]}", f"path not found: {inexistentes[0]}"), file=sys.stderr)
        return 2

    arquivos = descobrir(alvos, base, ignorar)
    achados: list[Achado] = []
    analisados = ignorados = 0
    for caminho, explicito in arquivos:
        try:
            rotulo = caminho.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            rotulo = caminho.as_posix()
        encontrados, analisado = verificar_arquivo(caminho, rotulo, explicito, args.estrito, NOMES_CONFIG_PADRAO)
        achados += encontrados
        analisados += analisado
        ignorados += not analisado
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(tr(f"# {analisados} arquivo(s) analisado(s), {ignorados} ignorado(s) (.md sem JSON)", f"# {analisados} file(s) analyzed, {ignorados} ignored (.md without JSON)"))
    print(tr(f"{erros} erro(s), {len(achados) - erros} aviso(s)", f"{erros} error(s), {len(achados) - erros} warning(s)"))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
