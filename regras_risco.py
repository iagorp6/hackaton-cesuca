"""Níveis de severidade de chamados (ver contexto/modelo-classificacao-risco.md). Python puro."""
from __future__ import annotations

import re
import unicodedata

NIVEIS = ["Crítico", "Alto", "Médio", "Baixo", "Planejado"]
EMOJI = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢", "Planejado": "🔵"}
METAS = {  # (1º atendimento, resolução) em minutos
    "Crítico": (5, 60), "Alto": (15, 120), "Médio": (60, 240), "Baixo": (240, 480), "Planejado": (480, None),
}
# ordem de severidade para subir nível (Planejado < Baixo < Médio < Alto < Crítico)
_ORDEM = ["Planejado", "Baixo", "Médio", "Alto", "Crítico"]

SINAIS = {
    "Crítico": ["parou", "parado", "fora do ar", "caiu", "nao consigo faturar", "nao conseguimos faturar",
                "emitir nota", "notas estao sendo rejeitadas", "rejeitad", "todos os usuarios", "ninguem consegue",
                "caixa travou", "operacao parada", "caminhoes parados"],
    "Alto": ["erro", "varios usuarios", "perdi dados", "perda de dados", "nao fecha", "nao entram", "401",
             "integracao", "divergente", "saldo negativo", "encargos", "prazo", "cancelamento", "concorrente"],
    "Médio": ["lento", "lentidao", "travando", "demora", "senha", "bloquead", "acesso", "nao consigo entrar", "contornar"],
    "Baixo": ["como faco", "duvida", "instalar", "instalacao", "relatorio", "nao entendi", "nao sei", "tutorial"],
    "Planejado": ["sugestao", "seria bom", "melhoria", "quando puderem", "funcionalidade", "da para"],
}
_PRODUTOS = ["alfa", "beta", "portal", "app", "aplicativo", "erp", "fiscal", "pdv", "folha", "estoque", "financeiro", "bi", "api"]


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _subir(nivel: str, n: int = 1) -> str:
    return _ORDEM[min(_ORDEM.index(nivel) + n, len(_ORDEM) - 1)]


def classificar_nivel(texto: str, risco_cliente: str = "Baixo", dias_aberto: int = 0) -> dict:
    t = _norm(texto)
    nivel, motivos = None, []
    for nv in NIVEIS:  # do mais severo para o menos
        achou = [s for s in SINAIS[nv] if s in t]
        if achou:
            nivel = nv
            motivos.append(f"texto cita: {', '.join(achou[:3])}")
            break
    if nivel is None:
        nivel = "Baixo"
        motivos.append("sem sinal de urgência no texto")
    if risco_cliente == "Alto" and nivel != "Crítico":
        nivel = _subir(nivel)
        motivos.append("cliente em risco Alto de churn: +1 nível")
    if dias_aberto > 7 and nivel != "Crítico":
        nivel = _subir(nivel)
        motivos.append(f"aberto há {dias_aberto} dias: +1 nível")

    faltando = []
    if nivel in ("Crítico", "Alto"):
        if not re.search(r"\d+\s*(usuario|colaborador|pessoa|caminh|loja|caixa)|todos|varios|ninguem", t):
            faltando.append("quantos usuários afetados")
        if not any(re.search(rf"\b{p}\b", t) for p in _PRODUTOS):
            faltando.append("produto afetado")
    m1, mr = METAS[nivel]
    return {"nivel": nivel, "emoji": EMOJI[nivel], "motivos": motivos,
            "meta_1o_atendimento_min": m1, "meta_resolucao_min": mr, "dados_faltando": faltando}


def reavaliar(nivel: str, minutos_esperando: float) -> str:
    meta = METAS[nivel][1]
    return _subir(nivel) if meta is not None and minutos_esperando > meta else nivel
