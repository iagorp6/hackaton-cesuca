import pandas as pd
import plotly.express as px
import streamlit as st

from apelidos import aplicar_apelidos
from estilo import (AMBAR, AZUL_CLARO, CORES_RISCO, DESTAQUE, VERDE, VERMELHO, aplicar_estilo, barras_html,
                    cabecalho_pagina, cartao, marca, rotulo_menu)
from radar import Pesos, calcular_radar, carregar_dados, mensagem_retencao, problemas_qualidade
from triagem import fila_repriorizada, llm_disponivel, motor_llm, triar, OLLAMA_API_KEY, OLLAMA_MODEL

st.set_page_config(page_title="Vértice Desk · Central de Atendimento", page_icon="vertice-icon.svg", layout="wide",
                   initial_sidebar_state="expanded")
aplicar_estilo()


@st.cache_data
def dados():
    return carregar_dados()


clientes, atend, uso = dados()

# ---------------- Menu lateral ----------------
marca()
PAGINAS = {
    "painel": ":material/space_dashboard: Painel do mês",
    "chamado": ":material/support_agent: Novo chamado",
    "fila": ":material/format_list_numbered: Fila de atendimento",
    "risco": ":material/notifications_active: Clientes em risco",
    "ficha": ":material/person_search: Ficha do cliente",
    "processo": ":material/swap_horiz: Processo",
    "relatorios": ":material/insights: Relatórios",
    "qualidade": ":material/fact_check: Qualidade dos dados",
}
pagina = st.sidebar.radio("Menu", list(PAGINAS), format_func=PAGINAS.get, key="pagina",
                          label_visibility="collapsed")

rotulo_menu("Configurações")
apelidos_on = st.sidebar.toggle("Nomes lúdicos dos clientes", value=True,
                                help="Só muda o nome exibido. O ID (C001...) e os CSV originais não mudam.")
if apelidos_on:
    clientes = aplicar_apelidos(clientes)
with st.sidebar.expander("Pesos do score de risco"):
    st.caption("Importância de cada sinal. O score é reescalado para 0 a 100.")
    pesos = Pesos(
        queda_uso=st.slider("Queda de uso", 0, 50, 35),
        pendentes=st.slider("Chamados pendentes", 0, 50, 25),
        satisfacao=st.slider("Satisfação baixa", 0, 50, 25),
        tempo=st.slider("Tempo de resolução alto", 0, 50, 15),
    )
st.sidebar.caption("Dados fictícios · Hackathon Data Cempro + Cesuca 2026")
if pesos.total() == 0:
    st.sidebar.error("Defina ao menos um peso maior que zero.")
    st.stop()

radar = calcular_radar(clientes, atend, uso, pesos)

ORDEM = ["Alto", "Médio", "Baixo"]
MESES = {"2026-07": "Jul", "2026-08": "Ago", "2026-09": "Set"}
resolvidos = atend[atend["status"] == "Resolvido"]
pendentes = atend[atend["status"] == "Pendente"]
n_alto = int((radar["faixa"] == "Alto").sum())
SELOS = ["Triagem ativa", f"{len(pendentes)} pendentes", f"{n_alto} clientes em risco alto"]

EXEMPLOS = {
    "Sistema fora do ar": "Bom dia, o Sistema Beta parou desde cedo e nenhum usuário consegue lançar pedidos. Estamos com o faturamento parado, é urgente!",
    "Senha bloqueada no app": "Não consigo entrar no aplicativo pelo celular, diz que a senha está bloqueada.",
    "Portal lento": "O portal está muito lento hoje, as telas demoram mais de 1 minuto pra carregar.",
    "Sugestão de relatório": "Seria bom se o relatório mensal pudesse ser exportado em Excel, quando puderem.",
    "(escrever o meu)": "",
}

