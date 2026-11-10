# -*- coding: utf-8 -*-
"""Testes de integridade de empacotamento e exportação de símbolos."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import estruturas_metalicas_nbr8800


class TestPackaging(unittest.TestCase):
    """Verifica a integridade estrutural do pacote Python."""

    def test_versao_definida(self) -> None:
        self.assertEqual(estruturas_metalicas_nbr8800.__version__, "1.0.0")

    def test_simbolos_exportados_em_all(self) -> None:
        all_symbols = estruturas_metalicas_nbr8800.__all__
        self.assertIn("dimensionar_perfil_metalico", all_symbols)
        self.assertIn("obter_perfil_w", all_symbols)
        self.assertIn("obter_aco_estrutural", all_symbols)
        self.assertIn("salvar_json_canonico", all_symbols)
        self.assertIn("carregar_json_canonico", all_symbols)
        self.assertIn("exportar_relatorio_texto", all_symbols)
        self.assertIn("exportar_csv", all_symbols)
        self.assertIn("exportar_zip_deterministico", all_symbols)
        self.assertIn("gerar_painel_svg", all_symbols)

        for sym in all_symbols:
            self.assertTrue(
                hasattr(estruturas_metalicas_nbr8800, sym),
                f"Símbolo {sym} listado em __all__ mas ausente no pacote",
            )

    def test_arquivo_py_typed_presente(self) -> None:
        pkg_dir = Path(estruturas_metalicas_nbr8800.__file__).parent
        py_typed = pkg_dir / "py.typed"
        self.assertTrue(py_typed.exists(), "py.typed deve existir para suporte a PEP 561")


if __name__ == "__main__":
    unittest.main()
