# -*- coding: utf-8 -*-
"""Pacote dimensionamento-estruturas-metalicas-nbr8800.

Dimensionamento analítico rigoroso de perfis estruturais de aço segundo a
ABNT NBR 8800:2024 utilizando aritmética racional exata (frações inteiras)
e biblioteca padrão do Python.
"""

from __future__ import annotations

from .constants import (
    CATALOGO_PERFIS_W,
    PROPRIEDADES_ACOS,
    GAMMA_A1,
    GAMMA_A2,
    ESBELTEZ_MAXIMA_TRACAO,
    ESBELTEZ_MAXIMA_COMPRESSAO,
)
from .models import (
    AcoEstrutural,
    PerfilPropriedades,
    CondicoesContornoAco,
    SolicitacoesAco,
    VerificacaoTracao,
    VerificacaoCompressao,
    VerificacaoFlexao,
    VerificacaoCisalhamentoAco,
    VerificacaoFlexoCompressao,
    ResultadoAco,
)
from .calculator import (
    obter_aco_estrutural,
    obter_perfil_w,
    dimensionar_perfil_metalico,
    verificar_tracao_axial,
    verificar_compressao_axial,
    verificar_flexao_simples,
    verificar_cisalhamento,
    verificar_flexo_compressao,
    raiz_quadrada_fracao,
    calcular_fator_reducao_flambagem_chi,
)
from .codecs import (
    salvar_json_canonico,
    carregar_json_canonico,
    resultado_para_dict,
    entrada_de_dict,
)
from .exporters import (
    exportar_relatorio_texto,
    exportar_csv,
    exportar_zip_deterministico,
)
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"
__author__ = "Lofrano Tecnologia"
__license__ = "MIT"

__all__ = [
    "__version__",
    "CATALOGO_PERFIS_W",
    "PROPRIEDADES_ACOS",
    "GAMMA_A1",
    "GAMMA_A2",
    "ESBELTEZ_MAXIMA_TRACAO",
    "ESBELTEZ_MAXIMA_COMPRESSAO",
    "AcoEstrutural",
    "PerfilPropriedades",
    "CondicoesContornoAco",
    "SolicitacoesAco",
    "VerificacaoTracao",
    "VerificacaoCompressao",
    "VerificacaoFlexao",
    "VerificacaoCisalhamentoAco",
    "VerificacaoFlexoCompressao",
    "ResultadoAco",
    "obter_aco_estrutural",
    "obter_perfil_w",
    "dimensionar_perfil_metalico",
    "verificar_tracao_axial",
    "verificar_compressao_axial",
    "verificar_flexao_simples",
    "verificar_cisalhamento",
    "verificar_flexo_compressao",
    "raiz_quadrada_fracao",
    "calcular_fator_reducao_flambagem_chi",
    "salvar_json_canonico",
    "carregar_json_canonico",
    "resultado_para_dict",
    "entrada_de_dict",
    "exportar_relatorio_texto",
    "exportar_csv",
    "exportar_zip_deterministico",
    "gerar_painel_svg",
]
