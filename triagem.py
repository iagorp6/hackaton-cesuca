"""Triagem inteligente de chamados.

Motores, nesta ordem: Claude (ANTHROPIC_API_KEY), Ollama Cloud (OLLAMA_API_KEY) ou local (OLLAMA_HOST), regras.

Classifica um chamado novo (texto livre) em serviço, assunto e prioridade, e
ajusta a prioridade pelo risco de churn do cliente calculado em radar.py.

Dois motores:
- LLM (Claude), quando ANTHROPIC_API_KEY está definida no ambiente.
- Fallback por palavras-chave, para a demo nunca depender de rede ou chave.
"""

from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


def _carregar_env(caminho: str = ".env") -> None:
    """Lê .env simples (CHAVE=valor) sem sobrescrever variáveis já definidas no ambiente."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), caminho)
    if not os.path.exists(p):
        return
    for linha in open(p, encoding="utf-8"):
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                os.environ.setdefault(k.strip(), v)


_carregar_env()

SERVICOS = ["Portal Web", "Aplicativo Mobile", "Sistema Alfa", "Sistema Beta"]
ASSUNTOS = ["Erro no sistema", "Lentidão", "Acesso e senha", "Dúvida de utilização",
            "Instalação", "Atualização", "Relatório", "Solicitação de melhoria"]
PRIORIDADES = ["Baixa", "Normal", "Alta"]

FILAS = {
    "Erro no sistema": "N2 Técnico",
    "Lentidão": "N2 Técnico",
    "Instalação": "N2 Técnico",
    "Atualização": "N2 Técnico",
    "Acesso e senha": "N1 Acesso",
    "Dúvida de utilização": "N1 Suporte",
    "Relatório": "N1 Suporte",
    "Solicitação de melhoria": "Produto",
}

MODEL = os.environ.get("TRIAGEM_MODEL", "claude-opus-5-5")


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


# ---------------- Fallback por palavras-chave ----------------
KW_ASSUNTO = {
    "Acesso e senha": ["senha", "login", "logar", "logon", "acesso", "bloquead", "autentic", "entrar", "usuario"],
    "Lentidão": ["lent", "devagar", "demora", "travando", "trava", "carregando", "timeout"],
    "Erro no sistema": ["erro", "bug", "falha", "nao funciona", "parou", "fora do ar", "caiu", "exception", "crash"],
    "Instalação": ["instal", "configurar", "setup", "implantar"],
    "Atualização": ["atualiza", "versao", "update", "upgrade"],
    "Relatório": ["relatorio", "exportar", "planilha", "dashboard", "grafico"],
    "Solicitação de melhoria": ["melhoria", "sugest", "seria bom", "gostaria que", "nova funcionalidade", "poderia ter"],
    "Dúvida de utilização": ["duvida", "como faco", "como fazer", "onde fica", "nao sei", "ajuda"],
}
KW_SERVICO = {
    "Aplicativo Mobile": ["app", "aplicativo", "celular", "mobile", "android", "iphone", "ios"],
    "Portal Web": ["portal", "site", "navegador", "web", "chrome"],
    "Sistema Alfa": ["alfa"],
    "Sistema Beta": ["beta"],
}
KW_ALTA = ["urgente", "parado", "parou", "fora do ar", "caiu", "nao consigo", "todos os usuarios",
           "producao", "faturamento", "bloquead", "perdendo", "critico"]
KW_BAIXA = ["sugest", "melhoria", "quando puder", "duvida", "seria bom", "gostaria"]


def _melhor(texto: str, mapa: dict[str, list[str]], padrao: str) -> tuple[str, list[str]]:
    pontos = {k: [w for w in ws if w in texto] for k, ws in mapa.items()}
    k = max(pontos, key=lambda x: len(pontos[x]))
    return (k, pontos[k]) if pontos[k] else (padrao, [])


def classificar_regras(texto: str, servico_cliente: str | None = None) -> dict:
    t = _norm(texto)
    assunto, kw_a = _melhor(t, KW_ASSUNTO, "Dúvida de utilização")
    servico, kw_s = _melhor(t, KW_SERVICO, servico_cliente or "Portal Web")
    alta = [w for w in KW_ALTA if w in t]
    baixa = [w for w in KW_BAIXA if w in t]
    if alta:
        prioridade = "Alta"
    elif baixa or assunto == "Solicitação de melhoria":
        prioridade = "Baixa"
    else:
        prioridade = "Normal"
    sinais = kw_a + kw_s + alta + baixa
    return {
        "servico": servico,
        "assunto": assunto,
        "prioridade": prioridade,
        "justificativa": "Palavras-chave encontradas: " + (", ".join(sorted(set(sinais))) if sinais else "nenhuma (valores padrão)"),
        "resposta_sugerida": None,
        "motor": "Regras (palavras-chave)",
    }


# ---------------- LLM ----------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
if not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = "http://" + OLLAMA_HOST
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
_HOSTS_LOCAIS_PADRAO = ("http://localhost:11434", "http://host.docker.internal:11434")
if OLLAMA_API_KEY and OLLAMA_HOST in _HOSTS_LOCAIS_PADRAO:
    OLLAMA_HOST = "https://ollama.com"  # chave presente: usa Ollama Cloud
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b" if OLLAMA_API_KEY else "qwen2.5:3b")


def _ollama_headers() -> dict:
    h = {"Content-Type": "application/json"}
    if OLLAMA_API_KEY:
        h["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    return h

SYSTEM_PROMPT = (
    "Você é o assistente de triagem do Vértice Desk, a central de atendimento da Vértice Sistemas, "
    "software house B2B que vende ERP e soluções para empresas. Produtos: Sistema Alfa (ERP e estoque), "
    "Sistema Beta (financeiro e faturamento), Portal Web (autoatendimento) e Aplicativo Mobile. "
    "Classifique o chamado em serviço, assunto e prioridade usando só as categorias permitidas. "
    "Prioridade Alta: operação do cliente parada, sistema fora do ar, faturamento ou emissão de nota bloqueados, "
    "vários usuários afetados ou risco financeiro. Baixa: sugestões de melhoria e dúvidas sem urgência. Normal: o resto. "
    "A justificativa deve ter no máximo 2 frases e citar o que no texto definiu a prioridade. "
    "A resposta_sugerida é a primeira resposta ao cliente, em português, cordial e objetiva, até 5 frases: "
    "confirme o que entendeu, diga que o chamado já foi encaminhado, peça só as informações que faltam "
    "(produto afetado, quantos usuários, desde quando, prints) e assine como \"Equipe Vértice Desk\". "
    "Não prometa prazo exato e não invente informações."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "servico": {"type": "string", "enum": SERVICOS},
        "assunto": {"type": "string", "enum": ASSUNTOS},
        "prioridade": {"type": "string", "enum": PRIORIDADES},
        "justificativa": {"type": "string"},
        "resposta_sugerida": {"type": "string"},
    },
    "required": ["servico", "assunto", "prioridade", "justificativa", "resposta_sugerida"],
}

_ollama_ok: bool | None = None


def ollama_disponivel() -> bool:
    global _ollama_ok
    if _ollama_ok is None:
        import urllib.request
        try:
            req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", headers=_ollama_headers())
            with urllib.request.urlopen(req, timeout=3 if OLLAMA_API_KEY else 1.5) as r:
                _ollama_ok = r.status == 200
        except Exception:
            _ollama_ok = False
    return _ollama_ok


def motor_llm() -> str | None:
    """Qual LLM usar: Claude (se houver ANTHROPIC_API_KEY), Ollama local (se estiver rodando) ou nenhum."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    if ollama_disponivel():
        return "ollama"
    return None


