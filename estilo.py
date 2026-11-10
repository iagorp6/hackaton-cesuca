"""Identidade visual do Vértice Desk (só apresentação; nenhuma regra de negócio aqui).

Uso no app.py, logo depois de st.set_page_config:
    from estilo import aplicar_estilo, topo
    aplicar_estilo()
    topo()
"""
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import streamlit as st

# Paleta: tinta escura na navegação, um único azul-petróleo de destaque, neutros levemente azulados.
TINTA = "#0d1f2d"
DESTAQUE = "#0f6e7a"
DESTAQUE_SUAVE = "#e3f1f2"
FUNDO = "#f4f6f8"
SUPERFICIE = "#ffffff"
LINHA = "#e2e7ec"
TEXTO = "#16222e"
APAGADO = "#5c6b7a"
SERIES = [DESTAQUE, "#d9822b", "#5b5fc7", "#2f9e63", "#8a94a3", "#c2410c"]

CSS = f"""
<style>
html, body, [class*="st-"], .stMarkdown, .stText, button, input, textarea, select {{
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}}
/* Ícones do Streamlit usam fonte própria: sem isto aparece "double_arrow_right" escrito */
[data-testid="stIconMaterial"], .material-symbols-rounded, span[class*="material"] {{
  font-family: "Material Symbols Rounded" !important;
}}

.stApp {{ background: {FUNDO}; }}
.block-container {{ padding-top: 1.2rem !important; padding-bottom: 3rem !important; max-width: 1320px; }}

/* Some com o que denuncia "app de protótipo" */
[data-testid="stAppDeployButton"], #MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* Tipografia */
h1, h2, h3, h4 {{ color: {TEXTO}; letter-spacing: -0.01em; }}
.stMarkdown h2 {{ font-size: 1.5rem; font-weight: 700; }}
.stMarkdown h3 {{ font-size: 1.25rem; font-weight: 650; line-height: 1.3; }}
.stMarkdown h4 {{ font-size: 1.05rem; font-weight: 650; margin-top: .6rem; }}
.stMarkdown p, .stMarkdown li {{ color: {TEXTO}; }}
[data-testid="stCaptionContainer"] {{ color: {APAGADO}; }}

/* Barra superior */
.vd-top {{
  display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
  background: {TINTA}; color: #fff; border-radius: 12px; padding: 14px 20px; margin-bottom: 6px;
}}
.vd-marca {{ display: flex; align-items: center; gap: 12px; }}
.vd-logo {{
  width: 34px; height: 34px; border-radius: 8px; background: {DESTAQUE};
  display: grid; place-items: center; font-weight: 700; font-size: 18px; color: #fff;
}}
.vd-nome {{ font-size: 18px; font-weight: 700; line-height: 1.1; }}
.vd-sub {{ font-size: 12.5px; color: #a9b8c6; }}
.vd-chips {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.vd-chip {{
  font-size: 12px; font-weight: 600; padding: 5px 10px; border-radius: 999px;
  background: rgba(255,255,255,.08); color: #d6e0ea; border: 1px solid rgba(255,255,255,.12);
}}
.vd-chip b {{ color: #fff; }}
.vd-ponto {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #3ecf8e; margin-right: 6px; }}

/* Abas como navegação de site */
.stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] {{
  gap: 4px; background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 10px;
  padding: 4px; margin-bottom: 18px; flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"], .stTabs [role="tab"] {{
  background: transparent !important; border: none !important; border-radius: 7px !important;
  padding: 8px 14px !important; height: auto !important; color: {APAGADO} !important; font-weight: 500;
}}
.stTabs [data-baseweb="tab"]:hover {{ background: {FUNDO} !important; color: {TEXTO} !important; }}
.stTabs [aria-selected="true"] {{
  background: {DESTAQUE_SUAVE} !important; color: {DESTAQUE} !important; font-weight: 650 !important;
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* Cartões de KPI */
[data-testid="stMetric"] {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 12px;
  padding: 14px 16px; box-shadow: 0 1px 2px rgba(13,31,45,.04); height: 100%;
}}
[data-testid="stMetricLabel"] p {{
  font-size: 12px !important; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; color: {APAGADO};
}}
[data-testid="stMetricValue"] {{
  font-size: 1.7rem !important; font-weight: 700; color: {TEXTO}; font-variant-numeric: tabular-nums;
}}

/* Gráficos e tabelas em cartões */
[data-testid="stPlotlyChart"] {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 12px; padding: 10px 8px 4px;
  box-shadow: 0 1px 2px rgba(13,31,45,.04);
}}
[data-testid="stDataFrame"], [data-testid="stTable"] {{
  border: 1px solid {LINHA}; border-radius: 12px; overflow: hidden; background: {SUPERFICIE};
}}
[data-testid="stExpander"] {{ background: {SUPERFICIE}; border: 1px solid {LINHA}; border-radius: 12px; }}

/* Formulários e botões */
.stTextArea textarea, .stTextInput input, [data-baseweb="select"] > div {{
  border-radius: 8px !important; background: {SUPERFICIE} !important;
}}
.stButton > button, .stDownloadButton > button {{ border-radius: 8px; font-weight: 600; padding: .5rem 1.1rem; }}
.stButton > button[kind="primary"] {{ background: {DESTAQUE}; border-color: {DESTAQUE}; }}
.stButton > button[kind="primary"]:hover {{ background: #0b5862; border-color: #0b5862; }}
[data-testid="stAlert"] {{ border-radius: 10px; }}

/* Barra lateral escura */
[data-testid="stSidebar"] {{ background: {TINTA}; }}
[data-testid="stSidebar"] * {{ color: #dfe7ee !important; }}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{ color: #95a6b6 !important; }}

/* Cartão do chamado (classes já usadas no app) */
.vd-ticket {{
  background: {SUPERFICIE}; border: 1px solid {LINHA}; border-left: 4px solid {DESTAQUE};
  border-radius: 10px; padding: 14px 16px; margin: 10px 0; line-height: 1.8;
}}
.vd-tag {{
  display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
  background: {FUNDO}; color: {TEXTO}; border: 1px solid {LINHA}; margin-right: 6px;
}}

button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible {{
  outline: 3px solid {DESTAQUE}; outline-offset: 2px;
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }}
}}
</style>
"""