# ================= Painel do mês =================
if pagina == "painel":
    cabecalho_pagina("Painel do mês", "Fechamento operacional e saúde da carteira", SELOS)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Chamados no período", len(atend))
    k2.metric("Pendentes", len(pendentes), f"{len(pendentes) / len(atend) * 100:.0f}% do total", delta_color="off")
    k3.metric("Satisfação média", f"{atend['satisfacao_1_a_5'].mean():.1f} / 5")
    k4.metric("Clientes em risco alto", n_alto, f"{n_alto / len(radar) * 100:.0f}% da base", delta_color="inverse")
    st.write("")

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        with cartao("Evolução", "Chamados e pendências", "Comparação mensal do volume de suporte."):
            m = atend.assign(mes=atend["data_abertura"].astype(str).str[:7])
            evo = (m.groupby("mes").agg(Chamados=("atendimento_id", "count"),
                                        Pendentes=("status", lambda s: int((s == "Pendente").sum())))
                   .reindex(list(MESES)).fillna(0).rename(index=MESES).reset_index())
            fig = px.line(evo, x="mes", y=["Chamados", "Pendentes"], markers=True, text="value",
                          color_discrete_sequence=[DESTAQUE, AMBAR], labels={"mes": "", "value": ""})
            fig.update_traces(textposition="top center", line=dict(width=3), marker=dict(size=9))
            fig.update_traces(selector=dict(name="Pendentes"), line=dict(dash="dash"))
            st.plotly_chart(fig, width="stretch")
    with c2:
        with cartao("Adoção", "Uso dos serviços", "Acessos e operações dos 100 clientes."):
            u = (uso.groupby("mes")[["acessos", "operacoes_realizadas"]].sum().reindex(list(MESES)).fillna(0)
                 .rename(index=MESES).reset_index().rename(columns={"acessos": "Acessos", "operacoes_realizadas": "Operações"}))
            fig = px.bar(u, x="mes", y=["Acessos", "Operações"], barmode="group", text_auto=",.0f",
                         color_discrete_sequence=[VERDE, AZUL_CLARO], labels={"mes": "", "value": ""})
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, width="stretch")

    st.write("")
    c3, c4 = st.columns([3, 2], gap="medium")
    with c3:
        with cartao("Alertas", "Assuntos que pressionam o suporte", "Pendentes não entram no cálculo de tempo ou satisfação."):
            notas = resolvidos.dropna(subset=["satisfacao_1_a_5"])
            tab = pd.DataFrame({
                "Chamados": atend.groupby("assunto").size(),
                "Pendentes": pendentes.groupby("assunto").size(),
                "Tempo médio (min)": resolvidos.groupby("assunto")["tempo_resolucao_min"].mean().round(1),
                "Notas 1–2": notas.groupby("assunto")["satisfacao_1_a_5"].apply(lambda s: (s <= 2).mean() * 100).round(1),
            }).fillna(0).sort_values(["Pendentes", "Chamados"], ascending=False)
            tab["Pendentes"] = tab["Pendentes"].astype(int)
            st.dataframe(tab.reset_index(names="Assunto"), hide_index=True, width="stretch",
                         column_config={"Notas 1–2": st.column_config.ProgressColumn(
                             "Notas 1–2", min_value=0, max_value=100, format="%.1f%%")})
    with c4:
        with cartao("Prioridade", "Tempo médio de resolução", "Quem é urgente deveria esperar menos."):
            tp = resolvidos.groupby("prioridade")["tempo_resolucao_min"].agg(["mean", "count"]).reindex(["Alta", "Normal", "Baixa"])
            barras_html([(p, float(r["mean"]), f"{r['mean']:.1f} min", f"{int(r['count'])} chamados resolvidos")
                         for p, r in tp.dropna().iterrows()], cor=VERMELHO)
            st.caption("Hoje a prioridade Alta demora mais que a Baixa: a fila não respeita a urgência.")

