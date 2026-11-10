# -*- coding: utf-8 -*-
"""Testes de modelos imutáveis de estruturas metálicas."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.models import (
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


class TestModels(unittest.TestCase):
    """Testa a integridade, imutabilidade e tipagem dos modelos de dados."""

    def setUp(self) -> None:
        self.aco = AcoEstrutural(
            nome="A36",
            f_y_kn_cm2=Fraction(25, 1),
            f_u_kn_cm2=Fraction(40, 1),
            e_kn_cm2=Fraction(20000, 1),
            g_kn_cm2=Fraction(7692, 1),
        )
        self.perfil = PerfilPropriedades(
            designacao="W150x13.0",
            d_cm=Fraction(74, 5),
            bf_cm=Fraction(10, 1),
            tw_cm=Fraction(43, 100),
            tf_cm=Fraction(49, 100),
            h_cm=Fraction(5, 1),
            ag_cm2=Fraction(83, 5),
            ix_cm4=Fraction(634, 1),
            iy_cm4=Fraction(82, 1),
            wx_cm3=Fraction(857, 10),
            wy_cm3=Fraction(82, 5),
            zx_cm3=Fraction(96, 1),
            zy_cm3=Fraction(51, 2),
            rx_cm=Fraction(619, 100),
            ry_cm=Fraction(111, 50),
            j_cm4=Fraction(7, 5),
            cw_cm6=Fraction(408, 1),
        )
        self.contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(300, 1),
            ky_ly_cm=Fraction(300, 1),
            lb_cm=Fraction(150, 1),
            cb_fator=Fraction(1, 1),
        )
        self.solicitacoes = SolicitacoesAco(
            nsd_tracao_kn=Fraction(0, 1),
            nsd_compressao_kn=Fraction(100, 1),
            msd_x_kn_cm=Fraction(1000, 1),
            msd_y_kn_cm=Fraction(0, 1),
            vsd_y_kn=Fraction(20, 1),
        )

    def test_imutabilidade_aco(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.aco.nome = "Outro"  # type: ignore

    def test_imutabilidade_perfil(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.perfil.d_cm = Fraction(20, 1)  # type: ignore

    def test_imutabilidade_contorno(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.contorno.kx_lx_cm = Fraction(500, 1)  # type: ignore

    def test_imutabilidade_solicitacoes(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.solicitacoes.nsd_compressao_kn = Fraction(200, 1)  # type: ignore

    def test_instanciacao_verificacoes(self) -> None:
        v_tracao = VerificacaoTracao(
            nt_rd1_kn=Fraction(350, 1),
            nt_rd2_kn=Fraction(300, 1),
            nt_rd_kn=Fraction(300, 1),
            ratio_tracao=Fraction(0, 1),
            esbeltez=Fraction(50, 1),
            atende=True,
            modo_falha="Escoamento",
        )
        self.assertTrue(v_tracao.atende)
        self.assertEqual(v_tracao.nt_rd_kn, Fraction(300, 1))

        v_comp = VerificacaoCompressao(
            lambda_x=Fraction(30, 1),
            lambda_y=Fraction(80, 1),
            lambda_max=Fraction(80, 1),
            ne_kn=Fraction(1000, 1),
            lambda_0=Fraction(12, 10),
            fator_chi=Fraction(5, 10),
            fator_q=Fraction(1, 1),
            nc_rd_kn=Fraction(250, 1),
            ratio_compressao=Fraction(4, 10),
            atende=True,
            modo_falha="OK",
        )
        self.assertTrue(v_comp.atende)

        v_flex = VerificacaoFlexao(
            mpl_x_kn_cm=Fraction(2500, 1),
            mr_x_kn_cm=Fraction(2000, 1),
            lp_cm=Fraction(100, 1),
            lr_cm=Fraction(300, 1),
            mrd_x_kn_cm=Fraction(2000, 1),
            mrd_y_kn_cm=Fraction(500, 1),
            ratio_flexao_x=Fraction(5, 10),
            ratio_flexao_y=Fraction(0, 1),
            atende=True,
            modo_falha="Plastificação",
        )
        self.assertTrue(v_flex.atende)

        v_cis = VerificacaoCisalhamentoAco(
            aw_cm2=Fraction(15, 1),
            vrd_y_kn=Fraction(150, 1),
            ratio_cisalhamento=Fraction(2, 15),
            atende=True,
            modo_falha="Escoamento plástico",
        )
        self.assertTrue(v_cis.atende)

        v_fc = VerificacaoFlexoCompressao(
            ratio_combinado=Fraction(7, 10),
            equacao_normativa="Item 5.5.1",
            atende=True,
        )
        self.assertTrue(v_fc.atende)


if __name__ == "__main__":
    unittest.main()