def _template_plotly():
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family="Segoe UI, system-ui, sans-serif", size=13, color=TEXTO),
        title=dict(font=dict(size=15, color=TEXTO), x=0.01, xanchor="left"),
        colorway=SERIES,
        paper_bgcolor=SUPERFICIE,
        plot_bgcolor=SUPERFICIE,
        margin=dict(l=10, r=10, t=48, b=10),
        xaxis=dict(gridcolor=LINHA, linecolor=LINHA, zerolinecolor=LINHA, tickfont=dict(color=APAGADO)),
        yaxis=dict(gridcolor=LINHA, linecolor=LINHA, zerolinecolor=LINHA, tickfont=dict(color=APAGADO)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=""),
        hoverlabel=dict(bgcolor=TINTA, font=dict(color="#fff")),
        bargap=0.28,
    )
    return t


def aplicar_estilo():
    """Injeta o CSS e define o visual padrão de todos os gráficos plotly do app."""
    st.markdown(CSS, unsafe_allow_html=True)
    pio.templates["vertice"] = _template_plotly()
    px.defaults.template = "vertice"


def topo(subtitulo="Central de Atendimento · Suporte N1/N2", chips=None):
    """Barra superior com marca e indicadores curtos. chips: lista de (rótulo, valor)."""
    chips = chips or []
    html_chips = "".join(f'<span class="vd-chip">{r} <b>{v}</b></span>' for r, v in chips)
    st.markdown(
        f'<div class="vd-top"><div class="vd-marca"><div class="vd-logo">V</div>'
        f'<div><div class="vd-nome">Vértice Desk</div><div class="vd-sub">{subtitulo}</div></div></div>'
        f'<div class="vd-chips"><span class="vd-chip"><span class="vd-ponto"></span>Triagem ativa</span>{html_chips}</div></div>',
        unsafe_allow_html=True,
    )