# ================= Novo chamado =================
elif pagina == "chamado":
    motor = motor_llm()
    nome_motor = {"claude": "IA: Claude", "ollama": f"IA: {'Ollama Cloud' if OLLAMA_API_KEY else 'Ollama local'}"}.get(
        motor, "Classificação por regras")
    cabecalho_pagina("Novo chamado", "O chamado entra, é classificado e já sai priorizado e encaminhado.",
                     [nome_motor, f"{len(pendentes)} pendentes"])

    with cartao("Abertura", "Dados do chamado"):
        t1, t2 = st.columns([1, 2], gap="medium")
        with t1:
            ops_cli = radar["cliente_id"] + " · " + radar["nome_ficticio"] + " · risco " + radar["faixa"]
            cli_sel = st.selectbox("Solicitante (cliente)", ops_cli, key="tri_cli")
            exemplo = st.selectbox("Modelo de chamado", list(EXEMPLOS), key="tri_ex")
            usar_llm = st.toggle("Classificar com IA", value=motor is not None, disabled=motor is None)
        with t2:
            texto = st.text_area("Descrição", EXEMPLOS[exemplo], height=150, key=f"tri_txt_{exemplo}")
        abrir = st.button("Abrir chamado", type="primary", disabled=not texto.strip())

    if abrir:
        crow = radar[radar["cliente_id"] == cli_sel.split(" · ")[0]].iloc[0]
        with st.spinner("Registrando e classificando..."):
            res = triar(texto, crow, atend, uso, usar_llm=usar_llm)
        if res.aviso:
            st.warning(res.aviso)
        cli_nome = cli_sel.split(" · ")[1]
        prox_id = f"A{int(atend['atendimento_id'].str[1:].astype(int).max()) + 1:04d}"
        st.write("")
        sev = f"{res.nivel_emoji} Severidade {res.nivel}" if res.nivel else "Triagem concluída"
        meta = f" · 1º atendimento em até {res.meta_1o_atendimento_min} min" if res.meta_1o_atendimento_min else ""
        with cartao("Resultado da triagem", sev + meta, "; ".join(map(str, res.motivos_nivel or []))):
            st.markdown(f'<div class="vd-ticket"><b>Chamado #{prox_id}</b> · {cli_nome} · aberto em {pd.Timestamp.now():%d/%m/%Y %H:%M}<br>'
                        f'<span class="vd-tag">Status: Novo</span><span class="vd-tag">Fila: {res.fila}</span>'
                        f'<span class="vd-tag">Serviço: {res.servico}</span><span class="vd-tag">Assunto: {res.assunto}</span>'
                        f'</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("1 · Classificou", res.assunto)
            m2.metric("Serviço", res.servico)
            mudou = res.prioridade_final != res.prioridade_informada
            m3.metric("2 · Priorizou", res.prioridade_final,
                      f"era {res.prioridade_informada}" if mudou else "sem ajuste", delta_color="inverse" if mudou else "off")
            m4.metric("3 · Encaminhou", res.fila,
                      f"~{res.tempo_estimado_min} min (mediana)" if res.tempo_estimado_min else None, delta_color="off")
            st.markdown(f"**Justificativa:** {res.justificativa}  \n**Histórico do cliente:** {res.motivo_ajuste}  \n"
                        f"<small>Classificado por: {res.motor}</small>", unsafe_allow_html=True)
        st.write("")
        r1, r2 = st.columns([1, 1], gap="medium")
        with r1:
            with cartao("4 · Respondeu", "Resposta ao solicitante", "Rascunho pronto para o atendente revisar."):
                st.text_area("Resposta", res.resposta_sugerida, height=200, label_visibility="collapsed")
        with r2:
            with cartao("Histórico", "Chamados relacionados", "Do próprio cliente primeiro, depois mesmo assunto e serviço."):
                st.dataframe(res.similares, hide_index=True, width="stretch", height=200)

# ================= Fila =================
elif pagina == "fila":
    fila = fila_repriorizada(atend, radar)
    cabecalho_pagina("Fila de atendimento", "Pendentes ordenados por urgência, risco do cliente e dias em aberto.", SELOS)
    f1, f2, f3 = st.columns(3)
    f1.metric("Pendentes", len(fila))
    f2.metric("De clientes em risco Alto/Médio", int(fila["faixa"].isin(["Alto", "Médio"]).sum()))
    f3.metric("Subiram 5+ posições", int((fila["mudanca"] >= 5).sum()))
    st.write("")
    with cartao("Fila repriorizada", "Ordem de atendimento", "\"Subiu\" positivo = o chamado ganhou posições em relação à ordem de chegada."):
        st.dataframe(fila, hide_index=True, width="stretch", height=520,
                     column_config={
                         "posicao_nova": "Posição", "posicao_original": "Posição antes", "mudanca": "Subiu",
                         "atendimento_id": "Chamado", "cliente_id": "ID", "nome_ficticio": "Cliente",
                         "faixa": "Risco", "score": "Score", "prioridade": "Prioridade", "assunto": "Assunto",
                         "servico": "Serviço", "dias_aberto": "Dias em aberto",
                         "indice_urgencia": st.column_config.ProgressColumn("Urgência", min_value=0, max_value=110, format="%.0f")})

# ================= Clientes em risco =================
elif pagina == "risco":
    cabecalho_pagina("Clientes em risco", "Quem pode cancelar, por quê, e o que o relacionamento deve fazer.", SELOS)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with cartao("Carteira", "Clientes por faixa de risco"):
            dist = radar["faixa"].value_counts().reindex(ORDEM).fillna(0).reset_index()
            dist.columns = ["faixa", "clientes"]
            st.plotly_chart(px.bar(dist, x="faixa", y="clientes", color="faixa", color_discrete_map=CORES_RISCO,
                                   text_auto=True, labels={"faixa": "", "clientes": ""}).update_layout(showlegend=False),
                            width="stretch")
    with c2:
        with cartao("Segmentos", "Risco por setor"):
            seg = radar.groupby(["setor", "faixa"]).size().reset_index(name="clientes")
            st.plotly_chart(px.bar(seg, x="setor", y="clientes", color="faixa", color_discrete_map=CORES_RISCO,
                                   category_orders={"faixa": ORDEM}, labels={"setor": "", "clientes": ""}),
                            width="stretch")
    st.write("")
    with cartao("Ranking", "Lista para o time de relacionamento", "Filtre e exporte para acionar os clientes."):
        f1, f2, f3, f4 = st.columns(4)
        faixas = f1.multiselect("Faixa", ORDEM, default=["Alto", "Médio"])
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
        cols = ["cliente_id", "nome_ficticio"] + (["nome_original"] if "nome_original" in r else []) + [
            "score", "faixa", "motivos", "acao_sugerida", "setor", "porte", "cidade",
            "acessos_jul", "acessos_ago", "acessos_set", "pendentes", "satisfacao_media"]
        st.dataframe(r[cols], hide_index=True, width="stretch",
                     column_config={"score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d")})
        st.download_button("Exportar lista (CSV)", r[cols].to_csv(index=False).encode("utf-8"),
                           "radar_churn.csv", "text/csv")

