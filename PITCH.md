# Roteiro do pitch (5 min) · Vértice Sistemas

**Empresa do caso (fictícia):** **Vértice Sistemas**, software house B2B parecida com a Vértice: vende ERP e soluções para 100 empresas clientes (Serviços, Indústria, Tecnologia, Comércio) com 4 produtos (Sistema Alfa = ERP, Sistema Beta = financeiro/faturamento, Portal Web, Aplicativo Mobile). A solução é a **Central de Atendimento** dela, no estilo help desk (Zendesk/GLPI), com triagem por IA embutida.
Gancho: **"para o cliente da Vértice, sistema parado é operação parada. E para a Vértice, cliente mal atendido é contrato cancelado."**

Dica do reitor: a banca valoriza processo, simplificação e automação, não o código. Cada frase responde: *que etapa do processo isso elimina ou padroniza?*

## Os 6 verbos do desafio (mostrar que cobrimos TODOS)
O desafio pede uma solução que possa **informar, automatizar, prever, organizar, priorizar ou facilitar decisões**. A nossa faz as seis:

| Verbo | Onde está na solução | O que falar |
|---|---|---|
| **Informar** | Visão geral, Operação de suporte, Qualidade dos dados | "Gestor vê KPIs, SLA invertido e inconsistências dos dados numa tela." |
| **Automatizar** | Triagem IA + primeira resposta sugerida | "Classificar, encaminhar e responder deixam de ser trabalho manual." |
| **Prever** | Radar de churn + tempo estimado de resolução | "Sabemos quem pode cancelar antes de cancelar, e quanto o chamado deve levar." |
| **Organizar** | Fila repriorizada + roteamento para a fila certa | "Uma fila única, ordenada por regra, não por ordem de chegada." |
| **Priorizar** | 5 níveis de severidade + risco de churn sobe o nível | "Prioridade por critério auditável, não no feeling." |
| **Facilitar decisões** | Ranking de risco, ficha do cliente, ação sugerida, export CSV | "O CS recebe quem contatar, por quê e o que fazer." |

Dica: no fechamento, ler os 6 verbos em sequência apontando para a tela.

## Números do mercado (dizer sempre "segundo ...", detalhes em contexto/numeros-setor.md)
- "Segundo a Zendesk CX Trends 2026, **85% dos líderes de atendimento** dizem que um único problema não resolvido basta para perder o cliente." (liga suporte a churn)
- "Segundo benchmarks de mercado, churn em software para PMEs fica entre **14% e 22% ao ano**, bem acima do enterprise." (é o público da Vértice)
- "Segundo a Zendesk, **95% dos clientes querem saber por que a IA decidiu**: por isso cada triagem e cada score mostra o motivo."

## Tickets prontos para a demo (contexto/exemplos-tickets.md)
- **VD-1001** (NF-e rejeitada, 9 caminhões parados, ameaça cancelar): mostra nível alto + cliente em risco subindo a prioridade.
- **VD-1005** (elogio + sugestão de PDF): mostra nível baixo/planejado, não fura a fila.
- **VD-1007** (reajuste de 18%, cita concorrente): mostra que o risco de churn vem do cliente, não só do texto.

## A banca e o que cada um valoriza

| Avaliador | O que ele quer ouvir | Como falar com ele | Evitar |
|---|---|---|---|
| **Diretor da empresa** (não técnico) | Dinheiro, tempo, cliente que não cancela, risco | Números grandes e simples: "57 h de espera extra", "~150 h/mês liberadas", "9 clientes em risco alto hoje" | Siglas, stack, nomes de modelo de IA |
| **Dev front-end** | Que funciona de verdade, fluxo de tela claro, usabilidade | Demo ao vivo sem travar, poucos cliques, mostrar que a tela responde na hora | Pedir desculpa pelo visual; dizer "é só um protótipo" |
| **Professor (teórico)** | Método, coerência, limitações honestas | "Score explicável por regra, não modelo treinado, porque não há rótulo de churn"; AS-IS x TO-BE como modelagem de processo | Afirmar que prevê churn; vender estimativa como medição |

