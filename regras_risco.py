import re
import unicodedata


NIVEIS = ["Crítico", "Alto", "Médio", "Baixo", "Planejado"]

EMOJI = {
    "Crítico": "🔴",
    "Alto": "🟠",
    "Médio": "🟡",
    "Baixo": "🟢",
    "Planejado": "🔵",
}

METAS = {
    "Crítico": {"1o_atendimento_min": 5, "resolucao_min": 60},
    "Alto": {"1o_atendimento_min": 15, "resolucao_min": 120},
    "Médio": {"1o_atendimento_min": 60, "resolucao_min": 240},
    "Baixo": {"1o_atendimento_min": 240, "resolucao_min": 1440},
    "Planejado": {"1o_atendimento_min": 1440, "resolucao_min": None},
}

SINAIS = {
    "Crítico": (
        "parou",
        "fora do ar",
        "caiu",
        "nao consigo faturar",
        "nao conseguimos faturar",
        "nao consigo emitir nota",
        "nao conseguimos emitir nota",
        "nao consigo vender",
        "nao conseguimos vender",
        "todos os usuarios",
    ),
    "Alto": (
        "erro ao fechar pedido",
        "fechar pedido",
        "pedido nao fecha",
        "perdi dados",
        "varios usuarios",
        "prazo fiscal",
        "vence hoje",
    ),
    "Médio": (
        "erro",
        "lento",
        "lenta",
        "lentidao",
        "travando",
        "trava",
        "senha",
        "bloqueado",
        "bloqueada",
        "consigo contornar",
    ),
    "Baixo": (
        "como faco",
        "como exporto",
        "duvida",
        "instalar",
        "instalacao",
        "relatorio",
    ),
    "Planejado": (
        "sugestao",
        "seria bom",
        "melhoria",
        "quando puder",
        "seria legal",
    ),
}

_PRODUTOS = ("alfa", "beta", "portal", "app")


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


def _sinais_encontrados(texto):
    encontrados = {}
    for nivel in NIVEIS:
        encontrados[nivel] = [sinal for sinal in SINAIS[nivel] if sinal in texto]

    if "urgente" in texto and "beta" in texto:
        encontrados["Crítico"].append("urgente + beta")

    return encontrados


def _subir_nivel(nivel, quantidade=1):
    indice = NIVEIS.index(nivel)
    return NIVEIS[max(0, indice - quantidade)]


def classificar_nivel(texto, risco_cliente="Baixo", dias_aberto=0):
    texto_normalizado = _normalizar(texto)
    sinais = _sinais_encontrados(texto_normalizado)
    nivel = next(
        (nivel for nivel in NIVEIS if sinais[nivel]),
        "Baixo",
    )
    motivos = list(sinais[nivel]) if sinais[nivel] else ["sem sinal específico; nível padrão"]

    if _normalizar(risco_cliente) == "alto":
        nivel = _subir_nivel(nivel)
        motivos.append("risco do cliente Alto")

    if dias_aberto > 7:
        nivel = _subir_nivel(nivel)
        motivos.append("chamado aberto há mais de 7 dias")

    dados_faltando = []
    if nivel in ("Alto", "Crítico"):
        if not re.search(r"\b\d+\s+usuarios?\b", texto_normalizado):
            dados_faltando.append("quantos usuários afetados")
        if not any(
            re.search(rf"\b{re.escape(produto)}\b", texto_normalizado)
            for produto in _PRODUTOS
        ):
            dados_faltando.append("produto afetado")

    meta = METAS[nivel]
    return {
        "nivel": nivel,
        "emoji": EMOJI[nivel],
        "motivos": motivos,
        "meta_1o_atendimento_min": meta["1o_atendimento_min"],
        "meta_resolucao_min": meta["resolucao_min"],
        "dados_faltando": dados_faltando,
    }


def reavaliar(nivel, minutos_esperando):
    meta_resolucao = METAS[nivel]["resolucao_min"]
    if meta_resolucao is not None and minutos_esperando > meta_resolucao:
        return _subir_nivel(nivel)
    return nivel