# ================= Ficha do cliente =================
elif pagina == "ficha":
    cabecalho_pagina("Ficha do cliente", "Composição do risco, uso e histórico de um cliente.")
    opcoes = radar["cliente_id"] + " · " + radar["nome_ficticio"] + " · score " + radar["score"].astype(str)
    escolha = st.selectbox("Cliente (ordenado por risco)", opcoes)
    cid = escolha.split(" · ")[0]
    row = radar[radar["cliente_id"] == cid].iloc[0]

    a, b, c = st.columns([1, 1, 2], gap="medium")
    a.metric("Score de risco", int(row["score"]), row["faixa"], delta_color="off")
    b.metric("Chamados", int(row["chamados"]), f"{int(row['pendentes'])} pendente(s)", delta_color="off")
    with c:
        with cartao("Perfil", str(row["nome_ficticio"]), f"{row['porte']} · {row['setor']} · {row['cidade']}"):
            st.markdown(f"**Motivos:** {row['motivos']}  \n**Ação sugerida:** {row['acao_sugerida']}")
    st.write("")
    g1, g2 = st.columns(2, gap="medium")
    with g1:
        with cartao("Composição", "De onde vem o score"):
            comp = pd.DataFrame({
                "sinal": ["Queda de uso", "Pendentes", "Satisfação", "Tempo de resolução"],
                "pontos": [row["pts_queda_uso"], row["pts_pendentes"], row["pts_satisfacao"], row["pts_tempo"]],
            })
            st.plotly_chart(px.bar(comp, x="pontos", y="sinal", orientation="h", text_auto=".0f",
                                   labels={"pontos": "", "sinal": ""}), width="stretch")
    with g2:
        with cartao("Uso", "Uso mensal"):
            hist = uso[uso["cliente_id"] == cid].assign(mes=lambda d: d["mes"].map(MESES).fillna(d["mes"]))
            st.plotly_chart(px.line(hist, x="mes", y=["acessos", "operacoes_realizadas"], markers=True,
                                    hover_data=["servico"], color_discrete_sequence=[DESTAQUE, AMBAR],
                                    labels={"mes": "", "value": ""}).update_xaxes(type="category"),
                            width="stretch")
    st.write("")
    h1, h2 = st.columns([3, 2], gap="medium")
    with h1:
        with cartao("Histórico", "Chamados do cliente"):
            st.dataframe(atend[atend["cliente_id"] == cid].sort_values("data_abertura", ascending=False),
                         hide_index=True, width="stretch")
    with h2:
        with cartao("Retenção", "Mensagem sugerida", "Copie e envie pelo canal do cliente."):
            st.text_area("Mensagem", mensagem_retencao(row), height=260, label_visibility="collapsed")

