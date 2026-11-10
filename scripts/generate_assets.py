#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o painel vetorial SVG e renderiza a captura PNG em alta resolução (1440x900) via Chrome headless."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.calculator import dimensionar_perfil_metalico
from estruturas_metalicas_nbr8800.codecs import carregar_json_canonico, entrada_de_dict
from estruturas_metalicas_nbr8800.svg_generator import gerar_painel_svg


def main() -> int:
    raiz = Path(__file__).parent.parent
    caminho_exemplo = raiz / "examples" / "viga_coluna_w250x38_flexo_compressao.json"
    caminho_svg = raiz / "docs" / "painel_exemplo.svg"
    caminho_png = raiz / "docs" / "exemplo.png"

    caminho_svg.parent.mkdir(parents=True, exist_ok=True)

    dados = carregar_json_canonico(caminho_exemplo)
    designacao, nome_aco, contorno, solicitacoes = entrada_de_dict(dados)
    resultado = dimensionar_perfil_metalico(designacao, nome_aco, contorno, solicitacoes)

    conteudo_svg = gerar_painel_svg(resultado)
    with open(caminho_svg, "w", encoding="utf-8") as f:
        f.write(conteudo_svg)
    print(f"Painel SVG gerado em: {caminho_svg}")

    # Renderizar com Chrome Headless em 1440x900
    chrome_bin = None
    for cand in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        res = subprocess.run(["which", cand], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            chrome_bin = res.stdout.strip()
            break

    if not chrome_bin:
        print("Aviso: Navegador Chrome/Chromium não encontrado para captura PNG.")
        return 0

    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        "--hide-scrollbars",
        f"--screenshot={caminho_png.absolute()}",
        str(caminho_svg.absolute()),
    ]
    sub = subprocess.run(cmd, capture_output=True, text=True)
    if sub.returncode == 0 and caminho_png.exists():
        print(f"Captura PNG de alta resolução gerada com sucesso em: {caminho_png} ({os.path.getsize(caminho_png)} bytes)")
    else:
        print(f"Erro ao renderizar PNG com Chrome: {sub.stderr}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
