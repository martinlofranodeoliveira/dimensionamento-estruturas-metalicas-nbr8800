# -*- coding: utf-8 -*-
"""Testes de codecs e serialização JSON canônica sem float."""

from __future__ import annotations

from fractions import Fraction
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from estruturas_metalicas_nbr8800.calculator import dimensionar_perfil_metalico
from estruturas_metalicas_nbr8800.codecs import (
    salvar_json_canonico,
    carregar_json_canonico,
    resultado_para_dict,
    entrada_de_dict,
    fracao_para_dict,
    parsear_fracao,
    PROFUNDIDADE_MAXIMA_JSON,
)
from estruturas_metalicas_nbr8800.models import CondicoesContornoAco, SolicitacoesAco


class TestCodecs(unittest.TestCase):
    """Verifica a integridade dos codecs canônicos e proteções de entrada."""

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

    def test_fracao_para_dict_e_parsear(self) -> None:
        f = Fraction(355, 113)
        d = fracao_para_dict(f)
        self.assertEqual(d["numerador"], 355)
        self.assertEqual(d["denominador"], 113)
        self.assertEqual(d["valor_decimal"], "3.141593")

        recup = parsear_fracao(d)
        self.assertEqual(recup, f)

    def test_parsear_fracao_tipos(self) -> None:
        self.assertEqual(parsear_fracao(10), Fraction(10, 1))
        self.assertEqual(parsear_fracao("3/4"), Fraction(3, 4))
        self.assertEqual(parsear_fracao("2.5"), Fraction(5, 2))
        self.assertEqual(parsear_fracao(Fraction(7, 2)), Fraction(7, 2))

    def test_salvar_e_carregar_json_canonico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = Path(tmpdir) / "resultado.json"
            salvar_json_canonico(self.resultado, caminho)
            self.assertTrue(caminho.exists())

            carregado = carregar_json_canonico(caminho)
            self.assertEqual(carregado["perfil"]["designacao"], "W250x38.5")
            self.assertEqual(carregado["aco"]["nome"], "A572_GR50")
            self.assertTrue(carregado["conformidade_geral"])

    def test_rejeicao_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = Path(tmpdir) / "com_bom.json"
            conteudo = b"\xef\xbb\xbf{\"perfil\": \"W200x31.3\"}"
            with open(caminho, "wb") as f:
                f.write(conteudo)

            with self.assertRaises(ValueError) as ctx:
                carregar_json_canonico(caminho)
            self.assertIn("BOM", str(ctx.exception))

    def test_rejeicao_chaves_duplicadas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = Path(tmpdir) / "dup.json"
            conteudo = '{"perfil": "W200x31.3", "perfil": "W250x38.5"}'
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(conteudo)

            with self.assertRaises(ValueError) as ctx:
                carregar_json_canonico(caminho)
            self.assertIn("Chave duplicada", str(ctx.exception))

    def test_rejeicao_profundidade_excessiva(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = Path(tmpdir) / "profundo.json"
            dados: dict = {}
            atual = dados
            for _ in range(PROFUNDIDADE_MAXIMA_JSON + 5):
                novo: dict = {}
                atual["sub"] = novo
                atual = novo
            atual["final"] = 1

            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f)

            with self.assertRaises(ValueError) as ctx:
                carregar_json_canonico(caminho)
            self.assertIn("Profundidade", str(ctx.exception))

    def test_entrada_de_dict_reconstitui_objetos(self) -> None:
        dados = {
            "perfil": "W150x18.0",
            "aco": "A36",
            "contorno": {
                "kx_lx_cm": "250",
                "ky_ly_cm": "250",
                "lb_cm": "250",
                "cb_fator": "1",
            },
            "solicitacoes": {
                "nsd_tracao_kn": "200",
                "nsd_compressao_kn": "0",
                "msd_x_kn_cm": "0",
                "msd_y_kn_cm": "0",
                "vsd_y_kn": "0",
            },
        }
        perfil, aco, cont, sol = entrada_de_dict(dados)
        self.assertEqual(perfil, "W150x18.0")
        self.assertEqual(aco, "A36")
        self.assertEqual(cont.kx_lx_cm, Fraction(250, 1))
        self.assertEqual(sol.nsd_tracao_kn, Fraction(200, 1))


if __name__ == "__main__":
    unittest.main()