## 0:00 a 1:00 · Problema (quem fala: pessoa mais segura na oratória)
Tela: aba **🔄 Processo: antes x depois**
- "A Vértice atende 100 empresas. Quando o sistema delas para, a operação delas para."
- "Hoje o chamado chega por 4 canais, alguém lê, classifica e decide a prioridade no feeling."
- "Prova: Relatório é marcado como urgente em 46% das vezes, erro de sistema só em 38%. Não existe critério."
- "Resultado: o chamado urgente espera mais que o não urgente, 126 contra 100 minutos. São 57 horas de espera extra só nos urgentes."
- "E o time de relacionamento só descobre que o cliente está insatisfeito quando ele cancela."

## 1:00 a 4:00 · Demo do processo novo (quem fala: quem pilota a tela, ensaiado)
1. **Processo** (20 s): AS-IS x TO-BE lado a lado. "De 7 etapas, 4 viraram automáticas."
2. **Triagem IA** (80 s): escolher um cliente de risco **Alto**, exemplo "Sistema fora do ar". Mostrar em sequência: assunto e serviço classificados, fila definida, **prioridade subiu por causa do risco do cliente**, tempo estimado, primeira resposta pronta. Frase: "nenhuma dessas etapas precisou de uma pessoa decidindo."
3. **Fila repriorizada** (40 s): "os 40 chamados em aberto reordenados por uma regra única: urgência, risco do cliente e dias em aberto. Vejam quem subiu."
4. **Ranking / Ficha do cliente** (40 s): "o relacionamento recebe quem pode cancelar, o motivo e a ação sugerida, antes do cancelamento."

## 4:00 a 5:00 · Resultado
- "Informamos, automatizamos, prevemos, organizamos, priorizamos e facilitamos decisões: os 6 pontos do desafio numa solução só."
- "Uma regra única no lugar de decisões individuais: prioridade padronizada e auditável."
- "Com as nossas premissas, cerca de 150 horas por mês de triagem manual viram tempo para resolver chamado." (premissas ajustáveis na tela)
- "Se a IA cair, o processo continua por regras. O atendimento nunca para."
- "Próximo passo: uma entrada única para os 4 canais e alerta automático para o relacionamento."

## Perguntas prováveis e respostas curtas
(Lista completa e conferida com o código em contexto/perguntas-banca.md.)

**Diretor**
- *Quanto custa?* Roda em Docker num servidor comum; a IA pode ser local (sem custo por uso) ou em nuvem. Sem IA, funciona por regras.
- *Quanto eu ganho?* ~150 h/mês de triagem com 1.000 chamados/mês (premissa), e foco nos 9 clientes de risco alto antes de perderem o contrato.
- *Meu time precisa mudar muito?* Não. Muda a porta de entrada do chamado; o atendente continua resolvendo, só não precisa mais classificar nem priorizar.

**Dev front-end**
- *Por que Streamlit?* Para validar o processo em 2 horas. A lógica fica separada da tela (`radar.py`, `triagem.py`), então dá para trocar o front por React sem reescrever a regra.
- *E se a IA demorar ou falhar?* Tem fallback automático por regras e a tela avisa qual motor está ativo.
- *Funciona no celular?* Layout responsivo do Streamlit; versão final seria integrada ao Portal/App da Vértice.

**Professor**
- *Isso é machine learning?* O score de churn não é: é uma regra ponderada e explicável, porque os dados não têm rótulo de cancelamento. A IA entra só na classificação do texto do chamado.
- *Como validaram?* Não há texto de chamado nos dados, então a IA não foi validada com eles; o histórico é usado para tempo estimado e risco. Com cancelamentos reais, o próximo passo é treinar e validar (ex.: regressão logística).
- *Correlação ou causalidade?* Correlação. O score prioriza quem contatar primeiro, não prova que o cliente vai sair.
- *Qualidade dos dados?* Mostrar a aba Qualidade: inconsistências encontradas e como foram tratadas.

## Checklist antes de subir
- [ ] App aberto na aba Processo, zoom do navegador ajustado para o projetor
- [ ] Cliente de risco Alto já escolhido de antemão na Triagem
- [ ] Testar uma vez com a IA ligada; se falhar, seguir com regras sem comentar
- [ ] Cronômetro com alguém do time, sinal aos 4:00
