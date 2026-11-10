import pandas as pd
import plotly.express as px
import streamlit as st

from estilo import aplicar_estilo, topo
from radar import Pesos, calcular_radar, carregar_dados, mensagem_retencao, problemas_qualidade
from triagem import fila_repriorizada, llm_disponivel, motor_llm, triar, OLLAMA_API_KEY, OLLAMA_MODEL

st.set_page_config(page_title="Vértice Desk · Central de Atendimento", page_icon="🎫", layout="wide",
                   initial_sidebar_state="collapsed")
aplicar_estilo()


@st.cache_data
def dados():
    return carregar_dados()


clientes, atend, uso = dados()

st.sidebar.markdown("### Vértice Desk")
st.sidebar.caption("Central de Atendimento · Vértice Sistemas")

# ---------------- Sidebar: pesos ajustáveis ----------------
st.sidebar.subheader("Configuração do risco do cliente")
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

topo(chips=[("Pendentes", int((atend["status"] == "Pendente").sum())),
            ("Clientes em risco alto", int((radar["faixa"] == "Alto").sum()))])
st.caption("Vértice Sistemas · Dados fictícios do Hackathon Data Cempro + Cesuca 2026")

aba_triagem, aba_fila, aba_proc, aba_geral, aba_rank, aba_cliente, aba_ops, aba_dados = st.tabs(
    ["Novo chamado", "Fila de atendimento", "Processo (antes x depois)", "Painel", "Clientes em risco", "Ficha do cliente",
     "Relatórios", "Qualidade dos dados"]
)

EXEMPLOS = {
    "(escrever o meu)": "",
    "Sistema fora do ar": "Bom dia, o Sistema Beta parou desde cedo e nenhum usuário consegue lançar pedidos. Estamos com o faturamento parado, é urgente!",
    "Senha bloqueada no app": "Não consigo entrar no aplicativo pelo celular, diz que a senha está bloqueada.",
    "Portal lento": "O portal está muito lento hoje, as telas demoram mais de 1 minuto pra carregar.",
    "Sugestão de relatório": "Seria bom se o relatório mensal pudesse ser exportado em Excel, quando puderem.",
}

