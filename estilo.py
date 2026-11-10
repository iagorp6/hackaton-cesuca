"""Identidade visual do Vértice Desk (só apresentação; nenhuma regra de negócio aqui).

Layout de site: menu lateral branco com páginas, cabeçalho de página e conteúdo em cartões
com rótulo pequeno (eyebrow), título e subtítulo.
"""
import base64
import html
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

DESTAQUE = "#4f46e5"
DESTAQUE_ESCURO = "#4338ca"
DESTAQUE_SUAVE = "#eef0ff"
FUNDO = "#f6f7fb"
SUPERFICIE = "#ffffff"
LINHA = "#e6e8f0"
TEXTO = "#1e2235"
APAGADO = "#6b7280"
AMBAR = "#d4a017"
VERDE = "#5fb38a"
AZUL_CLARO = "#8cc5e3"
VERMELHO = "#d9534f"
VERTEX = "#f5b83d"
SERIES = [DESTAQUE, AMBAR, VERDE, AZUL_CLARO, "#9b8afb", "#94a3b8"]
CORES_RISCO = {"Alto": VERMELHO, "Médio": AMBAR, "Baixo": VERDE}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="st-"], .stMarkdown, button, input, textarea, select {{
  font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
}}
[data-testid="stIconMaterial"], .material-symbols-rounded, span[class*="material"] {{
  font-family: "Material Symbols Rounded" !important;
}}
.stApp {{ background: {FUNDO}; }}
.block-container {{ padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 1360px; }}
[data-testid="stAppDeployButton"], #MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent; }}

h1, h2, h3, h4 {{ color: {TEXTO}; letter-spacing: -0.01em; }}
.stMarkdown p, .stMarkdown li {{ color: {TEXTO}; }}
[data-testid="stCaptionContainer"] {{ color: {APAGADO}; }}

/* ---------- Menu lateral ---------- */
[data-testid="stSidebar"] {{ background: {SUPERFICIE}; border-right: 1px solid {LINHA}; }}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarUserContent"] {{ padding-top: 1.4rem; }}
.vd-marca {{ display: flex; align-items: center; gap: 12px; margin: 0 4px 22px; }}
.vd-logo {{
  display: block; width: 40px; height: 40px; flex: 0 0 40px;
}}
.vd-nome {{ font-size: 18px; font-weight: 700; color: {TEXTO}; line-height: 1.1; }}
.vd-sub {{ font-size: 12.5px; color: {APAGADO}; }}
[data-testid="stSidebar"] [role="radiogroup"] {{ gap: 4px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{
  width: 100%; padding: 10px 12px; border-radius: 10px; margin: 0; cursor: pointer;
  transition: background .12s ease;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: {FUNDO}; }}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display: none; }}
