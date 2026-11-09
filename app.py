import pandas as pd
import plotly.express as px
import streamlit as st

from radar import Pesos, calcular_radar, carregar_dados, mensagem_retencao, problemas_qualidade

st.set_page_config(page_title="Radar de Churn", page_icon="📡", layout="wide")


@st.cache_data
def dados():
    return carregar_dados()


clientes, atend, uso = dados()

# ---------------- Sidebar: pesos ajustáveis ----------------
st.sidebar.header("⚙️ Pesos do score")
st.sidebar.caption("Ajuste a importância de cada sinal. O score é reescalado para 0 a 100.")
pesos = Pesos(
    queda_uso=st.sidebar.slider("Queda de uso", 0, 50, 35),
    pendentes=st.sidebar.slider("Chamados pendentes", 0, 50, 25),
    satisfacao=st.sidebar.slider("Satisfação baixa", 0, 50, 25),
    tempo=st.sidebar.slider("Tempo de resolução alto", 0, 50, 15),
)
if pesos.total() == 0:
    st.sidebar.error("Defina ao menos um peso maior que zero.")
    st.stop()

radar = calcular_radar(clientes, atend, uso, pesos)

st.title("📡 Radar de Churn")
st.caption("Quais clientes estão em risco de cancelar, por quê, e o que o time de CS deve fazer agora. "
           "Dados 100% fictícios do Hackathon Data Cempro + Cesuca 2026.")

aba_geral, aba_rank, aba_cliente, aba_ops, aba_dados = st.tabs(
    ["Visão geral", "Ranking de risco", "Ficha do cliente", "Operação de suporte", "Qualidade dos dados"]
)

