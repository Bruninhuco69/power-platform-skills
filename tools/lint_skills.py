#!/usr/bin/env python3
"""Lint do padrão de skill (docs/PADRAO-SKILL.md) e da sanitização do repositório.

Uso:
    python tools/lint_skills.py                 # repositório inteiro
    python tools/lint_skills.py skills/<nome>   # só uma skill (+ sanitização dela)
    python tools/lint_skills.py --sem-scripts   # não executa `--help` dos scripts

Saída: `caminho:linha: ERRO|AVISO <CÓDIGO> mensagem` e, no fim, `N erro(s), M aviso(s)`.
Exit: 0 sem erro, 1 com erro, 2 uso incorreto.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

RAIZ_PADRAO = Path(__file__).resolve().parent.parent

LIMITE_AVISO_SKILL = 250
LIMITE_ERRO_SKILL = 500
LIMITE_SUMARIO = 300
LIMITE_DIVIDIR = 1000
LINHAS_BUSCA_SUMARIO = 40
DESCRICAO_MIN = 50
DESCRICAO_MAX = 1024
TIMEOUT_HELP_S = 30

NOME_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUMARIO = re.compile(r"^#{1,3}\s+(Sumário|Índice|Sumario|Indice)\b", re.IGNORECASE)
LINK_MD = re.compile(r"\]\(([^)\s]+)\)")
CAMINHO_CRASE = re.compile(r"`((?:references|scripts|assets|prompts)/[^`\s]+)`")
MARCA_ISENCAO = "lint-ok"

EXTENSOES_TEXTO = {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".ps1", ".sql", ".m", ".dax", ".csv"}
PASTAS_IGNORADAS = {".git", "__pycache__", ".pytest_cache", ".venv", "dist"}
ARQUIVO_LOCAL_SANITIZACAO = Path("tools/sanitizacao.local.txt")
FIXTURES_LINT = Path("tests/_lint")  # dados de teste do próprio lint

SANITIZACAO_GENERICA = [
    ("S001", re.compile(r"[A-Za-z]:[\\/]+Users[\\/]", re.IGNORECASE), "caminho absoluto de usuário"),  # lint-ok
    ("S001", re.compile(r"/c/Users/|/home/[a-z]", re.IGNORECASE), "caminho absoluto de usuário"),  # lint-ok
    ("S001", re.compile(r"(?:^|[\s\\/`'\"])OneDrive(?:[\\/]| - )", re.IGNORECASE), "pasta pessoal sincronizada"),  # lint-ok
]
EMAIL = re.compile(r"\b[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
DOMINIOS_FICTICIOS = {"contoso.com", "fabrikam.com", "example.com", "exemplo.com", "exemplo.com.br"}
PREFIXO_ANOTACAO_ODATA = "odata."  # <coluna>@odata.bind, @odata.nextLink: anotação OData, não e-mail
GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
PREFIXO_GUID_FICTICIO = "00000000-0000-0000-"


@dataclass(frozen=True)
class Achado:
    caminho: str
    linha: int
    nivel: str  # "ERRO" | "AVISO"
    codigo: str
    mensagem: str

    def formatar(self) -> str:
        return f"{self.caminho}:{self.linha}: {self.nivel} {self.codigo} {self.mensagem}"


def _rel(caminho: Path, raiz: Path) -> str:
    try:
        return caminho.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return caminho.as_posix()


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8", errors="replace")


def ler_frontmatter(texto: str) -> tuple[dict | None, str | None]:
    """Devolve (frontmatter, erro). Frontmatter é o YAML entre as duas primeiras linhas `---`."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return None, "SKILL.md não começa com frontmatter `---`"
    try:
        fim = next(i for i, l in enumerate(linhas[1:], start=1) if l.strip() == "---")
    except StopIteration:
        return None, "frontmatter sem `---` de fechamento"
    try:
        dados = yaml.safe_load("\n".join(linhas[1:fim])) or {}
    except yaml.YAMLError as erro:
        return None, f"frontmatter não é YAML válido: {erro}"
    if not isinstance(dados, dict):
        return None, "frontmatter não é um mapeamento"
    return dados, None