# ---------------- Processo: antes x depois ----------------
with aba_proc:
    st.markdown("### O foco não é o código, é o **processo de atendimento** que fica mais simples e automático.")
    res_p = atend[atend["status"] == "Resolvido"]
    med = res_p.groupby("prioridade")["tempo_resolucao_min"].median().reindex(["Alta", "Normal", "Baixa"])
    pend_p = atend[atend["status"] == "Pendente"]
    excesso_h = (res_p.loc[res_p["prioridade"] == "Alta", "tempo_resolucao_min"] - med["Baixa"]).clip(lower=0).sum() / 60

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Canais de entrada", atend["canal"].nunique(), help="WhatsApp, E-mail, Portal e Telefone, sem porta única")
    k2.metric("Chamados pendentes", len(pend_p))
    k3.metric("Mediana Alta x Baixa", f"{med['Alta']:.0f} x {med['Baixa']:.0f} min", "SLA invertido", delta_color="inverse")
    k4.metric("Espera extra dos chamados Alta", f"{excesso_h:.0f} h",
              help="Soma do tempo que cada chamado Alta passou da mediana dos chamados Baixa")

    a, b = st.columns(2)
    with a:
        st.markdown("#### Hoje (AS-IS)")
        st.markdown(
            "1. Chamado chega por **4 canais** diferentes\n"
            "2. Atendente **lê e classifica à mão** (serviço, assunto)\n"
            "3. Prioridade **definida no feeling**, sem critério\n"
            "4. Encaminha para a fila manualmente\n"
            "5. Fila por **ordem de chegada**, sem olhar o cliente\n"
            "6. Escreve a primeira resposta do zero\n"
            "7. CS só descobre o cliente insatisfeito **quando ele cancela**"
        )
    with b:
        st.markdown("#### Com o Vértice Desk (TO-BE)")
        st.markdown(
            "1. Chamado entra (qualquer canal) e vai para **um único passo de triagem**\n"
            "2. IA classifica **serviço e assunto automaticamente**\n"
            "3. Prioridade por **regra única**: impacto do texto + risco de churn do cliente\n"
            "4. Fila de destino definida **automaticamente**\n"
            "5. Fila **repriorizada** por prioridade, risco e dias em aberto\n"
            "6. **Primeira resposta sugerida** pronta para enviar\n"
            "7. Radar avisa o CS **antes** do cancelamento, com ação sugerida"
        )

    st.markdown("#### Evidência: a priorização manual não segue critério")
    c1, c2 = st.columns(2)
    alta_assunto = (atend.assign(alta=atend["prioridade"].eq("Alta"))
                    .groupby("assunto")["alta"].mean().mul(100).round(0).sort_values().reset_index())
    c1.plotly_chart(px.bar(alta_assunto, x="alta", y="assunto", orientation="h",
                           labels={"alta": "% marcado como Alta", "assunto": ""},
                           title="Relatório é marcado Alta mais vezes que Erro"), width="stretch")
    c2.plotly_chart(px.bar(med.reset_index(), x="prioridade", y="tempo_resolucao_min",
                           labels={"tempo_resolucao_min": "mediana (min)", "prioridade": ""},
                           title="Quem é urgente espera mais (SLA invertido)"), width="stretch")

    st.markdown("#### Etapas manuais eliminadas (estimativa)")
    st.caption("Premissas ajustáveis. Não temos o tempo real de cada etapa nos dados, então os minutos são hipóteses para discussão.")
    e1, e2 = st.columns([1, 2])
    with e1:
        vol = st.number_input("Chamados por mês", 50, 100000, len(atend) // 3 * 10, step=50,
                              help="Base: 300 chamados em 3 meses na amostra; ajuste para o volume real")
        m_class = st.number_input("Min. para ler e classificar", 0.0, 30.0, 3.0, 0.5)
        m_prio = st.number_input("Min. para decidir prioridade e fila", 0.0, 30.0, 2.0, 0.5)
        m_resp = st.number_input("Min. para escrever 1ª resposta", 0.0, 30.0, 4.0, 0.5)
    etapas = pd.DataFrame({
        "etapa": ["Ler e classificar", "Prioridade e fila", "Primeira resposta"],
        "antes": ["Manual", "Manual, sem critério", "Manual, do zero"],
        "depois": ["Automática (IA)", "Automática (regra + risco)", "Rascunho pronto, só revisar"],
        "min_por_chamado": [m_class, m_prio, m_resp],
    })
    etapas["horas_mes_liberadas"] = (etapas["min_por_chamado"] * vol / 60).round(0)
    with e2:
        st.dataframe(etapas, hide_index=True, width="stretch")
        st.success(f"**~{etapas['horas_mes_liberadas'].sum():.0f} horas/mês** de trabalho manual de triagem "
                   f"liberadas para resolver chamados, com {vol} chamados/mês.")

