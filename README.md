# 🎫 Vértice Desk: help desk com triagem IA + Radar de Churn

Hackathon Data Cempro + Cesuca 2026. Case fictício: **Vértice Sistemas**, software house B2B (ERP e soluções) parecida com a Data Cempro. A interface é um help desk estilo Zendesk/GLPI para atender os clientes B2B, com triagem por IA e risco de churn em cada ticket.

## Descrição (5 frases)
1. **Problema:** a empresa tem dados de uso e de suporte de 100 clientes, mas não sabe quais estão perto de cancelar até ser tarde.
2. **Evidência:** 26 clientes tiveram queda de mais de 50% nos acessos de julho para setembro, há 40 chamados pendentes e 39 atendimentos com nota 1 ou 2.
3. **Público:** time de Sucesso do Cliente (CS) e gestores de suporte.
4. **Solução:** um assistente de triagem com IA que classifica cada chamado novo (serviço, assunto, prioridade, fila) e sobe a prioridade quando o cliente está em risco de churn, calculado por um score explicável que cruza os 3 arquivos.
5. **Benefício:** hoje chamados de prioridade Alta demoram mais que os de Baixa (130 vs 102 min); com a triagem, o que é urgente e o cliente que pode cancelar vão para o topo da fila.

## Os 6 objetivos do desafio
| Objetivo | Como a solução atende |
|---|---|
| Informar | Visão geral, Operação de suporte e Qualidade dos dados |
| Automatizar | Triagem IA classifica, encaminha e sugere a primeira resposta |
| Prever | Score de risco de churn e tempo estimado de resolução |
| Organizar | Fila repriorizada e roteamento automático para a fila |
| Priorizar | Níveis de severidade + risco de churn do cliente sobe a prioridade |
| Facilitar decisões | Ranking de risco, ficha do cliente, ação sugerida e export CSV para o CS |

## Como rodar

### Docker (recomendado)
```bash
docker compose up --build
# abrir http://localhost:8501
```
Ou sem compose:
```bash
docker build -t radar-churn .
docker run --rm -p 8501:8501 radar-churn
```

### LLM da triagem (opcional)
A aba **Triagem IA** escolhe o motor nesta ordem:
1. **Claude (API)** se `ANTHROPIC_API_KEY` estiver definida (chave do console.anthropic.com; assinatura Pro/Max do Claude Code não serve como chave de API).
2. **Ollama local** se estiver rodando em `OLLAMA_HOST` (padrão `http://localhost:11434`) com o modelo `OLLAMA_MODEL` (padrão `qwen2.5:3b`).
3. **Regras por palavras-chave**, sempre disponível, para a demo nunca quebrar.

```bash
ollama pull qwen2.5:3b     # ~2 GB, roda em CPU
ollama serve               # se ainda não estiver rodando
```
No `docker compose`, o container já aponta para o Ollama do PC via `host.docker.internal`.

**Ollama Cloud (com chave):** a chave fica só no ambiente, nunca no código. O jeito mais simples: `cp .env.example .env` e preencher `OLLAMA_API_KEY` (o `.env` está no `.gitignore`; o app e o `docker compose` leem ele automaticamente). Ou via variável:
```bash
# Linux/macOS
export OLLAMA_API_KEY="sua-chave"; export OLLAMA_MODEL="gpt-oss:20b"
streamlit run app.py
# Windows PowerShell
$env:OLLAMA_API_KEY="sua-chave"; $env:OLLAMA_MODEL="gpt-oss:20b"; streamlit run app.py
# Docker (lê o .env automaticamente)
docker compose up --build
```

**Plano B, Ollama local dockerizado** (baixa ~2 GB, roda em CPU, mais lento):
```bash
OLLAMA_HOST=http://ollama:11434 OLLAMA_MODEL=qwen2.5:3b docker compose --profile local up --build
```

### Python local
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate   |   Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Dependências
Python 3.10+, streamlit, pandas, plotly, anthropic, pydantic (ver `requirements.txt`). Nenhuma chave é obrigatória: sem LLM, a triagem usa regras.

## Como o score funciona
Soma ponderada de 4 sinais, cada um normalizado de 0 a 1 e reescalado para 0 a 100 (pesos ajustáveis na barra lateral):

