"""Exportadores de dados, relatórios e pacotes determinísticos para estruturas metálicas.

Padrões de engenharia LOFRANO TECNOLOGIA:
- Sanitização contra injeção de fórmulas em CSV (prefixo "'" para '=', '+', '-', '@', '\\t', '\\r').
- Empacotamento ZIP determinístico com timestamp fixo (2026, 1, 1, 0, 0, 0) e flags de não-sobrescrita atômica.
- Relatório técnico estruturado em conformidade com a ABNT NBR 8800:2024.
"""

from __future__ import annotations

import csv
import io
import os
from pathlib import Path
import zipfile

from .codecs import resultado_para_dict
from .models import ResultadoAco

DATA_HORA_DETERMINISTICA_ZIP = (2026, 1, 1, 0, 0, 0)


def sanitizar_campo_csv(valor: object) -> str:
    """Sanitiza strings contra ataques de injeção de fórmulas em planilhas."""
    texto = str(valor)
    if texto and texto[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{texto}"
    return texto


def exportar_relatorio_texto(resultado: ResultadoAco) -> str:
    """Gera relatório de cálculo técnico formatado em texto legível para memorial descritivo."""
    p = resultado.perfil
    a = resultado.aco
    s = resultado.solicitacoes
    c = resultado.contorno
    tr = resultado.tracao
    comp = resultado.compressao
    fl = resultado.flexao
    cis = resultado.cisalhamento
    fc = resultado.flexo_compressao

    linhas = [
        "=" * 84,
        "   LOFRANO TECNOLOGIA — MEMORIAL DESCRITIVO DE DIMENSIONAMENTO ESTRUTURAL",
        "           ESTRUTURAS METÁLICAS E PERFIS DE AÇO (ABNT NBR 8800:2024)",
        "=" * 84,
        f"Perfil Selecionado:       {p.designacao} (Série W Laminado)",
        f"Aço Estrutural:           {a.nome} (f_y = {float(a.f_y_kn_cm2)*10:.0f} MPa, f_u = {float(a.f_u_kn_cm2)*10:.0f} MPa)",
        f"Módulo de Elasticidade:   E = {float(a.e_kn_cm2)*10:.0f} MPa · G = {float(a.g_kn_cm2)*10:.0f} MPa",
        "-" * 84,
        "1. PROPRIEDADES GEOMÉTRICAS DA SEÇÃO TRANSVERSAL",
        f"  Altura Total (d):       {float(p.d_cm):.2f} cm (Mesa: {float(p.bf_cm):.2f} cm x {float(p.tf_cm):.2f} cm)",
        f"  Espessura Alma (tw):    {float(p.tw_cm):.2f} cm (Altura livre da alma: {float(p.h_cm):.2f} cm)",
        f"  Área Bruta (Ag):        {float(p.ag_cm2):.2f} cm²",
        f"  Inércias Principais:    Ix = {float(p.ix_cm4):.1f} cm⁴ · Iy = {float(p.iy_cm4):.1f} cm⁴",
        f"  Módulos Plásticos:      Zx = {float(p.zx_cm3):.1f} cm³ · Zy = {float(p.zy_cm3):.1f} cm³",
        f"  Raios de Giração:       rx = {float(p.rx_cm):.2f} cm · ry = {float(p.ry_cm):.2f} cm",
        "-" * 84,
        "2. CONDIÇÕES DE CONTORNO E COMPRIMENTOS DE FLAMBAGEM",
        f"  Comprimento Efetivo Kx*Lx: {float(c.kx_lx_cm):.1f} cm -> Esbeltez λx = {float(comp.lambda_x):.1f}",
        f"  Comprimento Efetivo Ky*Ly: {float(c.ky_ly_cm):.1f} cm -> Esbeltez λy = {float(comp.lambda_y):.1f}",
        f"  Esbeltez Máxima Global:    λ_max = {float(comp.lambda_max):.1f} (Limite compressão <= 200)",
        f"  Comprimento Destravado Lb: {float(c.lb_cm):.1f} cm (Fator Cb = {float(c.cb_fator):.2f})",
        "-" * 84,
        "3. SOLICITAÇÕES DE CÁLCULO NO ESTADO LIMITE ÚLTIMO (ELU)",
        f"  Força Axial Solicitante:   N_sd,c = {float(s.nsd_compressao_kn):.1f} kN · N_sd,t = {float(s.nsd_tracao_kn):.1f} kN",
        f"  Momento Fletor Solicitante:M_sd,x = {float(s.msd_x_kn_cm)/100:.2f} kN.m · M_sd,y = {float(s.msd_y_kn_cm)/100:.2f} kN.m",
        f"  Força Cortante Solicitante:V_sd,y = {float(s.vsd_y_kn):.1f} kN",
        "-" * 84,
        "4. VERIFICAÇÃO DE COMPRESSÃO AXIAL E FLAMBAGEM (ITEM 5.3)",
        f"  Força Elástica de Euler Ne:{float(comp.ne_kn):.1f} kN",
        f"  Esbeltez Adimensional λ0:  {float(comp.lambda_0):.3f}",
        f"  Fator de Flambagem Local Q:{float(comp.fator_q):.2f}",
        f"  Fator de Redução Global χ: {float(comp.fator_chi):.4f}",
        f"  Força Resistente N_c,Rd:   {float(comp.nc_rd_kn):.1f} kN",
        f"  Taxa de Trabalho Nsd/NcRd: {float(comp.ratio_compressao)*100:.1f}%",
        f"  Status Compressão:         {'APROVADO' if comp.atende else 'REPROVADO'} ({comp.modo_falha})",
        "-" * 84,
        "5. VERIFICAÇÃO DE FLEXÃO SIMPLES (ITEM 5.4)",
        f"  Momento Plástico Mpl,x:    {float(fl.mpl_x_kn_cm)/100:.2f} kN.m",
        f"  Comprimentos Limites FLT:  Lp = {float(fl.lp_cm):.1f} cm · Lr = {float(fl.lr_cm):.1f} cm",
        f"  Momento Resistente M_Rd,x: {float(fl.mrd_x_kn_cm)/100:.2f} kN.m (Taxa: {float(fl.ratio_flexao_x)*100:.1f}%)",
        f"  Momento Resistente M_Rd,y: {float(fl.mrd_y_kn_cm)/100:.2f} kN.m (Taxa: {float(fl.ratio_flexao_y)*100:.1f}%)",
        f"  Status Flexão:             {'APROVADO' if fl.atende else 'REPROVADO'} ({fl.modo_falha})",
        "-" * 84,
        "6. VERIFICAÇÃO DE FORÇA CORTANTE (ITEM 5.4.3)",
        f"  Área Efetiva da Alma Aw:   {float(cis.aw_cm2):.2f} cm²",
        f"  Força Cortante Resist V_Rd:{float(cis.vrd_y_kn):.1f} kN",
        f"  Taxa de Trabalho Vsd/VRd:  {float(cis.ratio_cisalhamento)*100:.1f}%",
        f"  Status Cisalhamento:       {'APROVADO' if cis.atende else 'REPROVADO'} ({cis.modo_falha})",
        "-" * 84,
        "7. INTERAÇÃO FLEXO-COMPRESSÃO (ITEM 5.5.1)",
        f"  Equação de Interação:      {fc.equacao_normativa}",
        f"  Índice Combinado:          {float(fc.ratio_combinado)*100:.1f}% (Limite <= 100.0%)",
        f"  Status Interação:          {'APROVADO' if fc.atende else 'REPROVADO'}",
        "-" * 84,
        "8. CONCLUSÃO GERAL DE ENGENHARIA",
        f"  Parecer Estrutural: {'APROVADO E EM CONFORMIDADE' if resultado.conformidade_geral else 'NÃO CONFORME'}",
        f"  Resumo Executivo:   {resultado.resumo_executivo}",
        "=" * 84,
    ]

    return "\n".join(linhas) + "\n"


def exportar_csv(resultado: ResultadoAco, caminho_destino: str | Path) -> None:
    """Exporta métricas de cálculo para arquivo CSV protegido contra injeção de fórmulas."""
    p = resultado.perfil
    a = resultado.aco
    s = resultado.solicitacoes
    comp = resultado.compressao
    fl = resultado.flexao
    cis = resultado.cisalhamento
    fc = resultado.flexo_compressao

    with open(caminho_destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        escritor.writerow([
            sanitizar_campo_csv("parametro"),
            sanitizar_campo_csv("unidade"),
            sanitizar_campo_csv("valor_numerico"),
            sanitizar_campo_csv("status_normativo"),
        ])

        linhas_dados = [
            ("perfil", "-", p.designacao, "OK"),
            ("aco", "-", a.nome, "OK"),
            ("area_bruta_ag", "cm2", f"{float(p.ag_cm2):.2f}", "OK"),
            ("altura_total_d", "cm", f"{float(p.d_cm):.2f}", "OK"),
            ("largura_mesa_bf", "cm", f"{float(p.bf_cm):.2f}", "OK"),
            ("esbeltez_maxima", "-", f"{float(comp.lambda_max):.1f}", "CONFORME" if comp.lambda_max <= 200 else "FALHA"),
            ("forca_euler_ne", "kN", f"{float(comp.ne_kn):.1f}", "OK"),
            ("compressao_nc_rd", "kN", f"{float(comp.nc_rd_kn):.1f}", "OK"),
            ("taxa_compressao", "-", f"{float(comp.ratio_compressao):.4f}", "CONFORME" if comp.atende else "FALHA"),
            ("flexao_mrd_x", "kN.m", f"{float(fl.mrd_x_kn_cm)/100:.2f}", "OK"),
            ("taxa_flexao_x", "-", f"{float(fl.ratio_flexao_x):.4f}", "CONFORME" if fl.atende else "FALHA"),
            ("cortante_vrd_y", "kN", f"{float(cis.vrd_y_kn):.1f}", "OK"),
            ("taxa_cortante", "-", f"{float(cis.ratio_cisalhamento):.4f}", "CONFORME" if cis.atende else "FALHA"),
            ("interacao_combinada", "-", f"{float(fc.ratio_combinado):.4f}", "CONFORME" if fc.atende else "FALHA"),
            ("conformidade_geral", "-", "1" if resultado.conformidade_geral else "0", "APROVADO" if resultado.conformidade_geral else "REPROVADO"),
        ]

        for param, unid, val, st in linhas_dados:
            escritor.writerow([
                sanitizar_campo_csv(param),
                sanitizar_campo_csv(unid),
                sanitizar_campo_csv(val),
                sanitizar_campo_csv(st),
            ])


def exportar_zip_deterministico(
    resultado: ResultadoAco,
    caminho_zip: str | Path,
    conteudo_svg: str | None = None,
) -> None:
    """Cria um pacote ZIP determinístico com modo não-sobrescrita e timestamps normalizados."""
    caminho = Path(caminho_zip)
    if caminho.exists():
        raise FileExistsError(f"Arquivo de destino já existe e não será sobrescrito: {caminho}")

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(str(caminho), flags, 0o644)
    with os.fdopen(fd, "wb") as f_out:
        with zipfile.ZipFile(f_out, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Relatório em texto
            relatorio = exportar_relatorio_texto(resultado)
            info_txt = zipfile.ZipInfo("memorial_calculo.txt", DATA_HORA_DETERMINISTICA_ZIP)
            info_txt.external_attr = 0o644 << 16
            zf.writestr(info_txt, relatorio.encode("utf-8"))

            # 2. Dados em JSON canônico
            dados_dict = resultado_para_dict(resultado)
            import json
            json_str = json.dumps(dados_dict, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            info_json = zipfile.ZipInfo("resultado_calculo.json", DATA_HORA_DETERMINISTICA_ZIP)
            info_json.external_attr = 0o644 << 16
            zf.writestr(info_json, json_str.encode("utf-8"))

            # 3. Planilha CSV sanitizada
            buffer_csv = io.StringIO()
            escritor = csv.writer(buffer_csv, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            escritor.writerow([sanitizar_campo_csv("parametro"), sanitizar_campo_csv("valor")])
            escritor.writerow([sanitizar_campo_csv("perfil"), sanitizar_campo_csv(resultado.perfil.designacao)])
            escritor.writerow([sanitizar_campo_csv("aco"), sanitizar_campo_csv(resultado.aco.nome)])
            escritor.writerow([sanitizar_campo_csv("conformidade"), sanitizar_campo_csv(resultado.conformidade_geral)])
            info_csv = zipfile.ZipInfo("resumo_dados.csv", DATA_HORA_DETERMINISTICA_ZIP)
            info_csv.external_attr = 0o644 << 16
            zf.writestr(info_csv, buffer_csv.getvalue().encode("utf-8"))

            # 4. Painel SVG (se fornecido)
            if conteudo_svg is not None:
                info_svg = zipfile.ZipInfo("painel_detalhamento.svg", DATA_HORA_DETERMINISTICA_ZIP)
                info_svg.external_attr = 0o644 << 16
                zf.writestr(info_svg, conteudo_svg.encode("utf-8"))