[data-testid="stSidebar"] [role="radiogroup"] label p {{ font-size: 15px; font-weight: 500; color: {APAGADO}; }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background: {DESTAQUE_SUAVE}; }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{ color: {DESTAQUE}; font-weight: 650; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"]:has(+ [role="radiogroup"]) {{ display: none; }}
.vd-menu-rotulo {{
  font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: #9aa1b2; margin: 18px 6px 6px;
}}

/* ---------- Cabeçalho da página ---------- */
.vd-pagina {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }}
.vd-pagina h1 {{ font-size: 28px; font-weight: 700; margin: 0; padding: 0; }}
.vd-pagina p {{ color: {APAGADO}; margin: 4px 0 0; font-size: 15px; }}
.vd-selos {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.vd-selo {{
  font-size: 12.5px; font-weight: 600; padding: 7px 12px; border-radius: 999px;
  background: {SUPERFICIE}; border: 1px solid {LINHA}; color: {TEXTO};
}}
.vd-selo.ativo {{ background: {DESTAQUE}; border-color: {DESTAQUE}; color: #fff; }}
.vd-ponto {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #3ecf8e; margin-right: 6px; }}

/* ---------- Cartões ---------- */
[class*="st-key-card"] {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 16px;
  padding: 22px 24px 18px; box-shadow: 0 1px 3px rgba(30,34,53,.04);
}}
.vd-eyebrow {{
  font-size: 11.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {DESTAQUE};
}}
.vd-titulo {{ font-size: 21px; font-weight: 700; color: {TEXTO}; margin: 4px 0 2px; line-height: 1.25; }}
.vd-desc {{ font-size: 14px; color: {APAGADO}; margin-bottom: 6px; }}

/* KPIs */
[data-testid="stMetric"] {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 16px;
  padding: 16px 18px; box-shadow: 0 1px 3px rgba(30,34,53,.04); height: 100%;
}}
[class*="st-key-card"] [data-testid="stMetric"] {{ box-shadow: none; background: {FUNDO}; border-color: transparent; }}
[data-testid="stMetricLabel"] p {{
  font-size: 11.5px !important; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: {APAGADO};
}}
[data-testid="stMetricValue"] {{ font-size: 1.75rem !important; font-weight: 700; color: {TEXTO}; font-variant-numeric: tabular-nums; }}

/* Tabelas, formulários, botões */
[data-testid="stDataFrame"] {{ border: 1px solid {LINHA}; border-radius: 12px; overflow: hidden; }}
.stTextArea textarea, .stTextInput input, [data-baseweb="select"] > div, .stNumberInput input {{ border-radius: 10px !important; }}
.stButton > button, .stDownloadButton > button {{ border-radius: 10px; font-weight: 600; padding: .55rem 1.2rem; }}
.stButton > button[kind="primary"] {{ background: {DESTAQUE}; border-color: {DESTAQUE}; }}
.stButton > button[kind="primary"]:hover {{ background: {DESTAQUE_ESCURO}; border-color: {DESTAQUE_ESCURO}; }}
[data-testid="stAlert"] {{ border-radius: 12px; }}
[data-testid="stExpander"] {{ border: 1px solid {LINHA}; border-radius: 12px; background: {SUPERFICIE}; }}

/* Barras de progresso em HTML (tempo por prioridade) */
.vd-barra-item {{ margin: 14px 0 4px; }}
.vd-barra-topo {{ display: flex; justify-content: space-between; font-size: 14px; color: {TEXTO}; font-weight: 600; }}
.vd-barra-topo span:last-child {{ font-variant-numeric: tabular-nums; }}
.vd-barra {{ height: 10px; border-radius: 999px; background: {FUNDO}; margin-top: 6px; overflow: hidden; }}
.vd-barra i {{ display: block; height: 100%; border-radius: 999px; }}
.vd-barra-nota {{ font-size: 12px; color: {APAGADO}; margin-top: 4px; }}

/* Chamado aberto */
.vd-ticket {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-left: 4px solid {DESTAQUE};
  border-radius: 12px; padding: 14px 16px; margin: 10px 0; line-height: 1.9;
}}
.vd-tag {{
  display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
  background: {DESTAQUE_SUAVE}; color: {DESTAQUE}; margin-right: 6px;
}}
.vd-lista li {{ margin: 6px 0; }}
</style>
"""


def _template_plotly():
    t = go.layout.Template()
    eixo = dict(gridcolor=LINHA, linecolor=LINHA, zerolinecolor=LINHA, tickfont=dict(color=APAGADO, size=12),
                title=dict(font=dict(color=APAGADO, size=12)))
    t.layout = go.Layout(
        font=dict(family="Inter, system-ui, sans-serif", size=13, color=TEXTO),
        colorway=SERIES, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=36, b=8), height=330,
        xaxis=dict(eixo, showgrid=False), yaxis=dict(eixo),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text="",
                    font=dict(size=12.5, color=TEXTO)),
        hoverlabel=dict(bgcolor=TEXTO, font=dict(color="#fff")),
        bargap=0.35,
    )
    t.data.bar = [go.Bar(marker=dict(cornerradius=8))]
    return t


def aplicar_estilo():
    """Injeta o CSS e define o visual padrão de todos os gráficos plotly."""
    st.markdown(CSS, unsafe_allow_html=True)
    pio.templates["vertice"] = _template_plotly()
    px.defaults.template = "vertice"


def marca():
    icone = base64.b64encode(Path(__file__).with_name("vertice-icon.svg").read_bytes()).decode("ascii")
    st.sidebar.markdown(
        f'<div class="vd-marca"><img class="vd-logo" src="data:image/svg+xml;base64,{icone}" alt="Símbolo Vértice">'
        f'<div><div class="vd-nome">Vértice Desk</div>'
        '<div class="vd-sub">Central de Atendimento</div></div></div>', unsafe_allow_html=True)


def rotulo_menu(texto):
    st.sidebar.markdown(f'<div class="vd-menu-rotulo">{html.escape(texto)}</div>', unsafe_allow_html=True)


def cabecalho_pagina(titulo, descricao="", selos=None):
    """selos: lista de textos curtos exibidos à direita (o primeiro ganha o ponto verde)."""
    selos = selos or []
    s = "".join(
        f'<span class="vd-selo">{"<span class=vd-ponto></span>" if i == 0 else ""}{html.escape(t)}</span>'
        for i, t in enumerate(selos))
    st.markdown(f'<div class="vd-pagina"><div><h1>{html.escape(titulo)}</h1><p>{html.escape(descricao)}</p></div>'
                f'<div class="vd-selos">{s}</div></div>', unsafe_allow_html=True)


_n = {"i": 0}


def cartao(eyebrow, titulo, descricao=""):
    """Abre um cartão (use com `with`). Ex.: with cartao("Evolução", "Chamados", "..."): st.plotly_chart(...)"""
    _n["i"] += 1
    c = st.container(key=f"card_{_n['i']}")
    c.markdown(f'<div class="vd-eyebrow">{html.escape(eyebrow)}</div><div class="vd-titulo">{html.escape(titulo)}</div>'
               + (f'<div class="vd-desc">{html.escape(descricao)}</div>' if descricao else ""), unsafe_allow_html=True)
    return c


def barras_html(itens, cor=VERMELHO):
    """itens: lista de (rótulo, valor, texto_valor, nota). Barras proporcionais ao maior valor."""
    maior = max((v for _, v, _, _ in itens), default=1) or 1
    partes = []
    for rot, v, txt, nota in itens:
        partes.append(
            f'<div class="vd-barra-item"><div class="vd-barra-topo"><span>{html.escape(rot)}</span><span>{html.escape(txt)}</span></div>'
            f'<div class="vd-barra"><i style="width:{v / maior * 100:.0f}%;background:{cor}"></i></div>'
            f'<div class="vd-barra-nota">{html.escape(nota)}</div></div>')
    st.markdown("".join(partes), unsafe_allow_html=True)
