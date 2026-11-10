# -*- coding: utf-8 -*-
"""Testes de constantes, coeficientes normativos e catálogo de perfis de aço."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.constants import (
    CATALOGO_PERFIS_W,
    PROPRIEDADES_ACOS,
    GAMMA_A1,
    GAMMA_A2,
    ESBELTEZ_MAXIMA_TRACAO,
    ESBELTEZ_MAXIMA_COMPRESSAO,
    PI_FRACAO,
    PI2_FRACAO,
    FATOR_TENSAO_RESIDUAL_FLT,
)


class TestConstants(unittest.TestCase):
    """Verifica a integridade e precisão das constantes da NBR 8800:2024."""

    def test_coeficientes_ponderacao_resistencia(self) -> None:
        self.assertEqual(GAMMA_A1, Fraction(11, 10))
        self.assertEqual(GAMMA_A2, Fraction(135, 100))

    def test_limites_normativos_esbeltez(self) -> None:
        self.assertEqual(ESBELTEZ_MAXIMA_TRACAO, Fraction(300, 1))
        self.assertEqual(ESBELTEZ_MAXIMA_COMPRESSAO, Fraction(200, 1))

    def test_constantes_pi(self) -> None:
        self.assertIsInstance(PI_FRACAO, Fraction)
        self.assertIsInstance(PI2_FRACAO, Fraction)
        self.assertAlmostEqual(float(PI_FRACAO), 3.14159265, places=6)
        self.assertAlmostEqual(float(PI2_FRACAO), 9.8696044, places=5)

    def test_fator_tensao_residual(self) -> None:
        self.assertEqual(FATOR_TENSAO_RESIDUAL_FLT, Fraction(7, 10))

    def test_catalogo_perfis_w_contem_itens_essenciais(self) -> None:
        perfis_esperados = [
            "W150x13.0",
            "W150x18.0",
            "W200x15.0",
            "W200x22.5",
            "W200x31.3",
            "W250x28.4",
            "W250x38.5",
            "W310x32.7",
            "W360x44.0",
            "W410x53.0",
        ]
        for p in perfis_esperados:
            self.assertIn(p, CATALOGO_PERFIS_W)

    def test_propriedades_perfis_sao_fracoes_positivas(self) -> None:
        campos = [
            "d_cm", "bf_cm", "tw_cm", "tf_cm", "h_cm", "ag_cm2",
            "ix_cm4", "iy_cm4", "wx_cm3", "wy_cm3", "zx_cm3", "zy_cm3",
            "rx_cm", "ry_cm", "j_cm4", "cw_cm6"
        ]
        for desig, dados in CATALOGO_PERFIS_W.items():
            for c in campos:
                self.assertIn(c, dados, f"Campo {c} ausente no perfil {desig}")
                val = dados[c]
                self.assertIsInstance(val, Fraction, f"Campo {c} em {desig} não é Fraction")
                self.assertGreater(val, Fraction(0, 1), f"Campo {c} em {desig} não é positivo")

    def test_acos_estruturais_disponiveis(self) -> None:
        self.assertIn("A36", PROPRIEDADES_ACOS)
        self.assertIn("A572_GR50", PROPRIEDADES_ACOS)

        a36 = PROPRIEDADES_ACOS["A36"]
        self.assertEqual(a36["f_y_kn_cm2"], Fraction(25, 1))
        self.assertEqual(a36["f_u_kn_cm2"], Fraction(40, 1))
        self.assertEqual(a36["e_kn_cm2"], Fraction(20000, 1))

        a572 = PROPRIEDADES_ACOS["A572_GR50"]
        self.assertEqual(a572["f_y_kn_cm2"], Fraction(69, 2))  # 34.5 kN/cm²
        self.assertEqual(a572["f_u_kn_cm2"], Fraction(45, 1))  # 45.0 kN/cm²
        self.assertEqual(a572["e_kn_cm2"], Fraction(20000, 1))


if __name__ == "__main__":
    unittest.main()