# ================= Processo =================
elif pagina == "processo":
    cabecalho_pagina("Processo: antes x depois", "O ganho não é o código: é o atendimento mais simples e automático.")
    med = resolvidos.groupby("prioridade")["tempo_resolucao_min"].median().reindex(["Alta", "Normal", "Baixa"])
    excesso_h = (resolvidos.loc[resolvidos["prioridade"] == "Alta", "tempo_resolucao_min"] - med["Baixa"]).clip(lower=0).sum() / 60
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Canais de entrada", atend["canal"].nunique(), help="WhatsApp, E-mail, Portal e Telefone, sem porta única")
    k2.metric("Chamados pendentes", len(pendentes))
    k3.metric("Mediana Alta x Baixa", f"{med['Alta']:.0f} x {med['Baixa']:.0f} min", "SLA invertido", delta_color="inverse")
    k4.metric("Espera extra dos chamados Alta", f"{excesso_h:.0f} h",
              help="Soma do tempo que cada chamado Alta passou da mediana dos chamados Baixa")
    st.write("")
    a, b = st.columns(2, gap="medium")
    with a:
        with cartao("Hoje", "Processo manual (AS-IS)"):
            st.markdown(
                "1. Chamado chega por **4 canais** diferentes\n"
                "2. Atendente **lê e classifica à mão** (serviço, assunto)\n"
                "3. Prioridade **definida no feeling**, sem critério\n"
                "4. Encaminha para a fila manualmente\n"
                "5. Fila por **ordem de chegada**, sem olhar o cliente\n"
                "6. Escreve a primeira resposta do zero\n"
                "7. CS só descobre o cliente insatisfeito **quando ele cancela**")
    with b:
        with cartao("Com o Vértice Desk", "Processo automático (TO-BE)"):
            st.markdown(
                "1. Chamado entra (qualquer canal) e vai para **um único passo de triagem**\n"
                "2. IA classifica **serviço e assunto automaticamente**\n"
                "3. Prioridade por **regra única**: impacto do texto + risco do cliente\n"
                "4. Fila de destino definida **automaticamente**\n"
                "5. Fila **repriorizada** por prioridade, risco e dias em aberto\n"
                "6. **Primeira resposta sugerida** pronta para enviar\n"
                "7. Radar avisa o CS **antes** do cancelamento, com ação sugerida")
    st.write("")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with cartao("Evidência", "Prioridade sem critério", "Relatório é marcado Alta mais vezes que Erro no sistema."):
            alta_assunto = (atend.assign(alta=atend["prioridade"].eq("Alta"))
                            .groupby("assunto")["alta"].mean().mul(100).round(0).sort_values().reset_index())
            st.plotly_chart(px.bar(alta_assunto, x="alta", y="assunto", orientation="h", text_auto=".0f",
                                   labels={"alta": "% marcado como Alta", "assunto": ""}), width="stretch")
    with c2:
        with cartao("Evidência", "SLA invertido", "Mediana do tempo de resolução por prioridade."):
            st.plotly_chart(px.bar(med.reset_index(), x="prioridade", y="tempo_resolucao_min", text_auto=".0f",
                                   color_discrete_sequence=[VERMELHO],
                                   labels={"tempo_resolucao_min": "minutos", "prioridade": ""}), width="stretch")
    st.write("")
    with cartao("Ganho estimado", "Etapas manuais eliminadas",
                "Premissas ajustáveis: os dados não trazem o tempo real de cada etapa."):
        e1, e2 = st.columns([1, 2], gap="medium")
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
            st.success(f"**~{etapas['horas_mes_liberadas'].sum():.0f} horas/mês** de triagem manual "
                       f"liberadas para resolver chamados, com {vol} chamados/mês.")