def llm_disponivel() -> bool:
    return motor_llm() is not None


def classificar_ollama(texto: str, contexto_cliente: str) -> dict:
    import json
    import urllib.request

    body = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": SCHEMA,
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Contexto do cliente:\n{contexto_cliente}\n\nChamado:\n{texto}"},
        ],
    }
    req = urllib.request.Request(f"{OLLAMA_HOST}/api/chat", data=json.dumps(body).encode(),
                                 headers=_ollama_headers())
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.loads(json.loads(r.read())["message"]["content"])
    for k, opts in (("servico", SERVICOS), ("assunto", ASSUNTOS), ("prioridade", PRIORIDADES)):
        if out.get(k) not in opts:
            raise ValueError(f"valor inválido para {k}: {out.get(k)!r}")
    out["motor"] = f"LLM {'Ollama Cloud' if OLLAMA_API_KEY else 'local (Ollama)'} {OLLAMA_MODEL}"
    return out


def classificar_llm(texto: str, contexto_cliente: str) -> dict:
    import anthropic
    from pydantic import BaseModel

    class Triagem(BaseModel):
        servico: Literal["Portal Web", "Aplicativo Mobile", "Sistema Alfa", "Sistema Beta"]
        assunto: Literal["Erro no sistema", "Lentidão", "Acesso e senha", "Dúvida de utilização",
                         "Instalação", "Atualização", "Relatório", "Solicitação de melhoria"]
        prioridade: Literal["Baixa", "Normal", "Alta"]
        justificativa: str
        resposta_sugerida: str

    client = anthropic.Anthropic(timeout=30.0, max_retries=1)
    system = SYSTEM_PROMPT
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        output_config={"effort": "low"},
        system=system,
        messages=[{"role": "user", "content": f"Contexto do cliente:\n{contexto_cliente}\n\nChamado:\n{texto}"}],
        output_format=Triagem,
    )
    if resp.stop_reason == "refusal" or resp.parsed_output is None:
        raise RuntimeError("LLM não retornou classificação")
    out = resp.parsed_output.model_dump()
    out["motor"] = f"LLM ({MODEL})"
    return out