def checar_frontmatter(skill: Path, texto: str, raiz: Path) -> list[Achado]:
    rel = _rel(skill / "SKILL.md", raiz)
    dados, erro = ler_frontmatter(texto)
    if erro:
        return [Achado(rel, 1, "ERRO", "L002", erro)]
    achados: list[Achado] = []
    nome = dados.get("name")
    if nome != skill.name:
        achados.append(Achado(rel, 1, "ERRO", "L003", f"name `{nome}` difere da pasta `{skill.name}`"))
    elif not NOME_KEBAB.match(nome):
        achados.append(Achado(rel, 1, "ERRO", "L003", f"name `{nome}` não é kebab-case"))
    descricao = str(dados.get("description") or "").strip()
    if not (DESCRICAO_MIN <= len(descricao) <= DESCRICAO_MAX):
        achados.append(Achado(rel, 1, "ERRO", "L004",
                              f"description com {len(descricao)} caracteres (aceito: {DESCRICAO_MIN}-{DESCRICAO_MAX})"))
    if descricao and not descricao.startswith("Use quando"):
        achados.append(Achado(rel, 1, "AVISO", "L005", "description não começa com \"Use quando\""))
    if descricao and "Não use" not in descricao:
        achados.append(Achado(rel, 1, "AVISO", "L006", "description sem \"Não use para ...\" (exclusões)"))
    return achados


def checar_tamanho_skill(skill: Path, texto: str, raiz: Path) -> list[Achado]:
    total = len(texto.splitlines())
    rel = _rel(skill / "SKILL.md", raiz)
    if total > LIMITE_ERRO_SKILL:
        return [Achado(rel, total, "ERRO", "L007", f"SKILL.md com {total} linhas (máximo {LIMITE_ERRO_SKILL})")]
    if total > LIMITE_AVISO_SKILL:
        return [Achado(rel, total, "AVISO", "L007", f"SKILL.md com {total} linhas (alvo ≤ {LIMITE_AVISO_SKILL})")]
    return []


def checar_referencias(skill: Path, raiz: Path) -> list[Achado]:
    achados: list[Achado] = []
    if (skill / "reference").is_dir():
        achados.append(Achado(_rel(skill / "reference", raiz), 1, "ERRO", "L008",
                              "pasta `reference/` — o padrão é `references/`"))
    pasta = skill / "references"
    if not pasta.is_dir():
        return achados
    for arquivo in sorted(pasta.rglob("*.md")):
        linhas = _ler(arquivo).splitlines()
        rel = _rel(arquivo, raiz)
        if len(linhas) > LIMITE_SUMARIO and not any(SUMARIO.match(l) for l in linhas[:LINHAS_BUSCA_SUMARIO]):
            achados.append(Achado(rel, 1, "AVISO", "L009",
                                  f"{len(linhas)} linhas sem `## Sumário` nas primeiras {LINHAS_BUSCA_SUMARIO}"))
        if len(linhas) > LIMITE_DIVIDIR:
            achados.append(Achado(rel, 1, "AVISO", "L010", f"{len(linhas)} linhas — dividir (alvo ≤ {LIMITE_DIVIDIR})"))
    return achados


def checar_links(skill: Path, texto: str, raiz: Path) -> list[Achado]:
    achados: list[Achado] = []
    rel = _rel(skill / "SKILL.md", raiz)
    for numero, linha in enumerate(texto.splitlines(), start=1):
        alvos = [m.group(1) for m in LINK_MD.finditer(linha)] + [m.group(1) for m in CAMINHO_CRASE.finditer(linha)]
        for alvo in alvos:
            if alvo.startswith(("http://", "https://", "#", "mailto:")) or "<" in alvo or "*" in alvo:
                continue
            caminho = (skill / alvo.split("#", 1)[0]).resolve()
            if not caminho.exists():
                achados.append(Achado(rel, numero, "ERRO", "L011", f"link para `{alvo}`, que não existe"))
    return achados