| Sinal | Peso padrão | Cálculo |
|---|---|---|
| Queda de uso | 35 | acessos de set vs média de jul e ago (só queda conta) |
| Chamados pendentes | 25 | pendentes + pendentes de prioridade Alta (Alta conta em dobro), teto em 3 |
| Satisfação baixa | 25 | (5 - nota média) / 4 nos chamados resolvidos |
| Tempo de resolução alto | 15 | quanto o tempo médio do cliente passa da média geral (114 min) |

Faixas: **Alto** >= 45, **Médio** 25 a 44, **Baixo** < 25. Com os pesos padrão: 9 Alto, 34 Médio, 57 Baixo.

## Telas
- **Processo: antes x depois:** fluxo AS-IS x TO-BE, evidências de priorização manual sem critério e SLA invertido, horas/mês de triagem manual eliminadas (premissas ajustáveis)
- **Triagem IA:** escolhe o cliente, escreve o chamado, recebe assunto, serviço, prioridade (ajustada pelo risco de churn), fila, tempo estimado pela mediana histórica, chamados parecidos e primeira resposta sugerida
- **Fila repriorizada:** os 40 pendentes reordenados por prioridade + risco do cliente + dias em aberto, com a posição antes e depois
- **Visão geral:** KPIs, distribuição de risco, risco por setor e porte
- **Ranking de risco:** filtros, motivos, ação sugerida, exportação CSV para o CS
- **Ficha do cliente:** composição do score, uso mensal, histórico de chamados, rascunho de mensagem de retenção
- **Operação de suporte:** tempo por prioridade (SLA invertido), assunto x satisfação, pendências
- **Qualidade dos dados:** inconsistências encontradas e como foram tratadas

## Estrutura
```
app.py              interface Streamlit
radar.py            cálculo do score (lógica separada da interface)
triagem.py          classificação de chamados (Claude / Ollama / regras) e fila repriorizada
regras_risco.py     níveis de severidade (🔴 Crítico a 🔵 Planejado) por sinais no texto + risco do cliente
contexto/           pesquisa do time: modelo de severidade, tickets de demo, números do setor, perguntas da banca
data/               clientes.csv, atendimentos.csv, uso_servicos.csv (convertidos dos .xlsx fornecidos)
Dockerfile, docker-compose.yml (o .dockerignore exclui .env, a chave nunca vai para a imagem)
CONTEXTO_PROVA.md   resumo do regulamento e do desafio
PITCH.md            roteiro do pitch com foco em processo
```

## Limitações
- Dados sintéticos e só 3 meses de histórico; não há rótulo de churn real, então o score é uma **regra de negócio explicável**, não um modelo treinado.
- Correlação não implica causalidade: o score prioriza contatos, não prova que o cliente vai sair.
- `uso_servicos` tem 1 serviço por cliente por mês (o serviço muda entre meses), então a queda de uso é calculada no total do cliente.
- 74 linhas têm `operacoes_realizadas` > `acessos` e 6 têm `acessos` = 0; mantidas como vieram e sinalizadas na aba Qualidade.
- `data_cadastro` vem em M/D/AAAA, diferente do dicionário (AAAA-MM-DD).
- A planilha de atendimentos não tem texto do chamado, só a categoria: a IA classifica texto novo e não foi treinada nem validada com os dados. O histórico é usado para tempo estimado, chamados parecidos e risco do cliente.
- O classificador por regras é simples (palavras-chave) e serve como fallback.
- A mensagem de retenção do radar é um template; a resposta da triagem usa LLM quando disponível.

## Próximos passos
- Com histórico de cancelamentos reais, treinar um modelo (ex.: regressão logística) e validar os pesos.
- Alerta automático (e-mail/Slack) quando um cliente entra na faixa Alto.
- Gerar a mensagem de retenção com LLM, personalizada pelo histórico de chamados.

## Recursos utilizados
- Bibliotecas open source: Streamlit, pandas, Plotly.
- IA no produto: Claude (API Anthropic) ou modelo local via Ollama para classificar chamados.
- IA generativa no desenvolvimento: Claude (Anthropic) usado como assistente na leitura do desafio, análise dos dados e geração de parte do código. Toda a lógica foi revisada pela equipe.
