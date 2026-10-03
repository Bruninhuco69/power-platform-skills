#!/usr/bin/env python3
"""Fotografa páginas HTML do projeto com o Chrome ou o Edge sem janela, para alguém olhar antes do usuário.

A verificação visual (`references/verificacao-visual.md`) existe porque validador de arquivo não vê
texto cortado, sobreposição ou contraste ruim: quem julga abre a imagem e olha.

  capturar-telas.py docs/planejamento/prototipo/index.html
      protótipo: uma imagem por tela (`<section data-tela>`), no padrão de navegação do arquivo
  capturar-telas.py docs/planejamento/prototipo/index.html --navegacoes
      só a primeira tela, uma vez em cada um dos cinco padrões de navegação
  capturar-telas.py docs/planejamento/identidade.html
      página comum (sem data-tela): uma imagem da página

Opções: --telas tela-a,tela-b · --perfil <chave de PERFIS> · --nav <padrão> · --saida PASTA
(default: `capturas/` ao lado do HTML) · --largura/--altura · --simular (só lista o que faria).
Navegador: variável PP_NAVEGADOR (caminho do executável) ou o primeiro Chrome/Edge/Chromium achado.

Exit: 0 tudo capturado · 1 alguma captura falhou · 2 uso incorreto (arquivo, opção, navegador ausente).
"""
from __future__ import annotations

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

_PASTA = str(Path(__file__).resolve().parent)  # _idioma.py fica ao lado
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)
from _idioma import tradutor  # noqa: E402

tr = tradutor(__file__)

PADROES_NAV = ("lateral-fixo", "lateral-recolhivel", "gaveta", "topo", "inicio-cartoes")
TAMANHO_PROTOTIPO = (1920, 1160)  # 1080 do canvas + a barra de controles do protótipo
TAMANHO_PAGINA = (1440, 2000)
TIMEOUT_S = 60
ESPERA_JS_MS = 3000
RE_TELA = re.compile(r"<section\b[^>]*\bdata-tela=\"([a-z0-9-]+)\"", re.IGNORECASE)
NOMES_NAVEGADOR = ("chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                   "msedge", "microsoft-edge", "microsoft-edge-stable")


@dataclass(frozen=True)
class Captura:
    nome: str
    url: str
    destino: Path


def _saida_utf8() -> None:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, LookupError, io.UnsupportedOperation):
            pass


def _caminhos_conhecidos() -> list[Path]:
    bases = [os.environ.get(v, "") for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    windows = [Path(b) / sub for b in bases if b for sub in (
        Path("Google/Chrome/Application/chrome.exe"), Path("Microsoft/Edge/Application/msedge.exe"))]
    mac = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
           Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
           Path("/Applications/Chromium.app/Contents/MacOS/Chromium")]
    return windows + mac


def achar_navegador() -> Path | None:
    escolhido = os.environ.get("PP_NAVEGADOR", "").strip()
    if escolhido:
        return Path(escolhido) if Path(escolhido).is_file() else None
    for nome in NOMES_NAVEGADOR:
        achado = shutil.which(nome)
        if achado:
            return Path(achado)
    return next((p for p in _caminhos_conhecidos() if p.is_file()), None)


def telas_do_html(texto: str) -> list[str]:
    vistas: list[str] = []
    for tela in RE_TELA.findall(texto):
        if tela not in vistas:
            vistas.append(tela)
    return vistas


def montar_url(html: Path, perfil: str = "", nav: str = "", tela: str = "") -> str:
    consulta = "&".join(f"{k}={v}" for k, v in (("perfil", perfil), ("nav", nav)) if v)
    return html.resolve().as_uri() + (f"?{consulta}" if consulta else "") + (f"#/{tela}" if tela else "")


def planejar(html: Path, args: argparse.Namespace) -> list[Captura]:
    saida = args.saida or html.parent / "capturas"
    telas = telas_do_html(html.read_text(encoding="utf-8"))
    if not telas:
        return [Captura(html.stem, montar_url(html), saida / f"{html.stem}.png")]
    if args.telas:
        pedidas = [t.strip() for t in args.telas.split(",") if t.strip()]
        faltam = [t for t in pedidas if t not in telas]
        if faltam:
            raise ValueError(tr(f"tela(s) que o HTML não tem: {', '.join(faltam)} (tem: {', '.join(telas)})",
                                f"screen(s) the HTML does not have: {', '.join(faltam)} (it has: {', '.join(telas)})"))
        telas = pedidas
    if args.navegacoes:
        return [Captura(f"{telas[0]}--{nav}", montar_url(html, args.perfil, nav, telas[0]),
                        saida / f"{telas[0]}--{nav}.png") for nav in PADROES_NAV]
    sufixo = f"--{args.nav}" if args.nav else ""
    return [Captura(t + sufixo, montar_url(html, args.perfil, args.nav, t), saida / f"{t}{sufixo}.png")
            for t in telas]


def comando(navegador: Path, captura: Captura, tamanho: tuple[int, int], perfil_dir: Path) -> list[str]:
    largura, altura = tamanho
    return [str(navegador), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", "--disable-extensions", f"--user-data-dir={perfil_dir}",
            f"--window-size={largura},{altura}", f"--virtual-time-budget={ESPERA_JS_MS}",
            f"--screenshot={captura.destino.resolve()}", captura.url]


