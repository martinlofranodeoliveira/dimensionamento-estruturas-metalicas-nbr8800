# -*- coding: utf-8 -*-
"""Testes de exportadores (texto, CSV sanitizado e ZIP determinístico)."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.calculator import dimensionar_perfil_metalico
from estruturas_metalicas_nbr8800.exporters import (
    exportar_relatorio_texto,
    exportar_csv,
    exportar_zip_deterministico,
    sanitizar_campo_csv,
    DATA_HORA_DETERMINISTICA_ZIP,
)
from estruturas_metalicas_nbr8800.models import CondicoesContornoAco, SolicitacoesAco


class TestExporters(unittest.TestCase):
    """Verifica a geração de relatórios técnicos e integridade de exportações."""

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

    def test_exportar_relatorio_texto(self) -> None:
        relatorio = exportar_relatorio_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", relatorio)
        self.assertIn("ABNT NBR 8800:2024", relatorio)
        self.assertIn("W250x38.5", relatorio)
        self.assertIn("A572_GR50", relatorio)
        self.assertIn("PROPRIEDADES GEOMÉTRICAS", relatorio)
        self.assertIn("COMPRESSÃO AXIAL", relatorio)
        self.assertIn("FLEXÃO SIMPLES", relatorio)
        self.assertIn("INTERAÇÃO FLEXO-COMPRESSÃO", relatorio)

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+2+2"), "'+2+2")
        self.assertEqual(sanitizar_campo_csv("-3-3"), "'-3-3")
        self.assertEqual(sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(sanitizar_campo_csv("\tcmd"), "'\tcmd")
        self.assertEqual(sanitizar_campo_csv("normal"), "normal")
        self.assertEqual(sanitizar_campo_csv(123), "123")

    def test_exportar_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_csv = Path(tmpdir) / "teste.csv"
            exportar_csv(self.resultado, caminho_csv)
            self.assertTrue(caminho_csv.exists())

            linhas = caminho_csv.read_text(encoding="utf-8").splitlines()
            self.assertGreater(len(linhas), 5)
            self.assertIn("parametro;unidade;valor_numerico;status_normativo", linhas[0])
            self.assertTrue(any("perfil;" in l for l in linhas))
            self.assertTrue(any("conformidade_geral;" in l for l in linhas))

    def test_exportar_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = Path(tmpdir) / "pacote.zip"
            exportar_zip_deterministico(
                self.resultado,
                caminho_zip,
                conteudo_svg="<svg></svg>",
            )
            self.assertTrue(caminho_zip.exists())

            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_calculo.txt", nomes)
                self.assertIn("resultado_calculo.json", nomes)
                self.assertIn("resumo_dados.csv", nomes)
                self.assertIn("painel_detalhamento.svg", nomes)

                # Verifica carimbo de data/hora determinístico
                for info in zf.infolist():
                    self.assertEqual(info.date_time, DATA_HORA_DETERMINISTICA_ZIP)

    def test_exportar_zip_deterministico_nao_sobrescreve(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = Path(tmpdir) / "existente.zip"
            caminho_zip.touch()

            with self.assertRaises(FileExistsError):
                exportar_zip_deterministico(self.resultado, caminho_zip)


if __name__ == "__main__":
    unittest.main()
