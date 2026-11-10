"""Modelos de dados imutáveis para dimensionamento de estruturas de aço (ABNT NBR 8800:2024).

Garante total tipagem estática e imutabilidade estrutural com frações exatas.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class AcoEstrutural:
    """Propriedades mecânicas do aço estrutural."""
    nome: str
    f_y_kn_cm2: Fraction
    f_u_kn_cm2: Fraction
    e_kn_cm2: Fraction
    g_kn_cm2: Fraction


@dataclass(frozen=True)
class PerfilPropriedades:
    """Propriedades geométricas e seccionais de um perfil I/H da série W."""
    designacao: str
    d_cm: Fraction
    bf_cm: Fraction
    tw_cm: Fraction
    tf_cm: Fraction
    h_cm: Fraction
    ag_cm2: Fraction
    ix_cm4: Fraction
    iy_cm4: Fraction
    wx_cm3: Fraction
    wy_cm3: Fraction
    zx_cm3: Fraction
    zy_cm3: Fraction
    rx_cm: Fraction
    ry_cm: Fraction
    j_cm4: Fraction
    cw_cm6: Fraction


@dataclass(frozen=True)
class CondicoesContornoAco:
    """Condições de contorno e comprimentos destravados da barra."""
    kx_lx_cm: Fraction
    ky_ly_cm: Fraction
    lb_cm: Fraction
    cb_fator: Fraction = Fraction(1, 1)


@dataclass(frozen=True)
class SolicitacoesAco:
    """Esforços solicitantes de cálculo no Estado Limite Último (ELU)."""
    nsd_tracao_kn: Fraction = Fraction(0, 1)
    nsd_compressao_kn: Fraction = Fraction(0, 1)
    msd_x_kn_cm: Fraction = Fraction(0, 1)
    msd_y_kn_cm: Fraction = Fraction(0, 1)
    vsd_y_kn: Fraction = Fraction(0, 1)


@dataclass(frozen=True)
class VerificacaoTracao:
    """Resultados da verificação de tração axial segundo a NBR 8800:2024."""
    nt_rd1_kn: Fraction                 # Escoamento da seção bruta
    nt_rd2_kn: Fraction                 # Ruptura da seção líquida efetiva
    nt_rd_kn: Fraction                  # Força resistente final
    esbeltez: Fraction
    ratio_tracao: Fraction
    atende: bool
    modo_falha: str


@dataclass(frozen=True)
class VerificacaoCompressao:
    """Resultados da verificação de compressão axial e flambagem global."""
    lambda_x: Fraction
    lambda_y: Fraction
    lambda_max: Fraction
    ne_kn: Fraction                     # Força elástica de Euler
    lambda_0: Fraction                  # Esbeltez adimensional
    fator_chi: Fraction                 # Fator de redução por flambagem
    fator_q: Fraction                   # Fator de redução por flambagem local
    nc_rd_kn: Fraction                  # Força resistente de cálculo à compressão
    ratio_compressao: Fraction
    atende: bool
    modo_falha: str


@dataclass(frozen=True)
class VerificacaoFlexao:
    """Resultados da verificação de flexão simples em torno dos eixos X e Y."""
    mpl_x_kn_cm: Fraction
    mr_x_kn_cm: Fraction
    lp_cm: Fraction
    lr_cm: Fraction
    mrd_x_kn_cm: Fraction
    mrd_y_kn_cm: Fraction
    ratio_flexao_x: Fraction
    ratio_flexao_y: Fraction
    atende: bool
    modo_falha: str


@dataclass(frozen=True)
class VerificacaoCisalhamentoAco:
    """Resultados da verificação de força cortante na alma (eixo Y)."""
    aw_cm2: Fraction
    vrd_y_kn: Fraction
    ratio_cisalhamento: Fraction
    atende: bool
    modo_falha: str


@dataclass(frozen=True)
class VerificacaoFlexoCompressao:
    """Interação entre forças axiais e momentos fletores (NBR 8800 item 5.5.1)."""
    ratio_combinado: Fraction
    atende: bool
    equacao_normativa: str


@dataclass(frozen=True)
class ResultadoAco:
    """Consolidação técnica do dimensionamento estrutural do perfil metálico."""
    perfil: PerfilPropriedades
    aco: AcoEstrutural
    solicitacoes: SolicitacoesAco
    contorno: CondicoesContornoAco
    tracao: VerificacaoTracao
    compressao: VerificacaoCompressao
    flexao: VerificacaoFlexao
    cisalhamento: VerificacaoCisalhamentoAco
    flexo_compressao: VerificacaoFlexoCompressao
    conformidade_geral: bool
    resumo_executivo: str
