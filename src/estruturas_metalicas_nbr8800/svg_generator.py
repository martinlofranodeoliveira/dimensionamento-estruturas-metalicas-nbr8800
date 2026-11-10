"""Gerador de painel técnico visual em SVG (1440x900) para perfis de aço estrutural.

Gera diagramas vetoriais nítidos em alta resolução com a seção transversal I detalhada,
cotas geométricas, curvas de flambagem e indicadores de conformidade com a ABNT NBR 8800:2024.
"""

from __future__ import annotations

from html import escape
from typing import Final

from .models import ResultadoAco

LARGURA_CANVAS: Final[int] = 1440
ALTURA_CANVAS: Final[int] = 900


def gerar_painel_svg(resultado: ResultadoAco) -> str:
    """Gera o painel técnico vetorial SVG 1440x900 do perfil de aço dimensionado."""
    p = resultado.perfil
    a = resultado.aco
    s = resultado.solicitacoes
    comp = resultado.compressao
    fl = resultado.flexao
    cis = resultado.cisalhamento
    fc = resultado.flexo_compressao

    status_cor = "#10b981" if resultado.conformidade_geral else "#ef4444"
    status_texto = "CONFORME NBR 8800:2024" if resultado.conformidade_geral else "NÃO CONFORME"

    # Escalar a seção transversal I para caber numa caixa de 380 x 360 px
    d_f = float(p.d_cm)
    bf_f = float(p.bf_cm)
    tf_f = float(p.tf_cm)
    tw_f = float(p.tw_cm)

    escala = min(300.0 / d_f, 280.0 / bf_f)
    d_px = d_f * escala
    bf_px = bf_f * escala
    tf_px = max(tf_f * escala, 8.0)
    tw_px = max(tw_f * escala, 6.0)

    centro_x = 320.0
    centro_y = 360.0

    # Coordenadas da seção I
    topo_mesa_sup = centro_y - d_px / 2.0
    base_mesa_sup = topo_mesa_sup + tf_px
    topo_mesa_inf = centro_y + d_px / 2.0 - tf_px
    base_mesa_inf = centro_y + d_px / 2.0

    esq_mesa = centro_x - bf_px / 2.0
    dir_mesa = centro_x + bf_px / 2.0
    esq_alma = centro_x - tw_px / 2.0
    dir_alma = centro_x + tw_px / 2.0

    svg_linhas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA_CANVAS} {ALTURA_CANVAS}" width="{LARGURA_CANVAS}" height="{ALTURA_CANVAS}">',
        '  <defs>',
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#090d16" />',
        '      <stop offset="100%" stop-color="#111827" />',
        '    </linearGradient>',
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1f2937" />',
        '      <stop offset="100%" stop-color="#374151" />',
        '    </linearGradient>',
        '    <linearGradient id="steelGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.3" />',
        '      <stop offset="100%" stop-color="#2563eb" stop-opacity="0.6" />',
        '    </linearGradient>',
        '    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">',
        '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5" />',
        '    </filter>',
        '  </defs>',
        '',
        '  <!-- Fundo Principal -->',
        f'  <rect width="{LARGURA_CANVAS}" height="{ALTURA_CANVAS}" fill="url(#bgGrad)" />',
        '',
        '  <!-- Cabeçalho Técnico -->',
        '  <rect x="30" y="25" width="1380" height="95" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="65" font-family="system-ui, -apple-system, sans-serif" font-size="24" font-weight="700" fill="#f8fafc">LOFRANO TECNOLOGIA</text>',
        '  <text x="55" y="95" font-family="system-ui, -apple-system, sans-serif" font-size="14" fill="#94a3b8">DIMENSIONAMENTO DE ESTRUTURAS METÁLICAS E PERFIS DE AÇO · ABNT NBR 8800:2024</text>',
        '',
        f'  <!-- Selo de Conformidade Geral -->',
        f'  <rect x="1080" y="42" width="300" height="60" rx="8" fill="{status_cor}" fill-opacity="0.2" stroke="{status_cor}" stroke-width="2" />',
        f'  <circle cx="1115" cy="72" r="12" fill="{status_cor}" />',
        f'  <text x="1140" y="78" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="700" fill="{status_cor}">{status_texto}</text>',
        '',
        '  <!-- Painel 1: Seção Transversal e Geometria do Perfil -->',
        '  <rect x="30" y="140" width="580" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">1. Seção Transversal do Perfil I</text>',
        f'  <text x="55" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">Perfil {escape(p.designacao)} · Aço {escape(a.nome)} · Ag = {float(p.ag_cm2):.1f} cm²</text>',
        '',
        '  <!-- Mesa Superior -->',
        f'  <rect x="{esq_mesa}" y="{topo_mesa_sup}" width="{bf_px}" height="{tf_px}" rx="2" fill="url(#steelGrad)" stroke="#60a5fa" stroke-width="2" />',
        '  <!-- Alma -->',
        f'  <rect x="{esq_alma}" y="{base_mesa_sup}" width="{tw_px}" height="{topo_mesa_inf - base_mesa_sup}" fill="url(#steelGrad)" stroke="#60a5fa" stroke-width="2" />',
        '  <!-- Mesa Inferior -->',
        f'  <rect x="{esq_mesa}" y="{topo_mesa_inf}" width="{bf_px}" height="{tf_px}" rx="2" fill="url(#steelGrad)" stroke="#60a5fa" stroke-width="2" />',
        '',
        '  <!-- Eixos Principais Centrais -->',
        f'  <line x1="{centro_x - 170}" y1="{centro_y}" x2="{centro_x + 170}" y2="{centro_y}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="6,4" />',
        f'  <text x="{centro_x + 175}" y="{centro_y + 4}" font-family="monospace" font-size="12" fill="#ef4444">Eixo X (Forte)</text>',
        f'  <line x1="{centro_x}" y1="{centro_y - 170}" x2="{centro_x}" y2="{centro_y + 170}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="6,4" />',
        f'  <text x="{centro_x}" y="{centro_y - 175}" font-family="monospace" font-size="12" fill="#10b981" text-anchor="middle">Eixo Y (Fraco)</text>',
        '',
        '  <!-- Cotas Geométricas -->',
        f'  <text x="{centro_x}" y="{topo_mesa_sup - 12}" font-family="monospace" font-size="12" font-weight="700" fill="#38bdf8" text-anchor="middle">bf = {bf_f:.1f} cm (tf = {tf_f:.2f} cm)</text>',
        f'  <text x="{esq_mesa - 20}" y="{centro_y}" font-family="monospace" font-size="12" font-weight="700" fill="#38bdf8" text-anchor="middle" transform="rotate(-90, {esq_mesa - 20}, {centro_y})">d = {d_f:.1f} cm (tw = {tw_f:.2f} cm)</text>',
        '',
        '  <!-- Painel 2: Capacidades Resistentes no ELU -->',
        '  <rect x="630" y="140" width="370" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="655" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">2. Resistências de Cálculo (ELU)</text>',
        f'  <text x="655" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">γ_a1 = 1.10 · γ_a2 = 1.35</text>',
        '',
        f'  <g transform="translate(655, 230)">',
        f'    <text y="0" font-family="sans-serif" font-size="13" fill="#94a3b8">Compressão Axial N_c,Rd:</text>',
        f'    <text x="320" y="0" font-family="monospace" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="end">{float(comp.nc_rd_kn):.1f} kN</text>',
        '',
        f'    <text y="35" font-family="sans-serif" font-size="13" fill="#94a3b8">Força Euler Ne (Mínima):</text>',
        f'    <text x="320" y="35" font-family="monospace" font-size="14" font-weight="700" fill="#38bdf8" text-anchor="end">{float(comp.ne_kn):.1f} kN</text>',
        '',
        f'    <text y="70" font-family="sans-serif" font-size="13" fill="#94a3b8">Redução por Flambagem χ:</text>',
        f'    <text x="320" y="70" font-family="monospace" font-size="14" font-weight="700" fill="#f59e0b" text-anchor="end">{float(comp.fator_chi):.4f} (Q={float(comp.fator_q):.2f})</text>',
        '',
        f'    <text y="105" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Plástico Mpl,x:</text>',
        f'    <text x="320" y="105" font-family="monospace" font-size="14" font-weight="700" fill="#f8fafc" text-anchor="end">{float(fl.mpl_x_kn_cm)/100:.1f} kN.m</text>',
        '',
        f'    <text y="140" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Resistente M_Rd,x:</text>',
        f'    <text x="320" y="140" font-family="monospace" font-size="14" font-weight="700" fill="#10b981" text-anchor="end">{float(fl.mrd_x_kn_cm)/100:.1f} kN.m</text>',
        '',
        f'    <text y="175" font-family="sans-serif" font-size="13" fill="#94a3b8">Momento Resistente M_Rd,y:</text>',
        f'    <text x="320" y="175" font-family="monospace" font-size="14" font-weight="700" fill="#10b981" text-anchor="end">{float(fl.mrd_y_kn_cm)/100:.1f} kN.m</text>',
        '',
        f'    <text y="210" font-family="sans-serif" font-size="13" fill="#94a3b8">Cortante Resistente V_Rd,y:</text>',
        f'    <text x="320" y="210" font-family="monospace" font-size="14" font-weight="700" fill="#38bdf8" text-anchor="end">{float(cis.vrd_y_kn):.1f} kN</text>',
        '',
        f'    <text y="245" font-family="sans-serif" font-size="13" fill="#94a3b8">Comprimento Limite Lp (FLT):</text>',
        f'    <text x="320" y="245" font-family="monospace" font-size="14" font-weight="700" fill="#e2e8f0" text-anchor="end">{float(fl.lp_cm):.1f} cm</text>',
        '',
        f'    <text y="280" font-family="sans-serif" font-size="13" fill="#94a3b8">Comprimento Limite Lr (FLT):</text>',
        f'    <text x="320" y="280" font-family="monospace" font-size="14" font-weight="700" fill="#e2e8f0" text-anchor="end">{float(fl.lr_cm):.1f} cm</text>',
        f'  </g>',
        '',
        '  <!-- Painel 3: Estabilidade e Interação Flexo-Compressão -->',
        '  <rect x="1020" y="140" width="390" height="440" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="1045" y="175" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">3. Estabilidade e Interação</text>',
        f'  <text x="1045" y="200" font-family="system-ui, sans-serif" font-size="13" fill="#94a3b8">Esbeltez Limite: λ &lt;= 200</text>',
        '',
        '  <!-- Card Esbeltez X e Y -->',
        '  <rect x="1045" y="225" width="340" height="85" rx="8" fill="#0f172a" fill-opacity="0.6" stroke="#38bdf8" stroke-width="1.5" />',
        f'  <text x="1060" y="250" font-family="sans-serif" font-size="13" font-weight="700" fill="#38bdf8">Índices de Esbeltez</text>',
        f'  <text x="1060" y="275" font-family="monospace" font-size="13" fill="#f8fafc">λx = {float(comp.lambda_x):.1f} · λy = {float(comp.lambda_y):.1f}</text>',
        f'  <text x="1060" y="295" font-family="monospace" font-size="12" fill="#10b981">λmax = {float(comp.lambda_max):.1f} &lt;= 200.0 (CONFORME)</text>',
        '',
        '  <!-- Card Interação Flexo-Compressão -->',
        f'  <rect x="1045" y="325" width="340" height="110" rx="8" fill="#0f172a" fill-opacity="0.6" stroke="{"#10b981" if fc.atende else "#ef4444"}" stroke-width="1.5" />',
        f'  <text x="1060" y="350" font-family="sans-serif" font-size="13" font-weight="700" fill="{"#10b981" if fc.atende else "#ef4444"}">Interação Flexo-Compressão (Item 5.5.1)</text>',
        f'  <text x="1060" y="375" font-family="monospace" font-size="11" fill="#94a3b8">{escape(fc.equacao_normativa)}</text>',
        f'  <text x="1060" y="400" font-family="monospace" font-size="14" font-weight="700" fill="#f8fafc">Taxa Combinada: {float(fc.ratio_combinado)*100:.1f}%</text>',
        f'  <text x="1060" y="420" font-family="sans-serif" font-size="11" font-weight="700" fill="{"#10b981" if fc.atende else "#ef4444"}">{"CAPACIDADE SUFICIENTE" if fc.atende else "SOBRECARGA COMBINADA"}</text>',
        '',
        '  <!-- Painel Inferior: Síntese de Auditoria -->',
        '  <rect x="30" y="600" width="1380" height="270" rx="12" fill="url(#cardGrad)" filter="url(#dropShadow)" />',
        '  <text x="55" y="635" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#38bdf8">4. Auditoria Estrutural e Resumo Executivo Normativo</text>',
        '',
        '  <g transform="translate(55, 660)">',
        '    <!-- Card 1: Compressão -->',
        f'    <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if comp.atende else "#ef4444"}" stroke-width="1.5" />',
        f'    <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Compressão Axial</text>',
        f'    <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">N_sd: {float(s.nsd_compressao_kn):.1f} kN</text>',
        f'    <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">N_c,Rd: {float(comp.nc_rd_kn):.1f} kN</text>',
        f'    <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Trabalho: {float(comp.ratio_compressao)*100:.1f}%</text>',
        f'    <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if comp.atende else "#ef4444"}" fill-opacity="0.2" />',
        f'    <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if comp.atende else "#ef4444"}" text-anchor="middle">{"COMPRESSÃO CONFORME" if comp.atende else "FALHA COMPRESSÃO"}</text>',
        '',
        '    <!-- Card 2: Flexão Simples -->',
        '    <g transform="translate(330, 0)">',
        f'      <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if fl.atende else "#ef4444"}" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Flexão X (FLT)</text>',
        f'      <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">M_sd,x: {float(s.msd_x_kn_cm)/100:.1f} kN.m</text>',
        f'      <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">M_Rd,x: {float(fl.mrd_x_kn_cm)/100:.1f} kN.m</text>',
        f'      <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Trabalho: {float(fl.ratio_flexao_x)*100:.1f}%</text>',
        f'      <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if fl.atende else "#ef4444"}" fill-opacity="0.2" />',
        f'      <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if fl.atende else "#ef4444"}" text-anchor="middle">{"FLEXÃO CONFORME" if fl.atende else "FALHA FLEXÃO"}</text>',
        '    </g>',
        '',
        '    <!-- Card 3: Força Cortante -->',
        '    <g transform="translate(660, 0)">',
        f'      <rect width="310" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="{"#10b981" if cis.atende else "#ef4444"}" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Cisalhamento Alma</text>',
        f'      <text x="20" y="60" font-family="sans-serif" font-size="12" fill="#94a3b8">V_sd,y: {float(s.vsd_y_kn):.1f} kN</text>',
        f'      <text x="20" y="85" font-family="sans-serif" font-size="12" fill="#94a3b8">V_Rd,y: {float(cis.vrd_y_kn):.1f} kN</text>',
        f'      <text x="20" y="110" font-family="sans-serif" font-size="12" fill="#94a3b8">Trabalho: {float(cis.ratio_cisalhamento)*100:.1f}%</text>',
        f'      <rect x="20" y="130" width="270" height="35" rx="6" fill="{"#10b981" if cis.atende else "#ef4444"}" fill-opacity="0.2" />',
        f'      <text x="155" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if cis.atende else "#ef4444"}" text-anchor="middle">{"CORTANTE CONFORME" if cis.atende else "FALHA CORTANTE"}</text>',
        '    </g>',
        '',
        '    <!-- Card 4: Síntese de Dimensionamento -->',
        '    <g transform="translate(990, 0)">',
        f'      <rect width="330" height="185" rx="8" fill="#0f172a" fill-opacity="0.8" stroke="#38bdf8" stroke-width="1.5" />',
        f'      <text x="20" y="32" font-family="sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Diagnóstico Geral</text>',
        f'      <text x="20" y="60" font-family="monospace" font-size="12" fill="#38bdf8">Perfil: {p.designacao}</text>',
        f'      <text x="20" y="85" font-family="monospace" font-size="12" fill="#f59e0b">Aço: {a.nome} (fy={float(a.f_y_kn_cm2)*10:.0f} MPa)</text>',
        f'      <text x="20" y="110" font-family="monospace" font-size="12" fill="#10b981">Esbeltez: λmax={float(comp.lambda_max):.1f}</text>',
        f'      <rect x="20" y="130" width="290" height="35" rx="6" fill="{"#10b981" if resultado.conformidade_geral else "#ef4444"}" fill-opacity="0.2" />',
        f'      <text x="165" y="152" font-family="sans-serif" font-size="12" font-weight="700" fill="{"#10b981" if resultado.conformidade_geral else "#ef4444"}" text-anchor="middle">{"PRONTO P/ DETALHAMENTO" if resultado.conformidade_geral else "REDIMENSIONAR"}</text>',
        '    </g>',
        '  </g>',
        '</svg>',
    ]

    return "\n".join(svg_linhas) + "\n"
