"""Módulo de codificação e decodificação canônica JSON para estruturas de aço.

Padrão rigoroso LOFRANO TECNOLOGIA:
- Rejeição absoluta de BOM (\\xef\\xbb\\xbf ou \\ufeff).
- Rejeição absoluta de tipos de ponto flutuante (float) no payload de entrada.
- Rejeição de chaves duplicadas.
- Limite de profundidade de aninhamento recursivo (máximo 32).
- Serialização determinística com ordenação alfabética e indentação uniforme.
"""

from __future__ import annotations

from fractions import Fraction
import json
import os
from pathlib import Path
from typing import Any

from .models import (
    CondicoesContornoAco,
    ResultadoAco,
    SolicitacoesAco,
)

PROFUNDIDADE_MAXIMA_JSON = 32


def _rejeitar_float(token: str) -> None:
    raise ValueError(
        f"Ponto flutuante proibido na entrada canônica: '{token}'. "
        f"Forneça grandezas em inteiros ou razões exatas (ex: string '12.5' ou inteiros)."
    )


def _verificar_pares_sem_duplicacao(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    chaves_vistas = set()
    dicionario = {}
    for chave, valor in pares:
        if chave in chaves_vistas:
            raise ValueError(f"Chave duplicada detectada no JSON canônico: '{chave}'")
        chaves_vistas.add(chave)
        dicionario[chave] = valor
    return dicionario


def _verificar_profundidade(obj: Any, nivel_atual: int = 0) -> None:
    if nivel_atual > PROFUNDIDADE_MAXIMA_JSON:
        raise ValueError(
            f"Profundidade JSON excedeu o limite máximo seguro de {PROFUNDIDADE_MAXIMA_JSON} níveis."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, nivel_atual + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel_atual + 1)


def parsear_fracao(valor: Any) -> Fraction:
    """Converte inteiros, strings ou dicts racionais em Fraction exata."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, str):
        v_limpo = valor.strip().replace(",", ".")
        if "/" in v_limpo:
            partes = v_limpo.split("/")
            if len(partes) == 2:
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        return Fraction(v_limpo)
    if isinstance(valor, dict) and "numerador" in valor and "denominador" in valor:
        return Fraction(int(valor["numerador"]), int(valor["denominador"]))
    raise ValueError(f"Não foi possível converter '{valor}' ({type(valor).__name__}) em Fraction exata.")


def fracao_para_dict(f: Fraction) -> dict[str, Any]:
    """Converte uma Fraction em estrutura legível canônica."""
    return {
        "numerador": f.numerator,
        "denominador": f.denominator,
        "valor_decimal": f"{float(f):.6f}",
    }


def carregar_json_canonico(caminho_ou_conteudo: str | Path) -> dict[str, Any]:
    """Carrega dados JSON validando ausência de BOM, ausência de floats e integridade."""
    if isinstance(caminho_ou_conteudo, (str, Path)) and os.path.exists(str(caminho_ou_conteudo)):
        with open(caminho_ou_conteudo, "rb") as f:
            bytes_conteudo = f.read()
    elif isinstance(caminho_ou_conteudo, str):
        bytes_conteudo = caminho_ou_conteudo.encode("utf-8")
    else:
        raise ValueError("Entrada inválida para carregar_json_canonico.")

    if bytes_conteudo.startswith(b"\xef\xbb\xbf"):
        raise ValueError("Byte Order Mark (BOM) UTF-8 detectado e estritamente proibido.")

    texto = bytes_conteudo.decode("utf-8")
    if "\ufeff" in texto:
        raise ValueError("Caractere BOM detectado no corpo do texto e estritamente proibido.")

    dados = json.loads(
        texto,
        parse_float=_rejeitar_float,
        object_pairs_hook=_verificar_pares_sem_duplicacao,
    )
    _verificar_profundidade(dados)
    return dados


def entrada_de_dict(dados: dict[str, Any]) -> tuple[str, str, CondicoesContornoAco, SolicitacoesAco]:
    """Reconstitui os parâmetros de dimensionamento a partir de um dicionário validado."""
    perfil = str(dados.get("perfil", "W200x31.3"))
    aco = str(dados.get("aco", "A572_GR50"))

    c_dict = dados.get("contorno", {})
    contorno = CondicoesContornoAco(
        kx_lx_cm=parsear_fracao(c_dict.get("kx_lx_cm", 300)),
        ky_ly_cm=parsear_fracao(c_dict.get("ky_ly_cm", 300)),
        lb_cm=parsear_fracao(c_dict.get("lb_cm", 300)),
        cb_fator=parsear_fracao(c_dict.get("cb_fator", 1)),
    )

    s_dict = dados.get("solicitacoes", {})
    solicitacoes = SolicitacoesAco(
        nsd_tracao_kn=parsear_fracao(s_dict.get("nsd_tracao_kn", 0)),
        nsd_compressao_kn=parsear_fracao(s_dict.get("nsd_compressao_kn", 0)),
        msd_x_kn_cm=parsear_fracao(s_dict.get("msd_x_kn_cm", 0)),
        msd_y_kn_cm=parsear_fracao(s_dict.get("msd_y_kn_cm", 0)),
        vsd_y_kn=parsear_fracao(s_dict.get("vsd_y_kn", 0)),
    )

    return perfil, aco, contorno, solicitacoes


def resultado_para_dict(resultado: ResultadoAco) -> dict[str, Any]:
    """Serializa o resultado completo em dicionário canônico com valores racionais e decimais."""
    p = resultado.perfil
    a = resultado.aco
    s = resultado.solicitacoes
    c = resultado.contorno
    tr = resultado.tracao
    comp = resultado.compressao
    fl = resultado.flexao
    cis = resultado.cisalhamento
    fc = resultado.flexo_compressao

    return {
        "norma_referencia": "ABNT NBR 8800:2024",
        "perfil": {
            "designacao": p.designacao,
            "d_cm": fracao_para_dict(p.d_cm),
            "bf_cm": fracao_para_dict(p.bf_cm),
            "tw_cm": fracao_para_dict(p.tw_cm),
            "tf_cm": fracao_para_dict(p.tf_cm),
            "ag_cm2": fracao_para_dict(p.ag_cm2),
            "ix_cm4": fracao_para_dict(p.ix_cm4),
            "iy_cm4": fracao_para_dict(p.iy_cm4),
            "wx_cm3": fracao_para_dict(p.wx_cm3),
            "wy_cm3": fracao_para_dict(p.wy_cm3),
            "zx_cm3": fracao_para_dict(p.zx_cm3),
            "zy_cm3": fracao_para_dict(p.zy_cm3),
            "rx_cm": fracao_para_dict(p.rx_cm),
            "ry_cm": fracao_para_dict(p.ry_cm),
            "j_cm4": fracao_para_dict(p.j_cm4),
            "cw_cm6": fracao_para_dict(p.cw_cm6),
        },
        "aco": {
            "nome": a.nome,
            "f_y_kn_cm2": fracao_para_dict(a.f_y_kn_cm2),
            "f_u_kn_cm2": fracao_para_dict(a.f_u_kn_cm2),
            "e_kn_cm2": fracao_para_dict(a.e_kn_cm2),
        },
        "solicitacoes": {
            "nsd_tracao_kn": fracao_para_dict(s.nsd_tracao_kn),
            "nsd_compressao_kn": fracao_para_dict(s.nsd_compressao_kn),
            "msd_x_kn_cm": fracao_para_dict(s.msd_x_kn_cm),
            "msd_y_kn_cm": fracao_para_dict(s.msd_y_kn_cm),
            "vsd_y_kn": fracao_para_dict(s.vsd_y_kn),
        },
        "contorno": {
            "kx_lx_cm": fracao_para_dict(c.kx_lx_cm),
            "ky_ly_cm": fracao_para_dict(c.ky_ly_cm),
            "lb_cm": fracao_para_dict(c.lb_cm),
            "cb_fator": fracao_para_dict(c.cb_fator),
        },
        "verificacoes": {
            "tracao": {
                "nt_rd_kn": fracao_para_dict(tr.nt_rd_kn),
                "esbeltez": fracao_para_dict(tr.esbeltez),
                "ratio_tracao": fracao_para_dict(tr.ratio_tracao),
                "atende": tr.atende,
                "modo_falha": tr.modo_falha,
            },
            "compressao": {
                "lambda_max": fracao_para_dict(comp.lambda_max),
                "ne_kn": fracao_para_dict(comp.ne_kn),
                "lambda_0": fracao_para_dict(comp.lambda_0),
                "fator_chi": fracao_para_dict(comp.fator_chi),
                "nc_rd_kn": fracao_para_dict(comp.nc_rd_kn),
                "ratio_compressao": fracao_para_dict(comp.ratio_compressao),
                "atende": comp.atende,
                "modo_falha": comp.modo_falha,
            },
            "flexao": {
                "mpl_x_kn_cm": fracao_para_dict(fl.mpl_x_kn_cm),
                "mrd_x_kn_cm": fracao_para_dict(fl.mrd_x_kn_cm),
                "mrd_y_kn_cm": fracao_para_dict(fl.mrd_y_kn_cm),
                "ratio_flexao_x": fracao_para_dict(fl.ratio_flexao_x),
                "atende": fl.atende,
                "modo_falha": fl.modo_falha,
            },
            "cisalhamento": {
                "vrd_y_kn": fracao_para_dict(cis.vrd_y_kn),
                "ratio_cisalhamento": fracao_para_dict(cis.ratio_cisalhamento),
                "atende": cis.atende,
                "modo_falha": cis.modo_falha,
            },
            "flexo_compressao": {
                "ratio_combinado": fracao_para_dict(fc.ratio_combinado),
                "atende": fc.atende,
                "equacao_normativa": fc.equacao_normativa,
            },
        },
        "conformidade_geral": resultado.conformidade_geral,
        "resumo_executivo": resultado.resumo_executivo,
    }


def salvar_json_canonico(resultado: ResultadoAco, caminho_destino: str | Path) -> None:
    """Salva os resultados em arquivo JSON canônico com codificação UTF-8 sem BOM."""
    dados = resultado_para_dict(resultado)
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False, sort_keys=True)
    with open(caminho_destino, "w", encoding="utf-8") as f:
        f.write(conteudo)
        f.write("\n")
