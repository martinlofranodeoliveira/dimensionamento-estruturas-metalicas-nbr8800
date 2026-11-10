#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditor e verificador independente para dimensionamento de estruturas metálicas (ABNT NBR 8800:2024).

Execução 100% autônoma em SQLite em memória sem importar o pacote de produção,
recalculando as capacidades resistentes nominais e de cálculo (tração, compressão,
flexão, cisalhamento e flexo-compressão) diretamente a partir das equações
constitutivas fundamentais da ABNT NBR 8800:2024.
"""

from __future__ import annotations

from fractions import Fraction
import math
import sqlite3
import sys


def raiz_quadrada_racional(fracao: Fraction, precisao: int = 8) -> Fraction:
    p = fracao.numerator
    q = fracao.denominator
    fator = 10 ** (2 * precisao)
    raiz = math.isqrt(p * q * fator)
    return Fraction(raiz, q * (10 ** precisao))


def executar_auditoria_independente() -> int:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE casos_auditoria (
            id TEXT PRIMARY KEY,
            perfil TEXT NOT NULL,
            ag_cm2 TEXT NOT NULL,
            ix_cm4 TEXT NOT NULL,
            iy_cm4 TEXT NOT NULL,
            zx_cm3 TEXT NOT NULL,
            d_cm TEXT NOT NULL,
            tw_cm TEXT NOT NULL,
            fy_kn_cm2 TEXT NOT NULL,
            e_kn_cm2 TEXT NOT NULL,
            kx_lx_cm TEXT NOT NULL,
            ky_ly_cm TEXT NOT NULL,
            lb_cm TEXT NOT NULL,
            nsd_comp_kn TEXT NOT NULL,
            msd_x_kn_cm TEXT NOT NULL,
            vsd_y_kn TEXT NOT NULL
        )
    """)

    # Casos de auditoria independente
    casos = [
        (
            "Coluna_W200x31_A572",
            "W200x31.3",
            "403/10",    # Ag = 40.3 cm²
            "3129/1",    # Ix = 3129 cm4
            "410/1",     # Iy = 410 cm4
            "340/1",     # Zx = 340 cm³
            "21/1",      # d = 21.0 cm
            "16/25",     # tw = 0.64 cm
            "69/2",      # fy = 34.5 kN/cm²
            "20000/1",   # E = 20000 kN/cm²
            "300/1",     # Kx*Lx = 300 cm
            "300/1",     # Ky*Ly = 300 cm
            "300/1",     # Lb = 300 cm
            "450/1",     # Nsd,c = 450 kN
            "0/1",       # Msd,x = 0
            "0/1",       # Vsd,y = 0
        ),
        (
            "Viga_W310x32_A572",
            "W310x32.7",
            "421/10",    # Ag = 42.1 cm²
            "6507/1",    # Ix = 6507 cm4
            "195/1",     # Iy = 195 cm4
            "482/1",     # Zx = 482 cm³
            "313/10",    # d = 31.3 cm
            "33/50",     # tw = 0.66 cm
            "69/2",      # fy = 34.5 kN/cm²
            "20000/1",   # E = 20000 kN/cm²
            "500/1",     # Kx*Lx = 500 cm
            "500/1",     # Ky*Ly = 500 cm
            "150/1",     # Lb = 150 cm
            "0/1",       # Nsd,c = 0
            "6500/1",    # Msd,x = 65.0 kN.m = 6500 kN.cm
            "85/1",      # Vsd,y = 85 kN
        ),
        (
            "Viga_Coluna_W250x38_A572",
            "W250x38.5",
            "497/10",    # Ag = 49.7 cm²
            "5724/1",    # Ix = 5724 cm4
            "588/1",     # Iy = 588 cm4
            "493/1",     # Zx = 493 cm³
            "131/5",     # d = 26.2 cm
            "33/50",     # tw = 0.66 cm
            "69/2",      # fy = 34.5 kN/cm²
            "20000/1",   # E = 20000 kN/cm²
            "350/1",     # Kx*Lx = 350 cm
            "350/1",     # Ky*Ly = 350 cm
            "175/1",     # Lb = 175 cm
            "280/1",     # Nsd,c = 280 kN
            "4200/1",    # Msd,x = 42.0 kN.m = 4200 kN.cm
            "65/1",      # Vsd,y = 65 kN
        ),
    ]

    cursor.executemany("""
        INSERT INTO casos_auditoria VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, casos)
    conn.commit()

    print("=" * 80)
    print("LOFRANO TECNOLOGIA — AUDITORIA INDEPENDENTE DE ESTRUTURAS METÁLICAS NBR 8800:2024")
    print("=" * 80)

    gamma_a1 = Fraction(11, 10)
    pi2 = Fraction(98696044, 10000000)

    sucessos = 0
    total = len(casos)

    for linha in cursor.execute("SELECT * FROM casos_auditoria"):
        (
            cid, perfil, ag_s, ix_s, iy_s, zx_s, d_s, tw_s, fy_s, e_s,
            kxlx_s, kyly_s, lb_s, nsd_s, msd_s, vsd_s
        ) = linha

        ag = Fraction(ag_s)
        ix = Fraction(ix_s)
        iy = Fraction(iy_s)
        zx = Fraction(zx_s)
        d = Fraction(d_s)
        tw = Fraction(tw_s)
        fy = Fraction(fy_s)
        e = Fraction(e_s)
        kxlx = Fraction(kxlx_s)
        kyly = Fraction(kyly_s)
        lb = Fraction(lb_s)
        nsd = Fraction(nsd_s)
        msd_x = Fraction(msd_s)
        vsd_y = Fraction(vsd_s)

        # 1. Compressão axial independente
        # Euler menor inércia (eixo fraco y)
        ne_y = pi2 * e * iy / (kyly * kyly)
        q_fator = Fraction(95, 100)  # simplificado para perfis compactos/semi-compactos
        lambda_0_sq = q_fator * ag * fy / ne_y
        lambda_0 = raiz_quadrada_racional(lambda_0_sq)

        # Fator chi
        # chi = 0.658^(lambda_0^2) approx 1 - 0.418 * lambda_0^2 + ... or lookup
        l0_val = float(lambda_0)
        if l0_val <= 1.5:
            chi_val = 0.658 ** (l0_val ** 2)
        else:
            chi_val = 0.877 / (l0_val ** 2)
        chi = Fraction(int(round(chi_val * 1000000)), 1000000)

        nc_rd = chi * q_fator * ag * fy / gamma_a1
        taxa_n = nsd / nc_rd if nc_rd > 0 else Fraction(0, 1)

        # 2. Flexão simples independente
        mpl_x = zx * fy
        mrd_x = mpl_x / gamma_a1
        taxa_m = msd_x / mrd_x if mrd_x > 0 else Fraction(0, 1)

        # 3. Cisalhamento na alma independente
        aw = d * tw
        vrd_y = Fraction(6, 10) * aw * fy / gamma_a1
        taxa_v = vsd_y / vrd_y if vrd_y > 0 else Fraction(0, 1)

        # 4. Interação flexo-compressão (NBR 8800 item 5.5.1)
        if taxa_n >= Fraction(2, 10):
            ratio_comb = taxa_n + Fraction(8, 9) * taxa_m
        else:
            ratio_comb = (taxa_n / Fraction(2, 1)) + taxa_m

        assert taxa_n <= Fraction(1, 1), f"Compressão violada no caso {cid}"
        assert taxa_m <= Fraction(1, 1), f"Flexão violada no caso {cid}"
        assert taxa_v <= Fraction(1, 1), f"Cisalhamento violado no caso {cid}"
        assert ratio_comb <= Fraction(1, 1), f"Interação violada no caso {cid}"

        print(
            f"✓ Caso '{cid}' ({perfil}): "
            f"Nc,Rd={float(nc_rd):.1f} kN (Taxa N={float(taxa_n)*100:.1f}%), "
            f"MRd,x={float(mrd_x)/100:.1f} kN.m (Taxa M={float(taxa_m)*100:.1f}%), "
            f"VRd,y={float(vrd_y):.1f} kN (Taxa V={float(taxa_v)*100:.1f}%), "
            f"Interação={float(ratio_comb)*100:.1f}% <= 100% -> APROVADO"
        )
        sucessos += 1

    conn.close()
    print("-" * 80)
    print(f"Resultado da Auditoria Independente: {sucessos}/{total} casos aprovados com sucesso.")
    print("=" * 80)
    return 0 if sucessos == total else 1


if __name__ == "__main__":
    sys.exit(executar_auditoria_independente())
