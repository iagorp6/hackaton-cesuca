# Perguntas da banca (e respostas de 1 frase)

> Legenda: **[FATO]** = pode ser afirmado com fonte (ver `numeros-setor.md`). **[SUPOSIÇÃO]** = depende de como o protótipo foi construído.
> Respostas já conferidas com o código do protótipo (09/11, 21:05).

## Diretor (negócio)

1. **Qual o retorno financeiro disso?**
   Ainda não medimos, mas a lógica é reter clientes de risco antes do cancelamento, e retenção costuma pesar mais que aquisição **[SUPOSIÇÃO]**.

2. **Por que não comprar Zendesk ou usar GLPI?**
   Eles gerenciam tickets, mas não cruzam o ticket com o risco de o cliente cancelar; é essa camada que o Vértice Desk acrescenta **[SUPOSIÇÃO]**.

3. **E se a IA errar a triagem de um ticket crítico?**
   A triagem é sugestão com motivo visível (palavras-chave ou justificativa da IA) e a primeira resposta é um rascunho que o atendente revisa; se a IA falhar, cai em regras automaticamente.

4. **Dá para usar com dados reais de clientes?**
   O protótipo usa dados fictícios, e com dados reais seriam necessários base legal, anonimização e controle de acesso conforme a LGPD.

## Dev front-end

1. **Como a lista se comporta com 10 mil tickets?**
   O protótipo trabalha com 300 atendimentos (40 pendentes) num st.dataframe; com 10 mil, a lógica fica no backend (radar.py/triagem.py) e o front pagina.

2. **Como o score de risco chega na tela e se atualiza?**
   O score é recalculado em Python a cada interação (Streamlit) e os pesos são ajustáveis na tela; em produção seria um job agendado ou evento por ticket novo.

3. **O que acontece quando a IA demora ou falha?**
   Tem fallback automático para regras por palavras-chave e a tela mostra qual motor está ativo (IA ou regras); o fluxo nunca para.

4. **Como vocês cuidam de acessibilidade e leitura rápida da fila?**
   O nível aparece com emoji e texto (Crítico, Alto...) e a fila é ordenada por um índice de urgência (prioridade + risco do cliente + dias em aberto).

## Professor teórico

1. **Como validaram o modelo de churn se os dados são fictícios?**
   Não validamos a acurácia: os dados sintéticos demonstram o fluxo, e a métrica real exigiria dados históricos de cancelamento.

2. **Qual métrica avaliaria o modelo e por quê?**
   Precision e recall da classe "vai cancelar", porque churn é desbalanceado e a acurácia sozinha engana.

3. **Risco de churn é causa ou correlação?**
   Correlação: o score indica quem se parece com clientes que saíram, e não prova que o ticket causou a saída.

4. **Há risco de viés ou vazamento de informação no modelo?**
   O score não é treinado (é regra ponderada e explicável), então não há vazamento de treino; o viés possível é favorecer quem reclama mais, por isso cada score mostra os motivos e os pesos são ajustáveis.

## Dica de resposta curta
Se a pergunta fugir do que foi construído: **"Isso está fora do protótipo, mas o caminho seria X."** É melhor do que inventar.