def capturar(navegador: Path, captura: Captura, tamanho: tuple[int, int]) -> str | None:
    """Tira a foto; devolve a mensagem de erro ou None."""
    captura.destino.parent.mkdir(parents=True, exist_ok=True)
    captura.destino.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="pp-captura-") as perfil_dir:  # perfil limpo: não usa o Chrome aberto
        try:
            subprocess.run(comando(navegador, captura, tamanho, Path(perfil_dir)), capture_output=True,
                           timeout=TIMEOUT_S, check=False)
        except subprocess.TimeoutExpired:
            return tr(f"o navegador passou de {TIMEOUT_S}s", f"the browser exceeded {TIMEOUT_S}s")
        except OSError as erro:
            return tr(f"não consegui rodar o navegador ({erro})", f"could not run the browser ({erro})")
    if not captura.destino.is_file() or captura.destino.stat().st_size == 0:
        return tr("o navegador terminou sem gravar a imagem", "the browser finished without writing the image")
    return None


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=tr("Fotografa as telas do protótipo ou uma página HTML (Chrome/Edge sem janela).",
                                                "Screenshots the prototype screens or an HTML page (headless Chrome/Edge)."),
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=tr("Exit: 0 ok, 1 alguma captura falhou, 2 uso incorreto.",
                                        "Exit: 0 ok, 1 a capture failed, 2 incorrect usage."))
    ap.add_argument("html", type=Path, help=tr("o arquivo .html", "the .html file"))
    ap.add_argument("--telas", help=tr("só estas telas (ids separados por vírgula)", "only these screens (comma-separated ids)"))
    ap.add_argument("--perfil", default="", help=tr("chave de PERFIS do protótipo (default: o do arquivo)",
                    "key of the prototype PERFIS (default: the file's own)"))
    ap.add_argument("--nav", default="", choices=("", *PADROES_NAV), help=tr("padrão de navegação (default: o do arquivo)",
                                                                                   "navigation pattern (default: the file's own)"))
    ap.add_argument("--navegacoes", action="store_true", help=tr("a primeira tela em cada padrão de navegação",
                    "the first screen in each navigation pattern"))
    ap.add_argument("--saida", type=Path, help=tr("pasta das imagens (default: capturas/ ao lado do HTML)",
                    "folder for the images (default: capturas/ next to the HTML)"))
    ap.add_argument("--largura", type=int, help=tr("largura da janela em px", "window width in px"))
    ap.add_argument("--altura", type=int, help=tr("altura da janela em px", "window height in px"))
    ap.add_argument("--simular", action="store_true", help=tr("só lista as capturas, sem abrir o navegador",
                    "only lists the captures, without opening the browser"))
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _saida_utf8()
    args = _argumentos(argv)
    if not args.html.is_file():
        print(tr(f"ERRO arquivo não encontrado: {args.html}", f"ERROR file not found: {args.html}"), file=sys.stderr)
        return 2
    if args.perfil and not re.fullmatch(r"[A-Za-z0-9_-]+", args.perfil):
        print(tr(f"ERRO --perfil inválido: {args.perfil!r}", f"ERROR invalid --perfil: {args.perfil!r}"), file=sys.stderr)
        return 2
    try:
        capturas = planejar(args.html, args)
    except ValueError as erro:
        print(tr(f"ERRO {erro}", f"ERROR {erro}"), file=sys.stderr)
        return 2
    prototipo = bool(telas_do_html(args.html.read_text(encoding="utf-8")))
    padrao = TAMANHO_PROTOTIPO if prototipo else TAMANHO_PAGINA
    tamanho = (args.largura or padrao[0], args.altura or padrao[1])
    if args.simular:
        for c in capturas:
            print(f"○ {c.nome} → {c.destino.as_posix()}  ({c.url})")
        print(tr(f"{len(capturas)} captura(s) planejada(s), {tamanho[0]}x{tamanho[1]}",
                f"{len(capturas)} capture(s) planned, {tamanho[0]}x{tamanho[1]}"))
        return 0
    navegador = achar_navegador()
    if navegador is None:
        print(tr("ERRO nenhum Chrome, Edge ou Chromium encontrado: instale um ou aponte PP_NAVEGADOR para o "
                 "executável. Sem navegador, a verificação visual fica \"não verificado\".",
                 "ERROR no Chrome, Edge or Chromium found: install one or point PP_NAVEGADOR to the "
                 "executable. Without a browser, the visual verification stays \"not verified\"."), file=sys.stderr)
        return 2
    erros = 0
    for c in capturas:
        falha = capturar(navegador, c, tamanho)
        if falha:
            erros += 1
            print(f"✗ {c.nome}: {falha}")
        else:
            print(f"✓ {c.nome} → {c.destino.as_posix()}")
    print(tr(f"{len(capturas) - erros} captura(s), {erros} erro(s) · {navegador.name} · {tamanho[0]}x{tamanho[1]}",
             f"{len(capturas) - erros} capture(s), {erros} error(s) · {navegador.name} · {tamanho[0]}x{tamanho[1]}"))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