# ---------------- Visão geral ----------------
with aba_geral:
    alto = radar[radar["faixa"] == "Alto"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Clientes em risco alto", len(alto), f"{len(alto) / len(radar) * 100:.0f}% da base", delta_color="inverse")
    k2.metric("Chamados pendentes", int((atend["status"] == "Pendente").sum()))
    k3.metric("Satisfação média", f"{atend['satisfacao_1_a_5'].mean():.2f} / 5")
    tot = uso.groupby("mes")["acessos"].sum()
    k4.metric("Acessos em set", int(tot.get("2026-09", 0)),
              f"{(tot.get('2026-09', 0) / tot.get('2026-08', 1) - 1) * 100:.1f}% vs ago")

    c1, c2 = st.columns(2)
    ordem = ["Alto", "Médio", "Baixo"]
    cores = {"Alto": "#d62728", "Médio": "#ff7f0e", "Baixo": "#2ca02c"}
    with c1:
        dist = radar["faixa"].value_counts().reindex(ordem).fillna(0).reset_index()
        dist.columns = ["faixa", "clientes"]
        st.plotly_chart(px.bar(dist, x="faixa", y="clientes", color="faixa", color_discrete_map=cores,
                               title="Clientes por faixa de risco"), use_container_width=True)
    with c2:
        st.plotly_chart(px.histogram(radar, x="score", nbins=20, title="Distribuição do score"),
                        use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        seg = radar.groupby(["setor", "faixa"]).size().reset_index(name="clientes")
        st.plotly_chart(px.bar(seg, x="setor", y="clientes", color="faixa", color_discrete_map=cores,
                               category_orders={"faixa": ordem}, title="Risco por setor"),
                        use_container_width=True)
    with c4:
        seg = radar.groupby(["porte", "faixa"]).size().reset_index(name="clientes")
        st.plotly_chart(px.bar(seg, x="porte", y="clientes", color="faixa", color_discrete_map=cores,
                               category_orders={"faixa": ordem, "porte": ["Micro", "Pequena", "Média"]},
                               title="Risco por porte"), use_container_width=True)

# ---------------- Ranking ----------------
with aba_rank:
    f1, f2, f3, f4 = st.columns(4)
    faixas = f1.multiselect("Faixa", ordem, default=["Alto", "Médio"])
    setores = f2.multiselect("Setor", sorted(radar["setor"].unique()))
    portes = f3.multiselect("Porte", ["Micro", "Pequena", "Média"])
    cidades = f4.multiselect("Cidade", sorted(radar["cidade"].unique()))

    r = radar.copy()
    if faixas:
        r = r[r["faixa"].isin(faixas)]
    if setores:
        r = r[r["setor"].isin(setores)]
    if portes:
        r = r[r["porte"].isin(portes)]
    if cidades:
        r = r[r["cidade"].isin(cidades)]

    cols = ["cliente_id", "nome_ficticio", "score", "faixa", "motivos", "acao_sugerida", "setor", "porte",
            "cidade", "acessos_jul", "acessos_ago", "acessos_set", "pendentes", "satisfacao_media"]
    st.dataframe(
        r[cols], hide_index=True, use_container_width=True,
        column_config={"score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d")},
    )
    st.download_button("⬇️ Exportar lista para o CS (CSV)", r[cols].to_csv(index=False).encode("utf-8"),
                       "radar_churn.csv", "text/csv")

# ---------------- Ficha do cliente ----------------
with aba_cliente:
    opcoes = radar["cliente_id"] + " · " + radar["nome_ficticio"] + " · score " + radar["score"].astype(str)
    escolha = st.selectbox("Cliente (ordenado por risco)", opcoes)
    cid = escolha.split(" · ")[0]
    row = radar[radar["cliente_id"] == cid].iloc[0]

    a, b, c = st.columns([1, 1, 2])
    a.metric("Score", int(row["score"]), row["faixa"], delta_color="off")
    b.metric("Chamados", int(row["chamados"]), f"{int(row['pendentes'])} pendente(s)", delta_color="off")
    c.markdown(f"**{row['nome_ficticio']}** · {row['porte']} · {row['setor']} · {row['cidade']}  \n"
               f"**Motivos:** {row['motivos']}  \n**Ação sugerida:** {row['acao_sugerida']}")

    comp = pd.DataFrame({
        "sinal": ["Queda de uso", "Pendentes", "Satisfação", "Tempo de resolução"],
        "pontos": [row["pts_queda_uso"], row["pts_pendentes"], row["pts_satisfacao"], row["pts_tempo"]],
    })
    g1, g2 = st.columns(2)
    g1.plotly_chart(px.bar(comp, x="pontos", y="sinal", orientation="h", title="De onde vem o score"),
                    use_container_width=True)
    hist = uso[uso["cliente_id"] == cid]
    g2.plotly_chart(px.line(hist, x="mes", y=["acessos", "operacoes_realizadas"], markers=True,
                            hover_data=["servico"], title="Uso mensal").update_xaxes(type="category"),
                    use_container_width=True)

    st.subheader("Chamados")
    st.dataframe(atend[atend["cliente_id"] == cid].sort_values("data_abertura", ascending=False),
                 hide_index=True, use_container_width=True)

    st.subheader("✉️ Rascunho de mensagem de retenção")
    st.text_area("Copie e envie pelo canal do cliente", mensagem_retencao(row), height=260)

# ---------------- Operação ----------------
with aba_ops:
    res = atend[atend["status"] == "Resolvido"]
    st.markdown("Insights para o time de suporte, que alimentam os sinais do radar.")
    o1, o2 = st.columns(2)
    t_prio = res.groupby("prioridade")["tempo_resolucao_min"].mean().reindex(["Alta", "Normal", "Baixa"]).reset_index()
    o1.plotly_chart(px.bar(t_prio, x="prioridade", y="tempo_resolucao_min",
                           title="Tempo médio de resolução por prioridade (min)"), use_container_width=True)
    o1.warning("Chamados de prioridade **Alta** demoram mais que os de **Baixa**: a fila não respeita a prioridade.")
    t_ass = res.groupby("assunto").agg(tempo=("tempo_resolucao_min", "mean"),
                                       satisfacao=("satisfacao_1_a_5", "mean"),
                                       chamados=("atendimento_id", "count")).reset_index()
    o2.plotly_chart(px.scatter(t_ass, x="tempo", y="satisfacao", size="chamados", text="assunto",
                               title="Assunto: tempo x satisfação"), use_container_width=True)
    o3, o4 = st.columns(2)
    sat_serv = res.groupby("servico")["satisfacao_1_a_5"].mean().sort_values().reset_index()
    o3.plotly_chart(px.bar(sat_serv, x="satisfacao_1_a_5", y="servico", orientation="h",
                           title="Satisfação média por serviço"), use_container_width=True)
    pend = atend[atend["status"] == "Pendente"].groupby(["prioridade", "assunto"]).size().reset_index(name="pendentes")
    o4.plotly_chart(px.bar(pend, x="assunto", y="pendentes", color="prioridade",
                           title="Pendências por assunto e prioridade"), use_container_width=True)

# ---------------- Qualidade ----------------
with aba_dados:
    st.markdown("Problemas encontrados nos arquivos fornecidos e como o radar lida com eles.")
    st.dataframe(problemas_qualidade(clientes, atend, uso), hide_index=True, use_container_width=True)
    st.info(
        "• Queda de uso compara set com a média de jul e ago, somando todos os serviços do cliente.  \n"
        "• Pendentes não têm nota nem tempo, então entram só no sinal de pendências.  \n"
        "• Clientes sem chamado recebem 0 nos sinais de atendimento.  \n"
        "• Correlação não implica causalidade: o score prioriza contatos, não prova que o cliente vai sair."
    )
