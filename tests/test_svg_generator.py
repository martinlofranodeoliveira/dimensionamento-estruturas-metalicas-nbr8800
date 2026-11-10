# -*- coding: utf-8 -*-
"""Testes de geração de painéis vetoriais SVG de estruturas metálicas."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.calculator import dimensionar_perfil_metalico
from estruturas_metalicas_nbr8800.models import CondicoesContornoAco, SolicitacoesAco
from estruturas_metalicas_nbr8800.svg_generator import gerar_painel_svg, LARGURA_CANVAS, ALTURA_CANVAS


class TestSvgGenerator(unittest.TestCase):
    """Verifica a integridade gráfica e sintática do SVG de detalhamento."""

    def setUp(self) -> None:
        self.contorno = CondicoesContornoAco(
            kx_lx_cm=Fraction(350, 1),
            ky_ly_cm=Fraction(350, 1),
            lb_cm=Fraction(175, 1),
            cb_fator=Fraction(114, 100),
        )
        self.solicitacoes = SolicitacoesAco(
            nsd_tracao_kn=Fraction(0, 1),
            nsd_compressao_kn=Fraction(280, 1),
            msd_x_kn_cm=Fraction(4200, 1),
            msd_y_kn_cm=Fraction(350, 1),
            vsd_y_kn=Fraction(65, 1),
        )
        self.resultado = dimensionar_perfil_metalico(
            "W250x38.5", "A572_GR50", self.contorno, self.solicitacoes
        )

    def test_dimensoes_padrao_canvas(self) -> None:
        self.assertEqual(LARGURA_CANVAS, 1440)
        self.assertEqual(ALTURA_CANVAS, 900)

    def test_gerar_painel_svg_estrutura_xml(self) -> None:
        svg_str = gerar_painel_svg(self.resultado)
        self.assertIsInstance(svg_str, str)
        self.assertTrue(svg_str.startswith("<svg"))
        self.assertTrue(svg_str.strip().endswith("</svg>"))

        # Valida conformidade XML do SVG
        root = ET.fromstring(svg_str)
        self.assertEqual(root.attrib.get("viewBox"), "0 0 1440 900")
        self.assertEqual(root.attrib.get("width"), "1440")
        self.assertEqual(root.attrib.get("height"), "900")

    def test_gerar_painel_svg_contem_textos_chave(self) -> None:
        svg_str = gerar_painel_svg(self.resultado)
        self.assertIn("W250x38.5", svg_str)
        self.assertIn("A572_GR50", svg_str)
        self.assertIn("ABNT NBR 8800:2024", svg_str)
        self.assertIn("Compressão Axial", svg_str)
        self.assertIn("Flexão", svg_str)
        self.assertIn("Cisalhamento Alma", svg_str)
        self.assertIn("Interação", svg_str)


if __name__ == "__main__":
    unittest.main()