# ---------------- Triagem IA ----------------
with aba_triagem:
    st.markdown("#### Abrir chamado")
    motor = motor_llm()
    st.caption({"claude": "Classificação automática: Claude (API)", "ollama": f"Classificação automática: {'Ollama Cloud' if OLLAMA_API_KEY else 'Ollama local'} ({OLLAMA_MODEL})"}.get(
        motor, "Classificação automática: regras por palavra-chave (sem LLM disponível)"))
    t1, t2 = st.columns([1, 2])
    with t1:
        ops_cli = radar["cliente_id"] + " · " + radar["nome_ficticio"] + " · risco " + radar["faixa"]
        cli_sel = st.selectbox("Solicitante (cliente)", ops_cli, key="tri_cli")
        exemplo = st.selectbox("Modelo de chamado", list(EXEMPLOS), key="tri_ex")
        usar_llm = st.toggle("Classificar com LLM", value=motor is not None, disabled=motor is None)
    with t2:
        texto = st.text_area("Descrição", EXEMPLOS[exemplo], height=150, key=f"tri_txt_{exemplo}")
    if st.button("Abrir chamado", type="primary", disabled=not texto.strip()):
        crow = radar[radar["cliente_id"] == cli_sel.split(" · ")[0]].iloc[0]
        with st.spinner("Registrando e classificando..."):
            res = triar(texto, crow, atend, uso, usar_llm=usar_llm)
        if res.aviso:
            st.warning(res.aviso)
        cli_nome = cli_sel.split(" · ")[1]
        prox_id = f"A{int(atend['atendimento_id'].str[1:].astype(int).max()) + 1:04d}"
        st.markdown(f'<div class="vd-ticket"><b>Chamado #{prox_id}</b> · {cli_nome} · aberto em {pd.Timestamp.now():%d/%m/%Y %H:%M}<br>'
                    f'<span class="vd-tag">Status: Novo</span><span class="vd-tag">Fila: {res.fila}</span>'
                    f'<span class="vd-tag">Serviço: {res.servico}</span><span class="vd-tag">Assunto: {res.assunto}</span>'
                    f'</div>', unsafe_allow_html=True)
        if res.nivel:
            meta = f" · 1º atendimento em até {res.meta_1o_atendimento_min} min" if res.meta_1o_atendimento_min else ""
            st.subheader(f"{res.nivel_emoji} Severidade: {res.nivel}{meta}")
            if res.motivos_nivel:
                st.caption("Motivos: " + "; ".join(map(str, res.motivos_nivel)))
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Assunto", res.assunto)
        m2.metric("Serviço", res.servico)
        mudou = res.prioridade_final != res.prioridade_informada
        m3.metric("Prioridade final", res.prioridade_final,
                  f"era {res.prioridade_informada}" if mudou else "sem ajuste", delta_color="inverse" if mudou else "off")
        m4.metric("Fila", res.fila, f"~{res.tempo_estimado_min} min (mediana histórica)" if res.tempo_estimado_min else None,
                  delta_color="off")
        st.markdown(f"**Justificativa:** {res.justificativa}  \n**Ajuste pelo histórico do cliente:** {res.motivo_ajuste}  \n"
                    f"<small>Classificado por: {res.motor}</small>", unsafe_allow_html=True)
        st.text_area("Resposta ao solicitante (rascunho para revisar)", res.resposta_sugerida, height=140)
        st.markdown("**Chamados relacionados** (do próprio cliente primeiro, depois mesmo assunto e serviço)")
        st.dataframe(res.similares, hide_index=True, width="stretch")

# ---------------- Fila repriorizada ----------------
with aba_fila:
    fila = fila_repriorizada(atend, radar)
    st.markdown("#### Fila de atendimento · pendentes")
    st.caption("Ordenada por prioridade informada + risco do cliente + dias em aberto. \"Subiu\" positivo = chamado ganhou posições.")
    f1, f2, f3 = st.columns(3)
    f1.metric("Pendentes", len(fila))
    f2.metric("Pendentes de clientes em risco Alto/Médio", int(fila["faixa"].isin(["Alto", "Médio"]).sum()))
    f3.metric("Chamados que subiram 5+ posições", int((fila["mudanca"] >= 5).sum()))
    st.dataframe(fila, hide_index=True, width="stretch",
                 column_config={
                     "posicao_nova": "Posição", "posicao_original": "Posição antes", "mudanca": "Subiu",
                     "atendimento_id": "Chamado", "cliente_id": "ID", "nome_ficticio": "Cliente",
                     "faixa": "Risco", "score": "Score", "prioridade": "Prioridade", "assunto": "Assunto",
                     "servico": "Serviço", "dias_aberto": "Dias em aberto",
                     "indice_urgencia": st.column_config.ProgressColumn("Urgência", min_value=0, max_value=110, format="%.0f")})

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
                               title="Clientes por faixa de risco"), width="stretch")
    with c2:
        st.plotly_chart(px.histogram(radar, x="score", nbins=20, title="Distribuição do score"),
                        width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        seg = radar.groupby(["setor", "faixa"]).size().reset_index(name="clientes")
        st.plotly_chart(px.bar(seg, x="setor", y="clientes", color="faixa", color_discrete_map=cores,
                               category_orders={"faixa": ordem}, title="Risco por setor"),
                        width="stretch")
    with c4:
        seg = radar.groupby(["porte", "faixa"]).size().reset_index(name="clientes")
        st.plotly_chart(px.bar(seg, x="porte", y="clientes", color="faixa", color_discrete_map=cores,
                               category_orders={"faixa": ordem, "porte": ["Micro", "Pequena", "Média"]},
                               title="Risco por porte"), width="stretch")

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

    cols = ["cliente_id", "nome_ficticio"] + (["nome_original"] if "nome_original" in r else []) + ["score", "faixa", "motivos", "acao_sugerida", "setor", "porte",
            "cidade", "acessos_jul", "acessos_ago", "acessos_set", "pendentes", "satisfacao_media"]
    st.dataframe(
        r[cols], hide_index=True, width="stretch",
        column_config={"score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d")},
    )
    st.download_button("Exportar lista para o CS (CSV)", r[cols].to_csv(index=False).encode("utf-8"),
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
                    width="stretch")
    hist = uso[uso["cliente_id"] == cid]
    g2.plotly_chart(px.line(hist, x="mes", y=["acessos", "operacoes_realizadas"], markers=True,
                            hover_data=["servico"], title="Uso mensal").update_xaxes(type="category"),
                    width="stretch")

    st.subheader("Chamados")
    st.dataframe(atend[atend["cliente_id"] == cid].sort_values("data_abertura", ascending=False),
                 hide_index=True, width="stretch")

    st.subheader("Mensagem de retenção (rascunho)")
    st.text_area("Copie e envie pelo canal do cliente", mensagem_retencao(row), height=260)

