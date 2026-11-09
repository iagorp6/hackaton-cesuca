# 📡 Radar de Churn

Hackathon Data Cempro + Cesuca 2026.

## Descrição (5 frases)
1. **Problema:** a empresa tem dados de uso e de suporte de 100 clientes, mas não sabe quais estão perto de cancelar até ser tarde.
2. **Evidência:** 26 clientes tiveram queda de mais de 50% nos acessos de julho para setembro, há 40 chamados pendentes e 39 atendimentos com nota 1 ou 2.
3. **Público:** time de Sucesso do Cliente (CS) e gestores de suporte.
4. **Solução:** um painel que cruza os 3 arquivos, calcula um score de risco explicável de 0 a 100 por cliente, mostra os motivos e sugere a próxima ação, com rascunho de mensagem de retenção.
5. **Benefício:** o CS para de reagir e passa a priorizar contatos por risco, além de enxergar falhas da operação (chamados de prioridade Alta demoram mais que os de Baixa).

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

### Python local
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate   |   Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Dependências
Python 3.10+, streamlit, pandas, plotly (ver `requirements.txt`). Nenhuma API externa ou chave é necessária.

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
- **Visão geral:** KPIs, distribuição de risco, risco por setor e porte
- **Ranking de risco:** filtros, motivos, ação sugerida, exportação CSV para o CS
- **Ficha do cliente:** composição do score, uso mensal, histórico de chamados, rascunho de mensagem de retenção
- **Operação de suporte:** tempo por prioridade (SLA invertido), assunto x satisfação, pendências
- **Qualidade dos dados:** inconsistências encontradas e como foram tratadas

## Estrutura
```
app.py              interface Streamlit
radar.py            cálculo do score (lógica separada da interface)
data/               clientes.csv, atendimentos.csv, uso_servicos.csv (convertidos dos .xlsx fornecidos)
Dockerfile, docker-compose.yml
CONTEXTO_PROVA.md   resumo do regulamento e do desafio
```

## Limitações
- Dados sintéticos e só 3 meses de histórico; não há rótulo de churn real, então o score é uma **regra de negócio explicável**, não um modelo treinado.
- Correlação não implica causalidade: o score prioriza contatos, não prova que o cliente vai sair.
- `uso_servicos` tem 1 serviço por cliente por mês (o serviço muda entre meses), então a queda de uso é calculada no total do cliente.
- 74 linhas têm `operacoes_realizadas` > `acessos` e 6 têm `acessos` = 0; mantidas como vieram e sinalizadas na aba Qualidade.
- `data_cadastro` vem em M/D/AAAA, diferente do dicionário (AAAA-MM-DD).
- A mensagem de retenção é um template; não usa LLM.

## Próximos passos
- Com histórico de cancelamentos reais, treinar um modelo (ex.: regressão logística) e validar os pesos.
- Alerta automático (e-mail/Slack) quando um cliente entra na faixa Alto.
- Gerar a mensagem de retenção com LLM, personalizada pelo histórico de chamados.

## Recursos utilizados
- Bibliotecas open source: Streamlit, pandas, Plotly.
- IA generativa: Claude (Anthropic) usado como assistente na leitura do desafio, análise dos dados e geração de parte do código. Toda a lógica foi revisada pela equipe.