# ---------------- Orquestração ----------------
@dataclass
class Resultado:
    servico: str
    assunto: str
    prioridade_informada: str
    prioridade_final: str
    motivo_ajuste: str
    justificativa: str
    fila: str
    tempo_estimado_min: int | None
    resposta_sugerida: str
    motor: str
    aviso: str | None = None
    similares: pd.DataFrame = field(default_factory=pd.DataFrame)
    # Nível de severidade (regras_risco.py); padrões mantêm compatibilidade com o front
    nivel: str | None = None
    nivel_emoji: str = ""
    motivos_nivel: list = field(default_factory=list)
    meta_1o_atendimento_min: int | None = None
    meta_resolucao_min: int | None = None
    dados_faltando: list = field(default_factory=list)


def _subir(p: str, n: int = 1) -> str:
    return PRIORIDADES[min(PRIORIDADES.index(p) + n, 2)]


def ajustar_por_risco(prioridade: str, cliente_row: pd.Series) -> tuple[str, str]:
    faixa = cliente_row["faixa"]
    if faixa == "Alto" and prioridade != "Alta":
        return _subir(prioridade), f"cliente em risco Alto de churn (score {cliente_row['score']})"
    if faixa == "Médio" and cliente_row["pendentes"] > 0 and prioridade == "Baixa":
        return "Normal", f"cliente em risco Médio com {cliente_row['pendentes']} pendência(s) aberta(s)"
    return prioridade, "sem ajuste"


def estimar_tempo(atend: pd.DataFrame, assunto: str, prioridade: str) -> int | None:
    r = atend[(atend["status"] == "Resolvido") & (atend["assunto"] == assunto)]
    if r.empty:
        return None
    return int(round(r["tempo_resolucao_min"].median()))


def resposta_template(nome: str, assunto: str, prioridade: str, fila: str) -> str:
    return (
        f"Olá, equipe da {nome}! Recebemos seu chamado sobre \"{assunto.lower()}\" e ele já foi encaminhado "
        f"para a equipe {fila} com prioridade {prioridade}. "
        "Vamos analisar e retornar o quanto antes. "
        "Se puder, envie prints ou o passo a passo do que aconteceu, isso agiliza o atendimento."
        "\n\nEquipe Vértice Desk"
    )


# Fallback quando regras_risco.py ainda não existe: deriva o nível da prioridade final
_NIVEL_POR_PRIORIDADE = {"Alta": "Alto", "Normal": "Médio", "Baixa": "Baixo"}
_EMOJI_NIVEL = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢", "Planejado": "🔵"}
_METAS_NIVEL = {"Crítico": (5, 60), "Alto": (15, 120), "Médio": (60, 240), "Baixo": (240, 480), "Planejado": (480, None)}


def nivel_severidade(texto: str, faixa_cliente: str, prioridade_final: str, dias_aberto: int = 0) -> dict:
    """Usa regras_risco.classificar_nivel (Gustavo) se existir; senão, deriva da prioridade final."""
    try:
        from regras_risco import classificar_nivel
        r = classificar_nivel(texto, risco_cliente=faixa_cliente, dias_aberto=dias_aberto)
        if isinstance(r, dict) and r.get("nivel"):
            r.setdefault("emoji", _EMOJI_NIVEL.get(r["nivel"], ""))
            r.setdefault("motivos", [])
            r.setdefault("dados_faltando", [])
            return r
    except Exception:  # ImportError ou bug no módulo novo: nunca derruba a triagem
        pass
    nivel = _NIVEL_POR_PRIORIDADE.get(prioridade_final, "Médio")
    m1, mr = _METAS_NIVEL[nivel]
    return {"nivel": nivel, "emoji": _EMOJI_NIVEL[nivel], "motivos": [f"derivado da prioridade {prioridade_final}"],
            "meta_1o_atendimento_min": m1, "meta_resolucao_min": mr, "dados_faltando": []}


def _pedir_dados(resposta: str, faltando: list) -> str:
    if not faltando:
        return resposta
    pedido = "Para agilizar, poderia nos informar: " + ", ".join(faltando) + "?"
    corpo = resposta.replace("\nEquipe Vértice Desk", "").rstrip()
    if pedido.lower() in corpo.lower():
        return resposta
    return f"{corpo}\n\n{pedido}\n\nEquipe Vértice Desk"


