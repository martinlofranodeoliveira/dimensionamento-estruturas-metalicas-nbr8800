# -*- coding: utf-8 -*-
"""Interface de linha de comando (CLI) para dimensionamento de estruturas metálicas (ABNT NBR 8800:2024).

Fornece comandos completos em português com saída em múltiplos formatos (texto, json, csv, svg, zip)
e proteção de codificação para execução multiplataforma no Linux e Windows.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import sys

from .calculator import dimensionar_perfil_metalico, obter_aco_estrutural, obter_perfil_w
from .constants import CATALOGO_PERFIS_W, PROPRIEDADES_ACOS
from .codecs import (
    carregar_json_canonico,
    entrada_de_dict,
    resultado_para_dict,
    salvar_json_canonico,
)
from .exporters import (
    exportar_csv,
    exportar_relatorio_texto,
    exportar_zip_deterministico,
)
from .models import CondicoesContornoAco, SolicitacoesAco
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"


def _configurar_stdout_seguro() -> None:
    """Garante que a saída padrão suporte UTF-8 sem falhar sob codificação legada no Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="estruturas-metalicas",
        description="Dimensionamento e verificação analítica de perfis de aço estrutural (ABNT NBR 8800:2024).",
        add_help=False,
    )

    parser.add_argument("-h", "--help", "--ajuda", action="help", help="Exibe esta mensagem de ajuda e sai.")
    parser.add_argument(
        "-v",
        "--version",
        "--versao",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão do programa e sai.",
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Subcomando 'calcular'
    p_calc = subparsers.add_parser(
        "calcular",
        help="Dimensiona e verifica um perfil estrutural a partir de arquivo JSON de entrada.",
        add_help=False,
    )
    p_calc.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando calcular.")
    p_calc.add_argument("arquivo_entrada", help="Caminho do arquivo JSON canônico com os dados de entrada.")
    p_calc.add_argument(
        "-f",
        "--formato",
        choices=["texto", "json", "csv", "svg", "zip"],
        default="texto",
        help="Formato da saída gerada (padrão: texto).",
    )
    p_calc.add_argument(
        "-o",
        "--saida",
        help="Caminho do arquivo de saída (opcional para texto/json; obrigatório para zip/svg se especificado).",
    )

    # Subcomando 'verificar'
    p_ver = subparsers.add_parser(
        "verificar",
        help="Verifica a conformidade normativa do perfil e retorna código de saída 0 ou 1.",
        add_help=False,
    )
    p_ver.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando verificar.")
    p_ver.add_argument("arquivo_entrada", help="Caminho do arquivo JSON de entrada.")

    # Subcomando 'catalogo'
    p_cat = subparsers.add_parser(
        "catalogo",
        help="Exibe a lista de perfis de abas paralelas (W) ou aços estruturais disponíveis.",
        add_help=False,
    )
    p_cat.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando catalogo.")
    p_cat.add_argument(
        "--tipo",
        choices=["perfis", "acos", "todos"],
        default="perfis",
        help="Tipo de catálogo a ser listado (padrão: perfis).",
    )

    # Subcomando 'gerar-exemplo'
    p_ex = subparsers.add_parser(
        "gerar-exemplo",
        help="Gera um modelo de arquivo JSON canônico de entrada.",
        add_help=False,
    )
    p_ex.add_argument("-h", "--help", "--ajuda", action="help", help="Ajuda do comando gerar-exemplo.")
    p_ex.add_argument(
        "--tipo",
        choices=["combinada", "compressao", "flexao", "tracao"],
        default="combinada",
        help="Tipo de caso de exemplo (padrão: combinada).",
    )
    p_ex.add_argument(
        "-o",
        "--saida",
        default="perfil_metalico_exemplo.json",
        help="Caminho do arquivo de destino (padrão: perfil_metalico_exemplo.json).",
    )

    return parser


def comando_calcular(args: argparse.Namespace) -> int:
    try:
        dados_json = carregar_json_canonico(args.arquivo_entrada)
        designacao, nome_aco, contorno, solicitacoes = entrada_de_dict(dados_json)
        resultado = dimensionar_perfil_metalico(designacao, nome_aco, contorno, solicitacoes)
    except Exception as exc:
        print(f"Erro no processamento da estrutura metálica: {exc}", file=sys.stderr)
        return 1

    formato = args.formato
    saida = args.saida

    if formato == "texto":
        relatorio = exportar_relatorio_texto(resultado)
        if saida:
            with open(saida, "w", encoding="utf-8") as f:
                f.write(relatorio)
            print(f"Relatório salvo em: {saida}")
        else:
            print(relatorio)
    elif formato == "json":
        if saida:
            salvar_json_canonico(resultado, saida)
            print(f"Resultado JSON salvo em: {saida}")
        else:
            dados = resultado_para_dict(resultado)
            print(json.dumps(dados, indent=2, ensure_ascii=False, sort_keys=True))
    elif formato == "csv":
        if not saida:
            saida = f"resultado_{resultado.perfil.designacao.replace(' ', '_')}.csv"
        exportar_csv(resultado, saida)
        print(f"Planilha CSV salva em: {saida}")
    elif formato == "svg":
        if not saida:
            saida = f"painel_{resultado.perfil.designacao.replace(' ', '_')}.svg"
        conteudo_svg = gerar_painel_svg(resultado)
        with open(saida, "w", encoding="utf-8") as f:
            f.write(conteudo_svg)
        print(f"Painel vetorial SVG salvo em: {saida}")
    elif formato == "zip":
        if not saida:
            saida = f"pacote_{resultado.perfil.designacao.replace(' ', '_')}.zip"
        conteudo_svg = gerar_painel_svg(resultado)
        exportar_zip_deterministico(resultado, saida, conteudo_svg=conteudo_svg)
        print(f"Pacote determinístico ZIP salvo em: {saida}")

    return 0 if resultado.conformidade_geral else 2


def comando_verificar(args: argparse.Namespace) -> int:
    try:
        dados_json = carregar_json_canonico(args.arquivo_entrada)
        designacao, nome_aco, contorno, solicitacoes = entrada_de_dict(dados_json)
        resultado = dimensionar_perfil_metalico(designacao, nome_aco, contorno, solicitacoes)
    except Exception as exc:
        print(f"Erro de validação: {exc}", file=sys.stderr)
        return 1

    if resultado.conformidade_geral:
        print(f"[CONFORME] Perfil '{resultado.perfil.designacao}' em aço '{resultado.aco.nome}' atende a todos os critérios da ABNT NBR 8800:2024.")
        print(f"           {resultado.resumo_executivo}")
        return 0
    else:
        print(f"[NÃO CONFORME] Perfil '{resultado.perfil.designacao}' em aço '{resultado.aco.nome}' apresenta não-conformidades estruturais.")
        print(f"               {resultado.resumo_executivo}", file=sys.stderr)
        return 1


def comando_catalogo(args: argparse.Namespace) -> int:
    tipo = args.tipo
    if tipo in ("perfis", "todos"):
        print("=== CATÁLOGO DE PERFIS LAMINADOS W (NBR 8800:2024) ===")
        print(f"{'Designação':<14} | {'d (mm)':<8} | {'bf (mm)':<8} | {'tw (mm)':<8} | {'tf (mm)':<8} | {'Ag (cm²)':<9} | {'Zx (cm³)':<9}")
        print("-" * 75)
        for desig in CATALOGO_PERFIS_W:
            p = obter_perfil_w(desig)
            d_mm = float(p.d_cm * 10)
            bf_mm = float(p.bf_cm * 10)
            tw_mm = float(p.tw_cm * 10)
            tf_mm = float(p.tf_cm * 10)
            ag = float(p.ag_cm2)
            zx = float(p.zx_cm3)
            print(
                f"{desig:<14} | {d_mm:<8.1f} | {bf_mm:<8.1f} | "
                f"{tw_mm:<8.1f} | {tf_mm:<8.1f} | {ag:<9.2f} | {zx:<9.1f}"
            )
        print()

    if tipo in ("acos", "todos"):
        print("=== AÇOS ESTRUTURAIS DISPONÍVEIS ===")
        print(f"{'Nome / Norma':<18} | {'fy (kN/cm²)':<12} | {'fu (kN/cm²)':<12} | {'E (kN/cm²)':<12}")
        print("-" * 60)
        for chave in PROPRIEDADES_ACOS:
            aco = obter_aco_estrutural(chave)
            print(
                f"{aco.nome:<18} | {float(aco.f_y_kn_cm2):<12.1f} | "
                f"{float(aco.f_u_kn_cm2):<12.1f} | {float(aco.e_kn_cm2):<12.0f}"
            )
        print()

    return 0


def comando_gerar_exemplo(args: argparse.Namespace) -> int:
    tipo = args.tipo
    if tipo == "compressao":
        exemplo = {
            "perfil": "W200x31.3",
            "aco": "A572_GR50",
            "contorno": {
                "kx_lx_cm": "300",
                "ky_ly_cm": "300",
                "lb_cm": "300",
                "cb_fator": "1",
            },
            "solicitacoes": {
                "nsd_tracao_kn": "0",
                "nsd_compressao_kn": "450",
                "msd_x_kn_cm": "0",
                "msd_y_kn_cm": "0",
                "vsd_y_kn": "0",
            },
        }
    elif tipo == "flexao":
        exemplo = {
            "perfil": "W310x32.7",
            "aco": "A572_GR50",
            "contorno": {
                "kx_lx_cm": "500",
                "ky_ly_cm": "150",
                "lb_cm": "150",
                "cb_fator": "1",
            },
            "solicitacoes": {
                "nsd_tracao_kn": "0",
                "nsd_compressao_kn": "0",
                "msd_x_kn_cm": "6500",
                "msd_y_kn_cm": "0",
                "vsd_y_kn": "85",
            },
        }
    elif tipo == "tracao":
        exemplo = {
            "perfil": "W150x18.0",
            "aco": "A36",
            "contorno": {
                "kx_lx_cm": "250",
                "ky_ly_cm": "250",
                "lb_cm": "250",
                "cb_fator": "1",
            },
            "solicitacoes": {
                "nsd_tracao_kn": "350",
                "nsd_compressao_kn": "0",
                "msd_x_kn_cm": "0",
                "msd_y_kn_cm": "0",
                "vsd_y_kn": "0",
            },
        }
    else:  # combinada
        exemplo = {
            "perfil": "W250x38.5",
            "aco": "A572_GR50",
            "contorno": {
                "kx_lx_cm": "350",
                "ky_ly_cm": "350",
                "lb_cm": "175",
                "cb_fator": "1.14",
            },
            "solicitacoes": {
                "nsd_tracao_kn": "0",
                "nsd_compressao_kn": "280",
                "msd_x_kn_cm": "4200",
                "msd_y_kn_cm": "350",
                "vsd_y_kn": "65",
            },
        }

    with open(args.saida, "w", encoding="utf-8") as f:
        json.dump(exemplo, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Modelo JSON de estrutura metálica gerado com sucesso em: {args.saida}")
    return 0


def main(argv: list[str] | None = None) -> int:
    _configurar_stdout_seguro()
    parser = _criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "calcular":
        return comando_calcular(args)
    elif args.comando == "verificar":
        return comando_verificar(args)
    elif args.comando == "catalogo":
        return comando_catalogo(args)
    elif args.comando == "gerar-exemplo":
        return comando_gerar_exemplo(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
