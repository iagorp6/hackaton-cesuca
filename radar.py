"""Cálculo do score de risco de churn (Radar de Churn).

Toda a lógica de dados fica aqui, separada da interface, para poder ser testada
e explicada na apresentação. O score é uma soma ponderada de sinais simples e
explicáveis. Não é um modelo preditivo treinado: os dados são sintéticos e não
há rótulo de churn real, então a abordagem é uma regra de negócio transparente.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
MESES = ["2026-07", "2026-08", "2026-09"]


@dataclass
class Pesos:
    queda_uso: float = 35.0
    pendentes: float = 25.0
    satisfacao: float = 25.0
    tempo: float = 15.0

    def total(self) -> float:
        return self.queda_uso + self.pendentes + self.satisfacao + self.tempo


def carregar_dados(data_dir: Path = DATA_DIR):
    clientes = pd.read_csv(data_dir / "clientes.csv")
    clientes["data_cadastro"] = pd.to_datetime(clientes["data_cadastro"], format="%m/%d/%Y")

    atend = pd.read_csv(data_dir / "atendimentos.csv")
    atend["data_abertura"] = pd.to_datetime(atend["data_abertura"])

    uso = pd.read_csv(data_dir / "uso_servicos.csv")
    return clientes, atend, uso


def problemas_qualidade(clientes, atend, uso) -> pd.DataFrame:
    """Lista inconsistências encontradas nos dados (vira transparência no pitch)."""
    itens = [
        ("uso_servicos", "operacoes_realizadas maior que acessos",
         int((uso["operacoes_realizadas"] > uso["acessos"]).sum())),
        ("uso_servicos", "acessos = 0 no mês", int((uso["acessos"] == 0).sum())),
        ("uso_servicos", "cliente trocou de serviço entre meses",
         int((uso.groupby("cliente_id")["servico"].nunique() > 1).sum())),
        ("atendimentos", "chamados pendentes (sem tempo e sem nota)",
         int((atend["status"] == "Pendente").sum())),
        ("clientes", "clientes sem nenhum atendimento",
         int(len(set(clientes["cliente_id"]) - set(atend["cliente_id"])))),
        ("clientes", "data_cadastro em M/D/AAAA (dicionário diz AAAA-MM-DD)", len(clientes)),
    ]
    return pd.DataFrame(itens, columns=["arquivo", "problema", "ocorrencias"])


def calcular_radar(clientes, atend, uso, pesos: Pesos | None = None) -> pd.DataFrame:
    pesos = pesos or Pesos()

    # Uso: acessos por mês por cliente
    piv = uso.pivot_table(index="cliente_id", columns="mes", values="acessos", aggfunc="sum")
    piv = piv.reindex(columns=MESES).fillna(0)
    piv.columns = ["acessos_jul", "acessos_ago", "acessos_set"]
    base = piv[["acessos_jul", "acessos_ago"]].mean(axis=1)
    queda = ((base - piv["acessos_set"]) / base.where(base > 0)).clip(lower=0, upper=1).fillna(0)
    piv["queda_uso_pct"] = (queda * 100).round(0)

    # Atendimentos
    resolvidos = atend[atend["status"] == "Resolvido"]
    ag = atend.groupby("cliente_id").agg(
        chamados=("atendimento_id", "count"),
        pendentes=("status", lambda s: int((s == "Pendente").sum())),
        pendentes_alta=("prioridade", lambda s: 0),
    )
    pend_alta = atend[(atend["status"] == "Pendente") & (atend["prioridade"] == "Alta")]
    ag["pendentes_alta"] = pend_alta.groupby("cliente_id").size().reindex(ag.index).fillna(0).astype(int)
    rs = resolvidos.groupby("cliente_id").agg(
        satisfacao_media=("satisfacao_1_a_5", "mean"),
        tempo_medio_min=("tempo_resolucao_min", "mean"),
    )

    df = clientes.set_index("cliente_id").join(piv).join(ag).join(rs)
    df[["chamados", "pendentes", "pendentes_alta"]] = df[["chamados", "pendentes", "pendentes_alta"]].fillna(0).astype(int)

    tempo_ref = resolvidos["tempo_resolucao_min"].mean()

    # Componentes normalizados 0..1
    c_queda = queda.reindex(df.index).fillna(0)
    c_pend = ((df["pendentes"] + df["pendentes_alta"]) / 3).clip(upper=1)  # Alta conta em dobro
    c_sat = ((5 - df["satisfacao_media"]) / 4).clip(0, 1).fillna(0)
    c_tempo = ((df["tempo_medio_min"] - tempo_ref) / tempo_ref).clip(0, 1).fillna(0)

    escala = 100 / pesos.total() if pesos.total() > 0 else 0
    df["pts_queda_uso"] = (c_queda * pesos.queda_uso * escala).round(1)
    df["pts_pendentes"] = (c_pend * pesos.pendentes * escala).round(1)
    df["pts_satisfacao"] = (c_sat * pesos.satisfacao * escala).round(1)
    df["pts_tempo"] = (c_tempo * pesos.tempo * escala).round(1)
    df["score"] = df[["pts_queda_uso", "pts_pendentes", "pts_satisfacao", "pts_tempo"]].sum(axis=1).round(0).astype(int)

    df["faixa"] = pd.cut(df["score"], bins=[-1, 24, 44, 100], labels=["Baixo", "Médio", "Alto"]).astype(str)
    df["motivos"] = df.apply(_motivos, axis=1, tempo_ref=tempo_ref)
    df["acao_sugerida"] = df.apply(_acao, axis=1)
    df["satisfacao_media"] = df["satisfacao_media"].round(2)
    df["tempo_medio_min"] = df["tempo_medio_min"].round(0)

    return df.reset_index().sort_values("score", ascending=False)


def _motivos(r, tempo_ref: float) -> str:
    m = []
    if r["queda_uso_pct"] >= 30:
        m.append(f"uso caiu {int(r['queda_uso_pct'])}% em set")
    if r["pendentes"] > 0:
        txt = f"{r['pendentes']} chamado(s) pendente(s)"
        if r["pendentes_alta"]:
            txt += f", {r['pendentes_alta']} de prioridade Alta"
        m.append(txt)
    if pd.notna(r["satisfacao_media"]) and r["satisfacao_media"] <= 3:
        m.append(f"satisfação média {r['satisfacao_media']:.1f}")
    if pd.notna(r["tempo_medio_min"]) and r["tempo_medio_min"] > tempo_ref * 1.3:
        m.append(f"tempo de resolução {int(r['tempo_medio_min'])} min (média {int(tempo_ref)})")
    if r["chamados"] == 0:
        m.append("sem histórico de atendimento")
    return "; ".join(m) if m else "sem sinais relevantes"


def _acao(r) -> str:
    if r["pendentes_alta"] > 0:
        return "Escalar pendência Alta e ligar para o cliente hoje"
    if r["pendentes"] > 0 and r["faixa"] == "Alto":
        return "Fechar pendências e agendar contato do CS"
    if r["queda_uso_pct"] >= 50:
        return "Oferecer treinamento / onboarding do serviço"
    if pd.notna(r["satisfacao_media"]) and r["satisfacao_media"] <= 2.5:
        return "Contato de recuperação com gestor da conta"
    if r["faixa"] == "Médio":
        return "Monitorar e enviar pesquisa rápida de satisfação"
    return "Sem ação imediata"


def mensagem_retencao(r) -> str:
    """Rascunho de mensagem para o time de CS (template, sem dependência de API)."""
    linhas = [
        f"Olá, equipe da {r['nome_ficticio']}!",
        "",
        "Aqui é do time de Sucesso do Cliente. Estamos acompanhando sua conta de perto e queremos garantir "
        "que vocês estejam aproveitando ao máximo nossas soluções.",
    ]
    if r["pendentes"] > 0:
        linhas.append(f"Vimos que há {r['pendentes']} solicitação(ões) em aberto e já priorizamos o retorno.")
    if r["queda_uso_pct"] >= 30:
        linhas.append("Notamos uma redução no uso recente e gostaríamos de oferecer uma sessão rápida de orientação, sem custo.")
    if pd.notna(r["satisfacao_media"]) and r["satisfacao_media"] <= 3:
        linhas.append("Sua opinião sobre os últimos atendimentos é muito importante, e queremos entender como melhorar.")
    linhas += ["", "Podemos agendar 15 minutos esta semana?", "", "Abraço,", "Time de Sucesso do Cliente"]
    return "\n".join(linhas)