# ================= Relatórios =================
elif pagina == "relatorios":
    cabecalho_pagina("Relatórios", "Insights para o time de suporte, que alimentam os sinais do radar.")
    o1, o2 = st.columns(2, gap="medium")
    with o1:
        with cartao("Satisfação", "Assunto: tempo x satisfação", "Tamanho da bolha = número de chamados."):
            t_ass = resolvidos.groupby("assunto").agg(tempo=("tempo_resolucao_min", "mean"),
                                                      satisfacao=("satisfacao_1_a_5", "mean"),
                                                      chamados=("atendimento_id", "count")).reset_index()
            st.plotly_chart(px.scatter(t_ass, x="tempo", y="satisfacao", size="chamados", text="assunto",
                                       labels={"tempo": "tempo médio (min)", "satisfacao": "nota média"})
                            .update_traces(textposition="top center"), width="stretch")
    with o2:
        with cartao("Serviços", "Satisfação média por serviço"):
            sat_serv = resolvidos.groupby("servico")["satisfacao_1_a_5"].mean().round(2).sort_values().reset_index()
            st.plotly_chart(px.bar(sat_serv, x="satisfacao_1_a_5", y="servico", orientation="h", text_auto=".2f",
                                   labels={"satisfacao_1_a_5": "", "servico": ""}), width="stretch")
    st.write("")
    o3, o4 = st.columns(2, gap="medium")
    with o3:
        with cartao("Pendências", "Pendências por assunto e prioridade"):
            pend = pendentes.groupby(["prioridade", "assunto"]).size().reset_index(name="pendentes")
            st.plotly_chart(px.bar(pend, x="assunto", y="pendentes", color="prioridade",
                                   color_discrete_map={"Alta": VERMELHO, "Normal": AMBAR, "Baixa": VERDE},
                                   labels={"assunto": "", "pendentes": ""}), width="stretch")
    with o4:
        with cartao("Carteira", "Risco por porte"):
            seg = radar.groupby(["porte", "faixa"]).size().reset_index(name="clientes")
            st.plotly_chart(px.bar(seg, x="porte", y="clientes", color="faixa", color_discrete_map=CORES_RISCO,
                                   category_orders={"faixa": ORDEM, "porte": ["Micro", "Pequena", "Média"]},
                                   labels={"porte": "", "clientes": ""}), width="stretch")

# ================= Qualidade =================
elif pagina == "qualidade":
    cabecalho_pagina("Qualidade dos dados", "Problemas encontrados nos arquivos fornecidos e como o radar lida com eles.")
    with cartao("Auditoria", "Inconsistências encontradas"):
        st.dataframe(problemas_qualidade(clientes, atend, uso), hide_index=True, width="stretch")
    st.write("")
    with cartao("Método", "Como os dados foram tratados"):
        st.markdown(
            "- Queda de uso compara set com a média de jul e ago, somando todos os serviços do cliente.\n"
            "- Pendentes não têm nota nem tempo, então entram só no sinal de pendências.\n"
            "- Clientes sem chamado recebem 0 nos sinais de atendimento.\n"
            "- Correlação não implica causalidade: o score prioriza contatos, não prova que o cliente vai sair.")
