#!/usr/bin/env python3
"""Valida telas Power Apps Canvas em YAML (.pa.yaml) antes de colar no Studio.

Substitui `validar-yaml.py` (só lia blocos cercados) e `verificar-telas.py` (preso a um
projeto). Só lê arquivos; nunca escreve.

Uso:
    python validar-telas.py                      # pastas.telas do power-platform.config.json
    python validar-telas.py Frontend/ tela.md    # pastas e/ou arquivos
    python validar-telas.py --codigos            # lista os códigos de achado

Formato (config `telas_formato` ou `--formato`):
    auto             .md com blocos ```yaml cercados valida cada bloco; .md sem nenhuma cerca
                     é lido inteiro como YAML (YAML puro em .md); .md só com cercas de outras
                     linguagens é documentação (1 aviso T020).
    yaml-puro        todo arquivo é lido inteiro como YAML.
    markdown-cercado só blocos ```yaml cercados.
Bloco com a linha `# validador: ignorar` é pulado (anti-exemplo didático).

Saída: `caminho:linha: ERRO|AVISO CÓDIGO mensagem` e, no fim, `N erro(s), M aviso(s)`.
Exit: 0 sem erro, 1 com erro, 2 uso incorreto.

Unidade de colagem (escopo da regra T006, nome duplicado): todos os arquivos de YAML puro
formam um só app; cada bloco cercado é uma colagem à parte.
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

try:
    import yaml
except ImportError:  # pragma: no cover
    print(tr("Requer PyYAML: pip install pyyaml", "Requires PyYAML: pip install pyyaml"), file=sys.stderr)
    sys.exit(2)

CONFIG_NOME = "power-platform.config.json"
EXTENSOES = {".md", ".yaml", ".yml"}
PASTAS_IGNORADAS = {"__pycache__", "node_modules"}
CHAVES_TOPO = {"App", "Screens", "ComponentDefinitions", "DataSources", "EditorState"}
MARCA_IGNORAR = "validador: ignorar"
TAG_NULO = "tag:yaml.org,2002:null"
NULOS = {"", "null", "~", "Null", "NULL"}

CODIGOS = {
    "T001": tr(
        "YAML não parseia (linha do erro)",
        "YAML does not parse (line of the error)"),
    "T002": tr(
        "propriedade sem `=` no início (schema exige ^=.*)",
        "property without a leading `=` (schema requires ^=.*)"),
    "T003": tr(
        "controle sem `Control:`",
        "control without `Control:`"),
    "T004": tr(
        "`Control:` sem `@versão` (ou fora do formato Tipo@x.y.z)",
        "`Control:` without `@version` (or not in the Type@x.y.z format)"),
    "T005": tr(
        "`Control`/`Variant` com fórmula Power Fx",
        "`Control`/`Variant` with a Power Fx formula"),
    "T006": tr(
        "nome de controle duplicado no conjunto validado",
        "duplicate control name in the validated set"),
    "T007": tr(
        "`;;` dentro de fórmula no YAML (dialeto da barra de fórmulas)",
        "`;;` inside a formula in the YAML (pt-BR formula-bar dialect)"),
    "T008": tr(
        "propriedade recusada pelo Studio (PA2108) naquele tipo de controle",
        "property rejected by Studio (PA2108) on that control type"),
    "T009": tr(
        "`RGBA(` literal (use token fx*)",
        "literal `RGBA(` (use an fx* token)"),
    "T010": tr(
        "nome de controle fora de kebab-case",
        "control name not in kebab-case"),
    "T011": tr(
        "`Search(`/`in` dentro de `Filter(` sobre fonte que não é coleção col*",
        "`Search(`/`in` inside `Filter(` over a source that is not a col* collection"),
    "T012": tr(
        "chave duplicada no mesmo mapa",
        "duplicate key in the same map"),
    "T013": tr(
        "`CountRows`/`CountIf` sobre fonte SQL (não delega; só com trilha sql-server)",
        "`CountRows`/`CountIf` over a SQL source (does not delegate; only on the sql-server track)"),
    "T014": tr(
        "coluna de DisplayFields/SearchFields/SortByColumns sem prefixo (só dataverse)",
        "column in DisplayFields/SearchFields/SortByColumns without a prefix (dataverse only)"),
    "T015": tr(
        "` #` depois de fórmula de uma linha (vira comentário YAML e trunca)",
        "` #` after a one-line formula (becomes a YAML comment and truncates)"),
    "T016": tr(
        "ordem de `Children` da tela: conteúdo, modais, loading, toast (toast por último)",
        "screen `Children` order: content, modals, loading, toast (toast last)"),
    "T017": tr(
        "estrutura inválida (Properties/Children com formato errado)",
        "invalid structure (Properties/Children with the wrong shape)"),
    "T018": tr(
        "`.Run(` sem `IfError(` na mesma fórmula",
        "`.Run(` without `IfError(` in the same formula"),
    "T020": tr(
        "arquivo ou bloco que não é tela YAML — ignorado",
        "file or block that is not a YAML screen — ignored"),
    "T022": tr(
        "chave de topo fora do schema (App, Screens, ComponentDefinitions, ...)",
        "top-level key outside the schema (App, Screens, ComponentDefinitions, ...)"),
}

CONTROL_RE = re.compile(r"^([A-Z][a-zA-Z0-9]*/)?[A-Z][a-zA-Z0-9]*(@\d+\.\d+\.\d+)?$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AUTO_RE = re.compile(r"^[A-Z][A-Za-z]*\d+(_\d+)?$")
COLECAO_RE = re.compile(r"^col[A-Za-z0-9_]*$")
PARECE_TELA_RE = re.compile(r"^(Screens|ComponentDefinitions|App):\s*$|^\s*(-\s+)?Control:\s", re.M)
CERCA_RE = re.compile(r"^\s{0,3}```\s*([A-Za-z0-9_.+-]*)\s*$")
COLUNAS_LIVRES = {"Value", "DisplayName", "Mail", "UserPrincipalName", "Id", "Name"}

RADIUS = {"RadiusTopLeft", "RadiusTopRight", "RadiusBottomLeft", "RadiusBottomRight"}
# [verificado: projeto de referência] — ver references/propriedades-inexistentes.md
RECUSADAS = {
    "Classic/Button@2.2.0": {"AccessibleLabel"},
    "Button@0.0.45": {"AccessibleLabel"},
    "Label@2.5.1": {"Live"},
    "Classic/ComboBox@2.4.0": {"Size"} | RADIUS,
    "Classic/DatePicker@2.6.0": {"Size"} | RADIUS,
    "Rectangle@2.3.0": set(RADIUS),
    "NumberInput@2.9.12": set(RADIUS),
    "ModernTextInput@1.1.1": set(RADIUS),
    "TextInput@0.0.54": set(RADIUS),
}
RECUSADA_EM_TODOS = {"FocusedBorderThickness"}
VERSOES_ATESTADAS = {
    "Label@2.5.1", "Classic/Button@2.2.0", "Image@2.2.3", "GroupContainer@1.5.0", "Button@0.0.45",
    "Classic/TextInput@2.3.2", "Classic/ComboBox@2.4.0", "Rectangle@2.3.0", "Text@0.0.51",
    "Gallery@2.15.0", "HtmlViewer@2.1.0", "Timer@2.1.0", "Classic/CheckBox@2.1.0",
    "Classic/DatePicker@2.6.0", "Spinner@1.4.6", "Classic/Icon@2.5.0", "CheckBox@0.0.30",
    "NumberInput@2.9.12", "ModernTextInput@1.1.1", "Classic/Toggle@2.1.0", "TextInput@0.0.54",
}


def NAO_E_TELA() -> str:
    return tr("não é tela YAML — ignorado", "not a YAML screen — ignored")


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
class Config:
    raiz: Path
    origem: Path | None = None
    projeto: str = ""
    trilha: str | None = None
    prefixo: str = ""
    pastas_telas: tuple[str, ...] = (".",)
    formato: str = "auto"
    ignorar: tuple[str, ...] = ()


@dataclass
class Unidade:
    caminho: str
    texto: str
    linha_base: int
    escopo: str
    bloco: bool


# ---------------------------------------------------------------- configuração

def _achar_config(inicio: Path) -> Path | None:
    for pasta in [inicio, *inicio.parents]:
        candidato = pasta / CONFIG_NOME
        if candidato.is_file():
            return candidato
    return None


def carregar_config(explicito: Path | None, inicio: Path) -> Config:
    arquivo = explicito or _achar_config(inicio)
    if arquivo is None:
        return Config(raiz=inicio)
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    pastas = dados.get("pastas", {}) or {}
    return Config(
        raiz=arquivo.resolve().parent,
        origem=arquivo,
        projeto=str(dados.get("projeto", "")),
        trilha=dados.get("trilha_dados"),
        prefixo=str(dados.get("prefixo_publisher", "")),
        pastas_telas=tuple(pastas.get("telas") or ["."]),
        formato=str(dados.get("telas_formato", "auto")),
        ignorar=tuple(dados.get("ignorar") or ()),
    )


def glob_para_regex(padrao: str) -> re.Pattern:
    saida, i = "", 0
    while i < len(padrao):
        if padrao.startswith("**/", i):
            saida += "(?:.*/)?"
            i += 3
        elif padrao.startswith("**", i):
            saida += ".*"
            i += 2
        elif padrao[i] == "*":
            saida += "[^/]*"
            i += 1
        elif padrao[i] == "?":
            saida += "[^/]"
            i += 1
        else:
            saida += re.escape(padrao[i])
            i += 1
    return re.compile(saida + "$")


def esta_ignorado(caminho: Path, cfg: Config) -> bool:
    try:
        rel = caminho.resolve().relative_to(cfg.raiz.resolve()).as_posix()
    except ValueError:
        rel = caminho.as_posix()
    return any(glob_para_regex(p).match(rel) for p in cfg.ignorar)


def descobrir_arquivos(alvos: list[Path], cfg: Config) -> list[Path]:
    achados: list[Path] = []
    for alvo in alvos:
        if alvo.is_file():
            achados.append(alvo)
            continue
        for arq in sorted(alvo.rglob("*")):
            partes = arq.relative_to(alvo).parts[:-1]
            oculto = any(p.startswith(".") or p in PASTAS_IGNORADAS for p in partes)
            if arq.is_file() and arq.suffix.lower() in EXTENSOES and not oculto \
                    and not esta_ignorado(arq, cfg):
                achados.append(arq)
    return achados


# ------------------------------------------------------------------- fórmulas

def limpar(formula: str) -> str:
    """Esvazia o conteúdo de textos entre aspas e remove comentários // e /* */."""
    saida, i, n = [], 0, len(formula)
    while i < n:
        if formula[i] == '"':
            j = i + 1
            while j < n:
                if formula[j] == '"':
                    if j + 1 < n and formula[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            saida.append('"' + " " * max(j - i - 1, 0) + '"')
            i = j + 1
        elif formula.startswith("//", i):
            fim = formula.find("\n", i)
            i = n if fim < 0 else fim
        elif formula.startswith("/*", i):
            fim = formula.find("*/", i + 2)
            i = n if fim < 0 else fim + 2
        else:
            saida.append(formula[i])
            i += 1
    return "".join(saida)


def ler_args(texto: str, inicio: int) -> list[str]:
    """Argumentos de primeiro nível da chamada cujo `(` termina em `inicio - 1`."""
    args, atual, prof = [], [], 1
    for c in texto[inicio:]:
        if c in "([{":
            prof += 1
        elif c in ")]}":
            prof -= 1
            if prof == 0:
                break
        if prof == 1 and c in ",;":
            args.append("".join(atual).strip())
            atual = []
        else:
            atual.append(c)
    args.append("".join(atual).strip())
    return args


def chamadas(formula: str, nome: str):
    padrao = re.compile(r"(?<![\w'.])" + nome + r"\s*\(")
    for m in padrao.finditer(formula):
        yield m, ler_args(formula, m.end())


def _fonte_raiz(arg: str) -> str:
    envoltorios = ("Filter", "Sort", "SortByColumns", "FirstN", "Search", "ShowColumns", "AddColumns")
    while True:
        m = re.match(r"^(" + "|".join(envoltorios) + r")\s*\(", arg)
        if not m:
            return arg.strip()
        arg = ler_args(arg, m.end())[0]


def achados_delegacao(f: str) -> list[tuple[str, str, str]]:
    saida = []
    for m, args in chamadas(f, "Filter"):
        if COLECAO_RE.match(_fonte_raiz(args[0])):
            continue
        interno = ";".join(args)
        if re.search(r"(?<![\w'.])Search\s*\(", interno) or re.search(r"\sin\s", " " + interno + " "):
            saida.append(("T011", "AVISO", tr(
                "`Search(`/`in` dentro de `Filter(` sobre fonte que não é "
                "coleção: confira a tabela de delegação do conector (references/delegacao.md)",
                "`Search(`/`in` inside `Filter(` over a source that is not a "
                "collection: check the connector's delegation table (references/delegation.md)")))
            break
    return saida


def achados_contagem(f: str, trilha: str | None) -> list[tuple[str, str, str]]:
    if trilha != "sql-server":
        return []
    for funcao in ("CountRows", "CountIf"):
        for _, args in chamadas(f, funcao):
            raiz = _fonte_raiz(args[0])
            if raiz and not COLECAO_RE.match(raiz) and ".AllItems" not in raiz:
                return [("T013", "AVISO", tr(
                    f"`{funcao}` não delega no conector SQL: mostre teto "
                    "(`2.000+`) ou conte no servidor (references/delegacao.md)",
                    f"`{funcao}` does not delegate on the SQL connector: show a ceiling "
                    "(`2,000+`) or count on the server (references/delegation.md)"))]
    return []


def achados_colunas(bruta: str, chave: str, cfg: Config) -> list[tuple[str, str, str]]:
    if cfg.trilha != "dataverse" or not cfg.prefixo:
        return []
    nomes: list[str] = []
    if chave in ("DisplayFields", "SearchFields"):
        nomes += re.findall(r'"([^"]*)"', bruta)
    for _, args in chamadas(bruta, "SortByColumns"):
        nomes += [a[1:-1] for a in args[1:] if re.fullmatch(r'"[^"]*"', a)]
    suspeitos = [n for n in nomes if n not in COLUNAS_LIVRES and not n.startswith(cfg.prefixo)]
    if not suspeitos:
        return []
    return [("T014", "AVISO", tr(
        f"coluna \"{suspeitos[0]}\" sem o prefixo `{cfg.prefixo}`: coluna errada "
        "não dá erro, só falha calada — confira no NOMES-AS-BUILT",
        f"column \"{suspeitos[0]}\" without the `{cfg.prefixo}` prefix: a wrong column "
        "raises no error, it just fails silently — check AS-BUILT-NAMES"))]


def regras_formula(bruta: str, chave: str, cfg: Config) -> list[tuple[str, str, str]]:
    f = limpar(bruta)
    saida: list[tuple[str, str, str]] = []
    if ";;" in f:
        saida.append(("T007", "ERRO", tr(
            "`;;` é encadeamento da barra de fórmulas pt-BR; no YAML "
            "colado use `;` (e `,` entre argumentos)",
            "`;;` is chaining from the pt-BR formula bar; in the pasted YAML "
            "use `;` (and `,` between arguments)")))
    if re.search(r"(?<![\w.'])RGBA\s*\(", f):
        saida.append(("T009", "AVISO", tr(
            "`RGBA(` literal: use token fx* (fxColorTransparent para 0,0,0,0)",
            "literal `RGBA(`: use an fx* token (fxColorTransparent for 0,0,0,0)")))
    saida += achados_delegacao(f)
    saida += achados_contagem(f, cfg.trilha)
    if re.search(r"\.Run\s*\(", f) and not re.search(r"(?<![\w'.])IfError\s*\(", f):
        saida.append(("T018", "AVISO", tr(
            "`.Run(` fora de `IfError(`: falha de transporte fica sem "
            "tratamento (references/chamada-flow.md)",
            "`.Run(` outside `IfError(`: a transport failure goes unhandled "
            "(references/flow-call.md)")))
    saida += achados_colunas(bruta, chave, cfg)
    return saida


# ----------------------------------------------------------------- estrutura

class Verificador:
    def __init__(self, unidade: Unidade, cfg: Config, registro: dict[str, dict[str, str]]):
        self.u = unidade
        self.cfg = cfg
        self.registro = registro.setdefault(unidade.escopo, {})
        self.linhas = unidade.texto.splitlines()
        self.achados: list[Achado] = []

    def _add(self, no, nivel: str, codigo: str, msg: str) -> None:
        linha = self.u.linha_base + no.start_mark.line
        self.achados.append(Achado(self.u.caminho, linha, nivel, codigo, msg))

    def mapa(self, no, onde: str) -> list[tuple[str, object, object]] | None:
        if not isinstance(no, yaml.MappingNode):
            self._add(no, "ERRO", "T017", tr(f"{onde} deveria ser um mapa", f"{onde} should be a map"))
            return None
        vistos: dict[str, bool] = {}
        itens = []
        for k, v in no.value:
            if k.value in vistos:
                self._add(k, "ERRO", "T012", tr(
                    f"chave duplicada `{k.value}` em {onde} (o Studio recusa)",
                    f"duplicate key `{k.value}` in {onde} (Studio rejects it)"))
            vistos[k.value] = True
            itens.append((k.value, k, v))
        return itens

    def propriedades(self, no, tipo: str | None, nome: str) -> None:
        itens = self.mapa(no, tr(f"Properties de `{nome}`", f"Properties of `{nome}`"))
        for chave, k, v in itens or []:
            self._recusada(k, chave, tipo, nome)
            if not isinstance(v, yaml.ScalarNode):
                self._add(v, "ERRO", "T017", tr(
                    f"`{nome}`.{chave}: valor precisa ser fórmula (texto com `=`)",
                    f"`{nome}`.{chave}: value must be a formula (text starting with `=`)"))
                continue
            if v.tag == TAG_NULO and v.value in NULOS:
                continue
            if not v.value.startswith("="):
                self._add(v, "ERRO", "T002", tr(
                    f"`{nome}`.{chave} não começa com `=`",
                    f"`{nome}`.{chave} does not start with `=`"))
                continue
            self._hash(v, nome, chave)
            for codigo, nivel, msg in regras_formula(v.value, chave, self.cfg):
                self._add(v, nivel, codigo, f"`{nome}`.{chave}: {msg}")

    def _recusada(self, k, prop: str, tipo: str | None, nome: str) -> None:
        if tipo is None:
            return
        base = tipo.split("@")[0]
        exata = RECUSADAS.get(tipo, set())
        if prop in exata or (prop in RECUSADA_EM_TODOS and tipo in VERSOES_ATESTADAS):
            self._add(k, "ERRO", "T008", tr(
                f"`{nome}` ({tipo}) usa `{prop}`, que o Studio recusa nesse "
                "controle (PA2108 derruba o bloco inteiro)",
                f"`{nome}` ({tipo}) uses `{prop}`, which Studio rejects on this "
                "control (PA2108 breaks the whole block)"))
        elif prop in RECUSADA_EM_TODOS or any(
                prop in props for t, props in RECUSADAS.items() if t.split("@")[0] == base):
            self._add(k, "AVISO", "T008", tr(
                f"`{nome}` ({tipo}) usa `{prop}`, recusada em outra versão "
                "deste controle: confirme no Studio antes de colar",
                f"`{nome}` ({tipo}) uses `{prop}`, rejected in another version "
                "of this control: confirm in Studio before pasting"))

    def _hash(self, v, nome: str, chave: str) -> None:
        if v.style is not None or v.start_mark.line != v.end_mark.line:
            return
        linha = self.linhas[v.end_mark.line] if v.end_mark.line < len(self.linhas) else ""
        if linha[v.end_mark.column:].lstrip().startswith("#"):
            self._add(v, "AVISO", "T015", tr(
                f"`{nome}`.{chave}: ` #` após a fórmula é comentário YAML e "
                "não é preservado; use `//` dentro de bloco `|-`",
                f"`{nome}`.{chave}: ` #` after the formula is a YAML comment and "
                "is not preserved; use `//` inside a `|-` block"))

    def controle(self, nome: str, k, no) -> None:
        if not KEBAB_RE.match(nome):
            auto = tr(" (nome automático do Studio)", " (Studio automatic name)") if AUTO_RE.match(nome) else ""
            self._add(k, "AVISO", "T010", tr(
                f"nome `{nome}` fora de kebab-case{auto}",
                f"name `{nome}` not in kebab-case{auto}"))
        if nome in self.registro:
            self._add(k, "ERRO", "T006", tr(
                f"nome de controle duplicado `{nome}` "
                f"(primeira ocorrência em {self.registro[nome]})",
                f"duplicate control name `{nome}` "
                f"(first occurrence at {self.registro[nome]})"))
        else:
            self.registro[nome] = f"{self.u.caminho}:{self.u.linha_base + k.start_mark.line}"
        itens = self.mapa(no, tr(f"controle `{nome}`", f"control `{nome}`"))
        if itens is None:
            return
        campos = {c: (kk, vv) for c, kk, vv in itens}
        tipo = self._tipo(nome, k, campos)
        if "Properties" in campos:
            self.propriedades(campos["Properties"][1], tipo, nome)
        if "Children" in campos:
            self.filhos(campos["Children"][1], nome)

    def _tipo(self, nome: str, k, campos: dict) -> str | None:
        if "Control" not in campos:
            self._add(k, "ERRO", "T003", tr(
                f"controle `{nome}` sem `Control:`", f"control `{nome}` without `Control:`"))
            return None
        no = campos["Control"][1]
        valor = no.value if isinstance(no, yaml.ScalarNode) else ""
        if valor.startswith("="):
            self._add(no, "ERRO", "T005", tr(
                f"`{nome}`: `Control` não aceita fórmula", f"`{nome}`: `Control` does not accept a formula"))
            return None
        if "Variant" in campos and getattr(campos["Variant"][1], "value", "").startswith("="):
            self._add(campos["Variant"][1], "ERRO", "T005", tr(
                f"`{nome}`: `Variant` não aceita fórmula", f"`{nome}`: `Variant` does not accept a formula"))
        if "ComponentName" not in campos and ("@" not in valor or not CONTROL_RE.match(valor)):
            self._add(no, "ERRO", "T004", tr(
                f"`{nome}`: `Control: {valor}` precisa de `Tipo@x.y.z` "
                "(use a versão já usada no app)",
                f"`{nome}`: `Control: {valor}` needs `Type@x.y.z` "
                "(use the version already used in the app)"))
        return valor

    def filhos(self, no, pai: str) -> None:
        if not isinstance(no, yaml.SequenceNode):
            self._add(no, "ERRO", "T017", tr(
                f"Children de `{pai}` deveria ser lista", f"Children of `{pai}` should be a list"))
            return
        for item in no.value:
            if not isinstance(item, yaml.MappingNode) or len(item.value) != 1:
                self._add(item, "ERRO", "T017", tr(
                    f"item de Children de `{pai}` precisa ter 1 chave (o nome)",
                    f"Children item of `{pai}` must have 1 key (the name)"))
                continue
            k, v = item.value[0]
            self.controle(k.value, k, v)

    def ordem_tela(self, no, tela: str) -> None:
        if not isinstance(no, yaml.SequenceNode):
            return
        nomes = [(i.value[0][0].value, i) for i in no.value
                 if isinstance(i, yaml.MappingNode) and len(i.value) == 1]
        toasts = [i for i, (n, _) in enumerate(nomes) if "toast" in n]
        if not toasts:
            return
        if toasts[-1] != len(nomes) - 1:
            self._add(nomes[toasts[-1]][1], "AVISO", "T016", tr(
                f"tela `{tela}`: o toast deve ser o último "
                "de Children (conteúdo, modais, loading, toast)",
                f"screen `{tela}`: the toast must be the last "
                "of Children (content, modals, loading, toast)"))
            return
        primeiro = toasts[0]
        for n, item in nomes[primeiro + 1:]:
            if "-mod-" in n or "loading" in n:
                self._add(item, "AVISO", "T016", tr(
                    f"tela `{tela}`: `{n}` está depois do toast",
                    f"screen `{tela}`: `{n}` comes after the toast"))


def classificar(raiz) -> str:
    if isinstance(raiz, yaml.SequenceNode):
        ok = raiz.value and all(isinstance(i, yaml.MappingNode) and len(i.value) == 1
                                and isinstance(i.value[0][1], yaml.MappingNode) for i in raiz.value)
        return "fragmento" if ok else "outro"
    if not isinstance(raiz, yaml.MappingNode) or not raiz.value:
        return "outro"
    chaves = {k.value for k, _ in raiz.value}
    if chaves & {"Screens", "ComponentDefinitions", "App"}:
        return "tela"
    valores = [v for _, v in raiz.value]
    if all(isinstance(v, yaml.MappingNode) and any(k.value == "Control" for k, _ in v.value) for v in valores):
        return "controles"
    if all(isinstance(v, yaml.ScalarNode) for v in valores) and any(
            v.value.startswith("=") for v in valores):
        return "propriedades"
    return "outro"


def verificar_tela(vf: Verificador, raiz) -> None:
    for k, v in raiz.value:
        if k.value not in CHAVES_TOPO:
            vf._add(k, "ERRO", "T022", tr(
                f"chave de topo `{k.value}` fora do schema "
                f"({', '.join(sorted(CHAVES_TOPO))})",
                f"top-level key `{k.value}` outside the schema "
                f"({', '.join(sorted(CHAVES_TOPO))})"))
            continue
        itens = vf.mapa(v, k.value) if k.value != "EditorState" and k.value != "DataSources" else None
        if k.value == "App":
            _propriedades_de(vf, v, "App")
        for nome, kk, vv in itens or []:
            if k.value == "Screens":
                _tela(vf, nome, vv)
            elif k.value == "ComponentDefinitions":
                _componente(vf, nome, vv)


def _propriedades_de(vf: Verificador, no, nome: str) -> None:
    itens = vf.mapa(no, nome)
    for chave, _, v in itens or []:
        if chave == "Properties":
            vf.propriedades(v, None, nome)


def _tela(vf: Verificador, nome: str, no) -> None:
    itens = vf.mapa(no, f"tela `{nome}`")
    for chave, _, v in itens or []:
        if chave == "Properties":
            vf.propriedades(v, None, nome)
        elif chave == "Children":
            vf.filhos(v, nome)
            vf.ordem_tela(v, nome)


def _componente(vf: Verificador, nome: str, no) -> None:
    itens = vf.mapa(no, f"componente `{nome}`")
    for chave, _, v in itens or []:
        if chave == "Properties":
            vf.propriedades(v, None, nome)
        elif chave == "Children":
            vf.filhos(v, nome)


def validar_unidade(u: Unidade, cfg: Config, registro: dict) -> list[Achado]:
    if MARCA_IGNORAR in u.texto:
        return []
    try:
        raiz = yaml.compose(u.texto, Loader=yaml.SafeLoader)
    except yaml.YAMLError as erro:
        marca = getattr(erro, "problem_mark", None)
        linha = u.linha_base + (marca.line if marca else 0)
        if not u.bloco and not PARECE_TELA_RE.search(u.texto):
            return [Achado(u.caminho, 1, "AVISO", "T020", NAO_E_TELA())]
        return [Achado(u.caminho, linha, "ERRO", "T001",
                       tr(f"YAML inválido: {getattr(erro, 'problem', erro)}",
                          f"Invalid YAML: {getattr(erro, 'problem', erro)}"))]
    tipo = classificar(raiz) if raiz is not None else "outro"
    if tipo == "outro":
        if u.bloco:
            return []
        return [Achado(u.caminho, 1, "AVISO", "T020", NAO_E_TELA())]
    vf = Verificador(u, cfg, registro)
    if tipo == "tela":
        verificar_tela(vf, raiz)
    elif tipo == "fragmento":
        vf.filhos(raiz, "(fragmento)")
    elif tipo == "controles":
        for k, v in raiz.value:
            vf.controle(k.value, k, v)
    else:
        vf.propriedades(raiz, None, "(snippet)")
    return vf.achados


# -------------------------------------------------------------------- arquivos

def extrair_blocos(texto: str) -> tuple[list[tuple[int, str]], bool]:
    """Devolve ([(linha_do_primeiro_conteudo, texto)] dos blocos yaml, houve_cerca)."""
    blocos, abertos, houve = [], None, False
    for numero, linha in enumerate(texto.splitlines(), start=1):
        m = CERCA_RE.match(linha)
        if not m:
            if abertos is not None:
                abertos[2].append(linha)
            continue
        houve = True
        if abertos is None:
            abertos = (m.group(1).lower(), numero + 1, [])
        else:
            lang, inicio, corpo = abertos
            if lang in ("yaml", "yml"):
                blocos.append((inicio, "\n".join(corpo) + "\n"))
            abertos = None
    return blocos, houve


def unidades_do_arquivo(caminho: Path, nome: str, cfg: Config, formato: str) -> list[Unidade]:
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    inteiro = Unidade(nome, texto, 1, "(app)", False)
    if caminho.suffix.lower() != ".md" or formato == "yaml-puro":
        return [inteiro]
    blocos, houve = extrair_blocos(texto)
    if blocos:
        return [Unidade(nome, t, ini, f"{nome}:{ini}", True) for ini, t in blocos]
    if houve or formato == "markdown-cercado":
        return [Unidade(nome, "", 1, "(doc)", False)]
    return [inteiro]


def validar_arquivos(arquivos: list[Path], cfg: Config, formato: str, base: Path) -> list[Achado]:
    registro: dict = {}
    achados: list[Achado] = []
    for caminho in arquivos:
        try:
            nome = caminho.resolve().relative_to(base.resolve()).as_posix()
        except ValueError:
            nome = caminho.as_posix()
        for u in unidades_do_arquivo(caminho, nome, cfg, formato):
            if not u.texto:
                achados.append(Achado(nome, 1, "AVISO", "T020", NAO_E_TELA()))
                continue
            achados += validar_unidade(u, cfg, registro)
    return sorted(achados, key=lambda a: (a.caminho, a.linha, a.codigo))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=tr(
        "Valida telas Power Apps Canvas em YAML (.pa.yaml).",
        "Validates Power Apps Canvas screens in YAML (.pa.yaml)."))
    ap.add_argument("alvos", nargs="*", type=Path, help=tr("arquivos e/ou pastas (default: pastas.telas)",
                                                         "files and/or folders (default: pastas.telas)"))
    ap.add_argument("--config", type=Path, help=tr(
        f"{CONFIG_NOME} (default: procura do diretório atual para cima)",
        f"{CONFIG_NOME} (default: searches from the current directory upward)"))
    ap.add_argument("--formato", choices=["auto", "yaml-puro", "markdown-cercado"],
                    help=tr("sobrepõe telas_formato do config", "overrides telas_formato from the config"))
    ap.add_argument("--trilha", choices=["sql-server", "dataverse"], help=tr("sobrepõe trilha_dados do config",
                                                                                "overrides trilha_dados from the config"))
    ap.add_argument("--codigos", action="store_true", help=tr(
        "lista os códigos de achado e sai", "lists the finding codes and exits"))
    args = ap.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    if args.codigos:
        for codigo, texto in CODIGOS.items():
            print(f"{codigo}  {texto}")
        return 0
    try:
        cfg = carregar_config(args.config, Path.cwd())
    except (OSError, ValueError) as erro:
        print(tr(f"config inválida: {erro}", f"invalid config: {erro}"), file=sys.stderr)
        return 2
    if args.trilha:
        cfg = Config(**{**cfg.__dict__, "trilha": args.trilha})
    alvos = args.alvos or [cfg.raiz / p for p in cfg.pastas_telas]
    faltando = [a for a in alvos if not a.exists()]
    if faltando:
        print(tr(f"caminho inexistente: {faltando[0]}", f"path does not exist: {faltando[0]}"), file=sys.stderr)
        return 2
    print(tr(
        f"INFO config: {cfg.origem.name if cfg.origem else 'nenhum (defaults genéricos)'}; "
        f"trilha_dados: {cfg.trilha or 'não definida (regras de conector desligadas)'}",
        f"INFO config: {cfg.origem.name if cfg.origem else 'none (generic defaults)'}; "
        f"trilha_dados: {cfg.trilha or 'not set (connector rules off)'}"))
    arquivos = descobrir_arquivos(alvos, cfg)
    achados = validar_arquivos(arquivos, cfg, args.formato or cfg.formato, Path.cwd())
    for a in achados:
        print(a.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    print(tr(f"{erros} erro(s), {len(achados) - erros} aviso(s)",
             f"{erros} error(s), {len(achados) - erros} warning(s)"))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