def checar_scripts(skill: Path, raiz: Path, executar: bool) -> list[Achado]:
    pasta = skill / "scripts"
    scripts = sorted(p for p in pasta.glob("*.py") if not p.name.startswith("_")) if pasta.is_dir() else []
    achados: list[Achado] = []
    if scripts and not list((raiz / "tests" / skill.name).glob("test_*.py")):
        achados.append(Achado(_rel(pasta, raiz), 1, "AVISO", "L013",
                              f"scripts sem testes em `tests/{skill.name}/test_*.py`"))
    if not executar:
        return achados
    for script in scripts:
        try:
            resultado = subprocess.run([sys.executable, str(script), "--help"], capture_output=True,
                                       text=True, timeout=TIMEOUT_HELP_S, cwd=str(skill))
            falhou = resultado.returncode != 0
            detalhe = (resultado.stderr or resultado.stdout).strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            falhou, detalhe = True, [f"sem resposta em {TIMEOUT_HELP_S}s"]
        if falhou:
            achados.append(Achado(_rel(script, raiz), 1, "ERRO", "L012", f"`--help` falhou: {detalhe[0]}"))
    return achados


def checar_skill(skill: Path, raiz: Path, executar_scripts: bool = True) -> list[Achado]:
    arquivo = skill / "SKILL.md"
    if not arquivo.is_file():
        return [Achado(_rel(skill, raiz), 1, "ERRO", "L001", "pasta de skill sem SKILL.md")]
    texto = _ler(arquivo)
    return (checar_frontmatter(skill, texto, raiz) + checar_tamanho_skill(skill, texto, raiz)
            + checar_referencias(skill, raiz) + checar_links(skill, texto, raiz)
            + checar_scripts(skill, raiz, executar_scripts))


def carregar_padroes_locais(raiz: Path) -> list[re.Pattern]:
    arquivo = raiz / ARQUIVO_LOCAL_SANITIZACAO
    if not arquivo.is_file():
        return []
    padroes = []
    for linha in _ler(arquivo).splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#"):
            padroes.append(re.compile(linha, re.IGNORECASE))
    return padroes


def arquivos_texto(alvo: Path, raiz: Path) -> list[Path]:
    candidatos = [alvo] if alvo.is_file() else alvo.rglob("*")
    excluidos = {(raiz / ARQUIVO_LOCAL_SANITIZACAO).resolve()}
    fixtures = (raiz / FIXTURES_LINT).resolve()
    saida = []
    for p in candidatos:
        if not p.is_file() or p.suffix.lower() not in EXTENSOES_TEXTO:
            continue
        if any(parte in PASTAS_IGNORADAS for parte in p.parts) or p.resolve() in excluidos:
            continue
        if fixtures in p.resolve().parents:
            continue
        saida.append(p)
    return sorted(saida)


def checar_sanitizacao(alvo: Path, raiz: Path, padroes_locais: list[re.Pattern]) -> list[Achado]:
    achados: list[Achado] = []
    for arquivo in arquivos_texto(alvo, raiz):
        rel = _rel(arquivo, raiz)
        for numero, linha in enumerate(_ler(arquivo).splitlines(), start=1):
            if MARCA_ISENCAO in linha:
                continue
            for codigo, padrao, motivo in SANITIZACAO_GENERICA:
                if padrao.search(linha):
                    achados.append(Achado(rel, numero, "ERRO", codigo, motivo))
            for email in EMAIL.findall(linha):
                dominio = email.split("@", 1)[1].lower()
                if dominio not in DOMINIOS_FICTICIOS and not dominio.startswith(PREFIXO_ANOTACAO_ODATA):
                    achados.append(Achado(rel, numero, "ERRO", "S002", f"e-mail real `{email}` (use @contoso.com)"))
            for guid in GUID.findall(linha):
                if not guid.lower().startswith(PREFIXO_GUID_FICTICIO):
                    achados.append(Achado(rel, numero, "ERRO", "S003",
                                          f"GUID `{guid}` não fictício (use {PREFIXO_GUID_FICTICIO}...)"))
            for padrao in padroes_locais:
                if padrao.search(linha):
                    achados.append(Achado(rel, numero, "ERRO", "S004", "nome interno listado em sanitizacao.local.txt"))
    return achados