# ---------------- Operação ----------------
with aba_ops:
    res = atend[atend["status"] == "Resolvido"]
    st.markdown("Insights para o time de suporte, que alimentam os sinais do radar.")
    o1, o2 = st.columns(2)
    t_prio = res.groupby("prioridade")["tempo_resolucao_min"].mean().reindex(["Alta", "Normal", "Baixa"]).reset_index()
    o1.plotly_chart(px.bar(t_prio, x="prioridade", y="tempo_resolucao_min",
                           title="Tempo médio de resolução por prioridade (min)"), width="stretch")
    o1.warning("Chamados de prioridade **Alta** demoram mais que os de **Baixa**: a fila não respeita a prioridade.")
    t_ass = res.groupby("assunto").agg(tempo=("tempo_resolucao_min", "mean"),
                                       satisfacao=("satisfacao_1_a_5", "mean"),
                                       chamados=("atendimento_id", "count")).reset_index()
    o2.plotly_chart(px.scatter(t_ass, x="tempo", y="satisfacao", size="chamados", text="assunto",
                               title="Assunto: tempo x satisfação"), width="stretch")
    o3, o4 = st.columns(2)
    sat_serv = res.groupby("servico")["satisfacao_1_a_5"].mean().sort_values().reset_index()
    o3.plotly_chart(px.bar(sat_serv, x="satisfacao_1_a_5", y="servico", orientation="h",
                           title="Satisfação média por serviço"), width="stretch")
    pend = atend[atend["status"] == "Pendente"].groupby(["prioridade", "assunto"]).size().reset_index(name="pendentes")
    o4.plotly_chart(px.bar(pend, x="assunto", y="pendentes", color="prioridade",
                           title="Pendências por assunto e prioridade"), width="stretch")

# ---------------- Qualidade ----------------
with aba_dados:
    st.markdown("Problemas encontrados nos arquivos fornecidos e como o radar lida com eles.")
    st.dataframe(problemas_qualidade(clientes, atend, uso), hide_index=True, width="stretch")
    st.info(
        "• Queda de uso compara set com a média de jul e ago, somando todos os serviços do cliente.  \n"
        "• Pendentes não têm nota nem tempo, então entram só no sinal de pendências.  \n"
        "• Clientes sem chamado recebem 0 nos sinais de atendimento.  \n"
        "• Correlação não implica causalidade: o score prioriza contatos, não prova que o cliente vai sair."
    )
