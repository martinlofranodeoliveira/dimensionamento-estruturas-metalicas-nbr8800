"""Constantes e catálogo de perfis estruturais de aço segundo a ABNT NBR 8800:2024.

Todas as constantes utilizam tipos inteiros ou frações exatas (Fraction),
garantindo zero imprecisão de ponto flutuante em conformidade com o padrão LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

# Coeficientes de ponderação das resistências de cálculo (ABNT NBR 8800:2024, Tabela 1)
GAMMA_A1: Final[Fraction] = Fraction(11, 10)     # Escoamento e instabilidade/flambagem: 1.10
GAMMA_A2: Final[Fraction] = Fraction(135, 100)   # Ruptura da seção líquida: 1.35

# Propriedades mecânicas dos aços estruturais (kN/cm²) - 1 MPa = 0.1 kN/cm²
PROPRIEDADES_ACOS: Final[dict[str, dict[str, Fraction]]] = {
    "A36": {
        "f_y_kn_cm2": Fraction(25, 1),           # 250 MPa = 25.0 kN/cm²
        "f_u_kn_cm2": Fraction(40, 1),           # 400 MPa = 40.0 kN/cm²
        "e_kn_cm2": Fraction(20000, 1),         # 200.000 MPa = 20000 kN/cm²
        "g_kn_cm2": Fraction(100000, 13),       # E / [2*(1+0.3)] = 7692.307 kN/cm²
    },
    "A572_GR50": {
        "f_y_kn_cm2": Fraction(345, 10),         # 345 MPa = 34.5 kN/cm²
        "f_u_kn_cm2": Fraction(45, 1),           # 450 MPa = 45.0 kN/cm²
        "e_kn_cm2": Fraction(20000, 1),         # 200.000 MPa = 20000 kN/cm²
        "g_kn_cm2": Fraction(100000, 13),       # E / [2*(1+0.3)]
    },
}

# Constantes matemáticas racionais para flambagem de Euler (pi e pi²)
PI_FRACAO: Final[Fraction] = Fraction(314159265, 100000000)
PI2_FRACAO: Final[Fraction] = Fraction(98696044, 10000000)   # ~9.8696044

# Limites normativos de índice de esbeltez (NBR 8800:2024)
ESBELTEZ_MAXIMA_COMPRESSAO: Final[Fraction] = Fraction(200, 1)
ESBELTEZ_MAXIMA_TRACAO: Final[Fraction] = Fraction(300, 1)

# Tensão residual para perfis laminados na flexão (kN/cm²): sigma_r = 0.3 * fy para laminados
# sigma_r / fy = 0.30 -> (fy - sigma_r) = 0.70 * fy
FATOR_TENSAO_RESIDUAL_FLT: Final[Fraction] = Fraction(7, 10)

# Catálogo de Perfis Estruturais Laminados I e H Série W (dimensões em cm, cm², cm³, cm⁴, cm⁶)
# d (altura total), bf (largura da mesa), tw (espessura alma), tf (espessura mesa)
CATALOGO_PERFIS_W: Final[dict[str, dict[str, Fraction]]] = {
    "W150x13.0": {
        "d_cm": Fraction(148, 10),
        "bf_cm": Fraction(100, 10),
        "tw_cm": Fraction(43, 100),
        "tf_cm": Fraction(49, 100),
        "h_cm": Fraction(148 - 2 * 49, 10),       # d - 2*tf
        "ag_cm2": Fraction(166, 10),
        "ix_cm4": Fraction(634, 1),
        "iy_cm4": Fraction(82, 1),
        "wx_cm3": Fraction(857, 10),
        "wy_cm3": Fraction(164, 10),
        "zx_cm3": Fraction(960, 10),
        "zy_cm3": Fraction(255, 10),
        "rx_cm": Fraction(619, 100),
        "ry_cm": Fraction(222, 100),
        "j_cm4": Fraction(14, 10),
        "cw_cm6": Fraction(408, 1),
    },
    "W150x18.0": {
        "d_cm": Fraction(153, 10),
        "bf_cm": Fraction(102, 10),
        "tw_cm": Fraction(58, 100),
        "tf_cm": Fraction(71, 100),
        "h_cm": Fraction(1530 - 2 * 71, 100),
        "ag_cm2": Fraction(234, 10),
        "ix_cm4": Fraction(938, 1),
        "iy_cm4": Fraction(126, 1),
        "wx_cm3": Fraction(1226, 10),
        "wy_cm3": Fraction(247, 10),
        "zx_cm3": Fraction(1389, 10),
        "zy_cm3": Fraction(382, 10),
        "rx_cm": Fraction(633, 100),
        "ry_cm": Fraction(232, 100),
        "j_cm4": Fraction(38, 10),
        "cw_cm6": Fraction(657, 1),
    },
    "W200x15.0": {
        "d_cm": Fraction(200, 10),
        "bf_cm": Fraction(100, 10),
        "tw_cm": Fraction(43, 100),
        "tf_cm": Fraction(52, 100),
        "h_cm": Fraction(2000 - 2 * 52, 100),
        "ag_cm2": Fraction(194, 10),
        "ix_cm4": Fraction(1305, 1),
        "iy_cm4": Fraction(87, 1),
        "wx_cm3": Fraction(1305, 10),
        "wy_cm3": Fraction(174, 10),
        "zx_cm3": Fraction(1475, 10),
        "zy_cm3": Fraction(273, 10),
        "rx_cm": Fraction(820, 100),
        "ry_cm": Fraction(212, 100),
        "j_cm4": Fraction(18, 10),
        "cw_cm6": Fraction(789, 1),
    },
    "W200x22.5": {
        "d_cm": Fraction(206, 10),
        "bf_cm": Fraction(102, 10),
        "tw_cm": Fraction(62, 100),
        "tf_cm": Fraction(80, 100),
        "h_cm": Fraction(2060 - 2 * 80, 100),
        "ag_cm2": Fraction(290, 10),
        "ix_cm4": Fraction(2029, 1),
        "iy_cm4": Fraction(142, 1),
        "wx_cm3": Fraction(1970, 10),
        "wy_cm3": Fraction(278, 10),
        "zx_cm3": Fraction(2240, 10),
        "zy_cm3": Fraction(433, 10),
        "rx_cm": Fraction(837, 100),
        "ry_cm": Fraction(221, 100),
        "j_cm4": Fraction(58, 10),
        "cw_cm6": Fraction(1380, 1),
    },
    "W200x31.3": {
        "d_cm": Fraction(210, 10),
        "bf_cm": Fraction(134, 10),
        "tw_cm": Fraction(64, 100),
        "tf_cm": Fraction(102, 100),
        "h_cm": Fraction(2100 - 2 * 102, 100),
        "ag_cm2": Fraction(403, 10),
        "ix_cm4": Fraction(3168, 1),
        "iy_cm4": Fraction(410, 1),
        "wx_cm3": Fraction(3017, 10),
        "wy_cm3": Fraction(612, 10),
        "zx_cm3": Fraction(3400, 10),
        "zy_cm3": Fraction(942, 10),
        "rx_cm": Fraction(886, 100),
        "ry_cm": Fraction(319, 100),
        "j_cm4": Fraction(128, 10),
        "cw_cm6": Fraction(4150, 1),
    },
    "W250x28.4": {
        "d_cm": Fraction(260, 10),
        "bf_cm": Fraction(102, 10),
        "tw_cm": Fraction(64, 100),
        "tf_cm": Fraction(100, 100),
        "h_cm": Fraction(2600 - 2 * 100, 100),
        "ag_cm2": Fraction(370, 10),
        "ix_cm4": Fraction(4046, 1),
        "iy_cm4": Fraction(179, 1),
        "wx_cm3": Fraction(3112, 10),
        "wy_cm3": Fraction(351, 10),
        "zx_cm3": Fraction(3550, 10),
        "zy_cm3": Fraction(550, 10),
        "rx_cm": Fraction(1045, 100),
        "ry_cm": Fraction(220, 100),
        "j_cm4": Fraction(110, 10),
        "cw_cm6": Fraction(2750, 1),
    },
    "W250x38.5": {
        "d_cm": Fraction(262, 10),
        "bf_cm": Fraction(147, 10),
        "tw_cm": Fraction(66, 100),
        "tf_cm": Fraction(112, 100),
        "h_cm": Fraction(2620 - 2 * 112, 100),
        "ag_cm2": Fraction(497, 10),
        "ix_cm4": Fraction(5724, 1),
        "iy_cm4": Fraction(588, 1),
        "wx_cm3": Fraction(4369, 10),
        "wy_cm3": Fraction(800, 10),
        "zx_cm3": Fraction(4930, 10),
        "zy_cm3": Fraction(1230, 10),
        "rx_cm": Fraction(1073, 100),
        "ry_cm": Fraction(344, 100),
        "j_cm4": Fraction(187, 10),
        "cw_cm6": Fraction(8990, 1),
    },
    "W310x32.7": {
        "d_cm": Fraction(313, 10),
        "bf_cm": Fraction(102, 10),
        "tw_cm": Fraction(66, 100),
        "tf_cm": Fraction(108, 100),
        "h_cm": Fraction(3130 - 2 * 108, 100),
        "ag_cm2": Fraction(421, 10),
        "ix_cm4": Fraction(6527, 1),
        "iy_cm4": Fraction(193, 1),
        "wx_cm3": Fraction(4171, 10),
        "wy_cm3": Fraction(378, 10),
        "zx_cm3": Fraction(4820, 10),
        "zy_cm3": Fraction(600, 10),
        "rx_cm": Fraction(1245, 100),
        "ry_cm": Fraction(214, 100),
        "j_cm4": Fraction(144, 10),
        "cw_cm6": Fraction(4300, 1),
    },
    "W360x44.0": {
        "d_cm": Fraction(352, 10),
        "bf_cm": Fraction(171, 10),
        "tw_cm": Fraction(69, 100),
        "tf_cm": Fraction(98, 100),
        "h_cm": Fraction(3520 - 2 * 98, 100),
        "ag_cm2": Fraction(571, 10),
        "ix_cm4": Fraction(12140, 1),
        "iy_cm4": Fraction(819, 1),
        "wx_cm3": Fraction(6900, 10),
        "wy_cm3": Fraction(958, 10),
        "zx_cm3": Fraction(7760, 10),
        "zy_cm3": Fraction(1490, 10),
        "rx_cm": Fraction(1458, 100),
        "ry_cm": Fraction(379, 100),
        "j_cm4": Fraction(180, 10),
        "cw_cm6": Fraction(23200, 1),
    },
    "W410x53.0": {
        "d_cm": Fraction(406, 10),
        "bf_cm": Fraction(178, 10),
        "tw_cm": Fraction(76, 100),
        "tf_cm": Fraction(109, 100),
        "h_cm": Fraction(4060 - 2 * 109, 100),
        "ag_cm2": Fraction(683, 10),
        "ix_cm4": Fraction(18700, 1),
        "iy_cm4": Fraction(1030, 1),
        "wx_cm3": Fraction(9210, 10),
        "wy_cm3": Fraction(1157, 10),
        "zx_cm3": Fraction(10400, 10),
        "zy_cm3": Fraction(1800, 10),
        "rx_cm": Fraction(1655, 100),
        "ry_cm": Fraction(388, 100),
        "j_cm4": Fraction(255, 10),
        "cw_cm6": Fraction(39400, 1),
    },
}
