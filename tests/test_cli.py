# -*- coding: utf-8 -*-
"""Testes da interface de linha de comando (CLI) de estruturas metálicas."""

from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.cli import main


class TestCli(unittest.TestCase):
    """Verifica todos os comandos, argumentos, formatos de exportação e códigos de saída da CLI."""

    def test_ajuda_sem_argumentos(self) -> None:
        with patch("sys.stdout", new=io.StringIO()):
            ret = main([])
            self.assertEqual(ret, 0)

    def test_versao(self) -> None:
        with patch("sys.stdout", new=io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--version"])
            self.assertEqual(ctx.exception.code, 0)

    def test_catalogo_perfis(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", new=buf):
            ret = main(["catalogo", "--tipo", "perfis"])
            self.assertEqual(ret, 0)
        saida = buf.getvalue()
        self.assertIn("CATÁLOGO DE PERFIS LAMINADOS W", saida)
        self.assertIn("W200x31.3", saida)

    def test_catalogo_acos(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", new=buf):
            ret = main(["catalogo", "--tipo", "acos"])
            self.assertEqual(ret, 0)
        saida = buf.getvalue()
        self.assertIn("AÇOS ESTRUTURAIS DISPONÍVEIS", saida)
        self.assertIn("A572_GR50", saida)

    def test_catalogo_todos(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", new=buf):
            ret = main(["catalogo", "--tipo", "todos"])
            self.assertEqual(ret, 0)
        saida = buf.getvalue()
        self.assertIn("CATÁLOGO DE PERFIS LAMINADOS W", saida)
        self.assertIn("AÇOS ESTRUTURAIS DISPONÍVEIS", saida)

    def test_gerar_exemplo_tipos(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for tipo in ["combinada", "compressao", "flexao", "tracao"]:
                caminho = Path(tmpdir) / f"exemplo_{tipo}.json"
                with patch("sys.stdout", new=io.StringIO()):
                    ret = main(["gerar-exemplo", "--tipo", tipo, "-o", str(caminho)])
                    self.assertEqual(ret, 0)
                self.assertTrue(caminho.exists())

    def test_verificar_arquivo_conforme(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = Path(tmpdir) / "exemplo.json"
            main(["gerar-exemplo", "-o", str(caminho)])

            buf = io.StringIO()
            with patch("sys.stdout", new=buf):
                ret = main(["verificar", str(caminho)])
                self.assertEqual(ret, 0)
            self.assertIn("[CONFORME]", buf.getvalue())

    def test_verificar_arquivo_inexistente(self) -> None:
        with patch("sys.stderr", new=io.StringIO()):
            ret = main(["verificar", "/caminho/inexistente/invalido.json"])
            self.assertEqual(ret, 1)

    def test_calcular_formatos_saida(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_in = Path(tmpdir) / "in.json"
            main(["gerar-exemplo", "-o", str(caminho_in)])

            # Formato texto no stdout
            buf = io.StringIO()
            with patch("sys.stdout", new=buf):
                ret = main(["calcular", str(caminho_in), "-f", "texto"])
                self.assertEqual(ret, 0)
            self.assertIn("LOFRANO TECNOLOGIA", buf.getvalue())

            # Formato texto para arquivo
            caminho_txt = Path(tmpdir) / "relatorio.txt"
            ret = main(["calcular", str(caminho_in), "-f", "texto", "-o", str(caminho_txt)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_txt.exists())

            # Formato json para arquivo
            caminho_json = Path(tmpdir) / "res.json"
            ret = main(["calcular", str(caminho_in), "-f", "json", "-o", str(caminho_json)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_json.exists())

            # Formato csv para arquivo
            caminho_csv = Path(tmpdir) / "res.csv"
            ret = main(["calcular", str(caminho_in), "-f", "csv", "-o", str(caminho_csv)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_csv.exists())

            # Formato svg para arquivo
            caminho_svg = Path(tmpdir) / "painel.svg"
            ret = main(["calcular", str(caminho_in), "-f", "svg", "-o", str(caminho_svg)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_svg.exists())

            # Formato zip para arquivo
            caminho_zip = Path(tmpdir) / "pacote.zip"
            ret = main(["calcular", str(caminho_in), "-f", "zip", "-o", str(caminho_zip)])
            self.assertEqual(ret, 0)
            self.assertTrue(caminho_zip.exists())


if __name__ == "__main__":
    unittest.main()