def checar_manifestos(raiz: Path) -> list[Achado]:
    plugin = raiz / ".claude-plugin" / "plugin.json"
    mercado = raiz / ".claude-plugin" / "marketplace.json"
    if not plugin.is_file() or not mercado.is_file():
        return [Achado(".claude-plugin", 1, "ERRO", "R001", "falta plugin.json ou marketplace.json")]
    try:
        versao = json.loads(_ler(plugin)).get("version")
        versoes_mercado = {p.get("version") for p in json.loads(_ler(mercado)).get("plugins", [])}
    except json.JSONDecodeError as erro:
        return [Achado(".claude-plugin", 1, "ERRO", "R001", f"manifesto não é JSON válido: {erro}")]
    achados = []
    if versoes_mercado != {versao}:
        achados.append(Achado(".claude-plugin/marketplace.json", 1, "ERRO", "R001",
                              f"versão {sorted(map(str, versoes_mercado))} difere do plugin.json ({versao})"))
    changelog = raiz / "CHANGELOG.md"
    if not changelog.is_file() or f"[{versao}]" not in _ler(changelog):
        achados.append(Achado("CHANGELOG.md", 1, "AVISO", "R002", f"CHANGELOG sem entrada `[{versao}]`"))
    return achados


def executar(alvos: list[Path], raiz: Path, executar_scripts: bool = True) -> list[Achado]:
    achados: list[Achado] = []
    padroes_locais = carregar_padroes_locais(raiz)
    if not padroes_locais:
        achados.append(Achado(ARQUIVO_LOCAL_SANITIZACAO.as_posix(), 1, "AVISO", "S000",
                              "arquivo ausente ou vazio — só padrões genéricos de sanitização"))
    repo_inteiro = alvos == [raiz]
    if repo_inteiro:
        achados += checar_manifestos(raiz)
        skills = sorted(p for p in (raiz / "skills").iterdir() if p.is_dir()) if (raiz / "skills").is_dir() else []
    else:
        skills = [a for a in alvos if a.is_dir() and a.parent.name == "skills"]
    for skill in skills:
        achados += checar_skill(skill, raiz, executar_scripts)
    for alvo in alvos:
        achados += checar_sanitizacao(alvo, raiz, padroes_locais)
    return achados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint do padrão de skill e da sanitização.")
    parser.add_argument("alvos", nargs="*", type=Path, help="pastas de skill ou arquivos (default: repo inteiro)")
    parser.add_argument("--raiz", type=Path, default=RAIZ_PADRAO, help="raiz do repositório")
    parser.add_argument("--sem-scripts", action="store_true", help="não executa `--help` dos scripts")
    args = parser.parse_args(argv)

    raiz = args.raiz.resolve()
    alvos = [a.resolve() for a in args.alvos] or [raiz]
    inexistentes = [a for a in alvos if not a.exists()]
    if inexistentes:
        print(f"caminho inexistente: {inexistentes[0]}", file=sys.stderr)
        return 2

    achados = executar(alvos, raiz, executar_scripts=not args.sem_scripts)
    for achado in achados:
        print(achado.formatar())
    erros = sum(a.nivel == "ERRO" for a in achados)
    avisos = len(achados) - erros
    print(f"{erros} erro(s), {avisos} aviso(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
