# -*- coding: utf-8 -*-
"""Testes de cálculos analíticos exatos e verificações da ABNT NBR 8800:2024."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.calculator import (
    raiz_quadrada_fracao,
    calcular_fator_reducao_flambagem_chi,
    obter_aco_estrutural,
    obter_perfil_w,
    verificar_tracao_axial,
    verificar_compressao_axial,
    verificar_flexao_simples,
    verificar_cisalhamento,
    verificar_flexo_compressao,
    dimensionar_perfil_metalico,
)
from estruturas_metalicas_nbr8800.models import CondicoesContornoAco, SolicitacoesAco


class TestCalculator(unittest.TestCase):
    """Testa rigorosamente as equações constitutivas e formulações normativas."""

    def setUp(self) -> None:
        self.aco_a572 = obter_aco_estrutural("A572_GR50")
        self.aco_a36 = obter_aco_estrutural("A36")
        self.perfil_w200 = obter_perfil_w("W200x31.3")
        self.perfil_w250 = obter_perfil_w("W250x38.5")
        self.perfil_w310 = obter_perfil_w("W310x32.7")

    def test_raiz_quadrada_fracao_quadrados_perfeitos(self) -> None:
        self.assertEqual(raiz_quadrada_fracao(Fraction(4, 1)), Fraction(2, 1))
        self.assertEqual(raiz_quadrada_fracao(Fraction(9, 16)), Fraction(3, 4))
        self.assertEqual(raiz_quadrada_fracao(Fraction(0, 1)), Fraction(0, 1))
        self.assertEqual(raiz_quadrada_fracao(Fraction(1, 100)), Fraction(1, 10))

    def test_raiz_quadrada_fracao_aproximacoes_racionais(self) -> None:
        r2 = raiz_quadrada_fracao(Fraction(2, 1), precisao_decimais=6)
        self.assertAlmostEqual(float(r2), 1.41421356, places=5)
        self.assertEqual(r2.denominator, 1000000)

    def test_raiz_quadrada_fracao_negativa_levanta_erro(self) -> None:
        with self.assertRaises(ValueError):
            raiz_quadrada_fracao(Fraction(-1, 1))

    def test_fator_chi_flambagem_anelastica(self) -> None:
        # lambda_0 <= 1.5
        chi = calcular_fator_reducao_flambagem_chi(Fraction(1, 1))
        # chi = 0.658^(1^2) = 0.658
        self.assertAlmostEqual(float(chi), 0.658, places=2)

    def test_fator_chi_flambagem_elastica(self) -> None:
        # lambda_0 > 1.5
        chi = calcular_fator_reducao_flambagem_chi(Fraction(2, 1))
        # chi = 0.877 / 2^2 = 0.877 / 4 = 0.21925
        self.assertAlmostEqual(float(chi), 0.21925, places=3)

    def test_verificar_tracao_axial_conforme(self) -> None:
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(200, 1),
            ky_ly_cm=Fraction(200, 1),
            lb_cm=Fraction(200, 1),
            cb_fator=Fraction(1, 1),
        )
        res = verificar_tracao_axial(self.perfil_w200, self.aco_a572, contorno, nsd_kn=Fraction(300, 1))
        self.assertTrue(res.atende)
        self.assertGreater(res.nt_rd_kn, Fraction(300, 1))
        self.assertLess(res.esbeltez, Fraction(300, 1))

    def test_verificar_tracao_axial_esbeltez_excessiva(self) -> None:
        contorno_longo = CondicoesContornoAco(
            kx_lx_cm=Fraction(2000, 1),
            ky_ly_cm=Fraction(2000, 1),
            lb_cm=Fraction(2000, 1),
            cb_fator=Fraction(1, 1),
        )
        res = verificar_tracao_axial(self.perfil_w200, self.aco_a572, contorno_longo, nsd_kn=Fraction(50, 1))
        self.assertFalse(res.atende)
        self.assertIn("Esbeltez de tração", res.modo_falha)

    def test_verificar_compressao_axial_conforme(self) -> None:
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(300, 1),
            ky_ly_cm=Fraction(300, 1),
            lb_cm=Fraction(300, 1),
            cb_fator=Fraction(1, 1),
        )
        res = verificar_compressao_axial(self.perfil_w200, self.aco_a572, contorno, nsd_kn=Fraction(400, 1))
        self.assertTrue(res.atende)
        self.assertLessEqual(res.lambda_max, Fraction(200, 1))
        self.assertGreater(res.nc_rd_kn, Fraction(400, 1))

    def test_verificar_compressao_axial_esbeltez_acima_limite(self) -> None:
        contorno_excessivo = CondicoesContornoAco(
            kx_lx_cm=Fraction(1200, 1),
            ky_ly_cm=Fraction(1200, 1),
            lb_cm=Fraction(1200, 1),
            cb_fator=Fraction(1, 1),
        )
        res = verificar_compressao_axial(self.perfil_w200, self.aco_a572, contorno_excessivo, nsd_kn=Fraction(10, 1))
        self.assertFalse(res.atende)
        self.assertIn("Esbeltez de compressão", res.modo_falha)

    def test_verificar_flexao_simples_plastificacao(self) -> None:
        # Lb curto -> plastificação integral
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(300, 1),
            ky_ly_cm=Fraction(300, 1),
            lb_cm=Fraction(50, 1),  # Lb bem curto <= Lp
            cb_fator=Fraction(1, 1),
        )
        res = verificar_flexao_simples(
            self.perfil_w310, self.aco_a572, contorno,
            msd_x_kn_cm=Fraction(5000, 1), msd_y_kn_cm=Fraction(0, 1)
        )
        self.assertTrue(res.atende)
        self.assertIn("Plastificação", res.modo_falha)

    def test_verificar_flexao_simples_flt_inelas(self) -> None:
        # Lb intermediário entre Lp e Lr
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(400, 1),
            ky_ly_cm=Fraction(400, 1),
            lb_cm=Fraction(250, 1),
            cb_fator=Fraction(1, 1),
        )
        res = verificar_flexao_simples(
            self.perfil_w310, self.aco_a572, contorno,
            msd_x_kn_cm=Fraction(4000, 1), msd_y_kn_cm=Fraction(0, 1)
        )
        self.assertTrue(res.atende)
        self.assertIn("Flambagem lateral", res.modo_falha)

    def test_verificar_cisalhamento_conforme(self) -> None:
        res = verificar_cisalhamento(self.perfil_w250, self.aco_a572, vsd_y_kn=Fraction(50, 1))
        self.assertTrue(res.atende)
        self.assertGreater(res.vrd_y_kn, Fraction(50, 1))
        self.assertIn("Escoamento por cisalhamento", res.modo_falha)

    def test_verificar_cisalhamento_excedente(self) -> None:
        res = verificar_cisalhamento(self.perfil_w250, self.aco_a572, vsd_y_kn=Fraction(500, 1))
        self.assertFalse(res.atende)

    def test_verificar_flexo_compressao_item_5_5_1(self) -> None:
        solicitacoes = SolicitacoesAco(
            nsd_tracao_kn=Fraction(0, 1),
            nsd_compressao_kn=Fraction(200, 1),
            msd_x_kn_cm=Fraction(3000, 1),
            msd_y_kn_cm=Fraction(200, 1),
            vsd_y_kn=Fraction(40, 1),
        )
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(300, 1),
            ky_ly_cm=Fraction(300, 1),
            lb_cm=Fraction(150, 1),
            cb_fator=Fraction(1, 1),
        )
        comp = verificar_compressao_axial(self.perfil_w250, self.aco_a572, contorno, solicitacoes.nsd_compressao_kn)
        flex = verificar_flexao_simples(self.perfil_w250, self.aco_a572, contorno, solicitacoes.msd_x_kn_cm, solicitacoes.msd_y_kn_cm)

        fc = verificar_flexo_compressao(solicitacoes, comp, flex)
        self.assertTrue(fc.atende)
        self.assertLessEqual(fc.ratio_combinado, Fraction(1, 1))
        self.assertIn("N_sd/N_c,Rd", fc.equacao_normativa)

    def test_dimensionar_perfil_metalico_completo(self) -> None:
        contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(350, 1),
            ky_ly_cm=Fraction(350, 1),
            lb_cm=Fraction(175, 1),
            cb_fator=Fraction(114, 100),
        )
        solicitacoes = SolicitacoesAco(
            nsd_tracao_kn=Fraction(0, 1),
            nsd_compressao_kn=Fraction(280, 1),
            msd_x_kn_cm=Fraction(4200, 1),
            msd_y_kn_cm=Fraction(350, 1),
            vsd_y_kn=Fraction(65, 1),
        )
        resultado = dimensionar_perfil_metalico("W250x38.5", "A572_GR50", contorno, solicitacoes)
        self.assertTrue(resultado.conformidade_geral)
        self.assertIn("CONFORME COM ABNT NBR 8800:2024", resultado.resumo_executivo)
        self.assertEqual(resultado.perfil.designacao, "W250x38.5")
        self.assertEqual(resultado.aco.nome, "A572_GR50")


if __name__ == "__main__":
    unittest.main()