def triar(texto: str, cliente_row: pd.Series, atend: pd.DataFrame, uso: pd.DataFrame,
          usar_llm: bool = True) -> Resultado:
    cid = cliente_row["cliente_id"]
    serv_recente = uso[uso["cliente_id"] == cid].sort_values("mes")["servico"].iloc[-1] if (uso["cliente_id"] == cid).any() else None
    contexto = (
        f"{cliente_row['nome_ficticio']} ({cliente_row['porte']}, {cliente_row['setor']}). "
        f"Serviço usado no último mês: {serv_recente}. Chamados pendentes: {cliente_row['pendentes']}."
    )

    aviso = None
    motor = motor_llm() if usar_llm else None
    if motor:
        try:
            c = classificar_llm(texto, contexto) if motor == "claude" else classificar_ollama(texto, contexto)
        except Exception as e:  # rede, chave inválida, rate limit: cai para regras
            aviso = f"LLM indisponível ({type(e).__name__}); usando regras."
            c = classificar_regras(texto, serv_recente)
    else:
        c = classificar_regras(texto, serv_recente)

    final, motivo = ajustar_por_risco(c["prioridade"], cliente_row)
    nv = nivel_severidade(texto, cliente_row["faixa"], final)
    if nv["nivel"] in ("Crítico", "Alto") and final != "Alta":
        final, motivo = "Alta", f"nível de severidade {nv['nivel']}" + (f"; {motivo}" if motivo != "sem ajuste" else "")
    fila = FILAS[c["assunto"]]
    resposta = c.get("resposta_sugerida") or resposta_template(cliente_row["nome_ficticio"], c["assunto"], final, fila)
    sim = atend[(atend["cliente_id"] == cid) | ((atend["assunto"] == c["assunto"]) & (atend["servico"] == c["servico"]))]
    sim = sim.assign(mesmo_cliente=sim["cliente_id"] == cid).sort_values(
        ["mesmo_cliente", "data_abertura"], ascending=[False, False]).head(6)

    return Resultado(
        servico=c["servico"],
        assunto=c["assunto"],
        prioridade_informada=c["prioridade"],
        prioridade_final=final,
        motivo_ajuste=motivo,
        justificativa=c["justificativa"],
        fila=fila,
        tempo_estimado_min=estimar_tempo(atend, c["assunto"], final),
        resposta_sugerida=_pedir_dados(resposta, nv["dados_faltando"]),
        motor=c["motor"],
        aviso=aviso,
        similares=sim.drop(columns="mesmo_cliente"),
        nivel=nv["nivel"],
        nivel_emoji=nv["emoji"],
        motivos_nivel=list(nv["motivos"]),
        meta_1o_atendimento_min=nv.get("meta_1o_atendimento_min"),
        meta_resolucao_min=nv.get("meta_resolucao_min"),
        dados_faltando=list(nv["dados_faltando"]),
    )


def fila_repriorizada(atend: pd.DataFrame, radar: pd.DataFrame, hoje: pd.Timestamp | None = None) -> pd.DataFrame:
    """Reordena os chamados pendentes: prioridade + risco de churn do cliente + tempo em aberto."""
    pend = atend[atend["status"] == "Pendente"].merge(
        radar[["cliente_id", "nome_ficticio", "score", "faixa"]], on="cliente_id", how="left")
    hoje = hoje or atend["data_abertura"].max()
    pend["dias_aberto"] = (hoje - pend["data_abertura"]).dt.days
    peso_prio = pend["prioridade"].map({"Alta": 50, "Normal": 25, "Baixa": 0})
    pend["indice_urgencia"] = (peso_prio + pend["score"] * 0.4 + pend["dias_aberto"].clip(upper=60) * 0.25).round(1)
    # posição original: ordem por prioridade informada e data de abertura (fila "como é hoje")
    orig = pend.assign(_p=pend["prioridade"].map({"Alta": 0, "Normal": 1, "Baixa": 2})).sort_values(["_p", "data_abertura"])
    pos_orig = {aid: i + 1 for i, aid in enumerate(orig["atendimento_id"])}
    pend = pend.sort_values("indice_urgencia", ascending=False).reset_index(drop=True)
    pend["posicao_nova"] = range(1, len(pend) + 1)
    pend["posicao_original"] = pend["atendimento_id"].map(pos_orig)
    pend["mudanca"] = pend["posicao_original"] - pend["posicao_nova"]
    return pend[["posicao_nova", "posicao_original", "mudanca", "atendimento_id", "cliente_id", "nome_ficticio",
                 "faixa", "score", "prioridade", "assunto", "servico", "dias_aberto", "indice_urgencia"]]
