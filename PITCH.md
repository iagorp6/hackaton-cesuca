# Roteiro do pitch (5 min), foco em PROCESSO

Dica do reitor: a banca valoriza processo, simplificação e automação, não o código. Falar de etapas eliminadas, não de bibliotecas.

## 1 min · Problema (aba "Processo: antes x depois")
- "Hoje o chamado chega por 4 canais, alguém lê, classifica e decide a prioridade no feeling."
- "Prova disso: Relatório é marcado como Alta em 46% das vezes, Erro só em 38%. Não existe critério."
- "Resultado: chamado Alta espera mais que Baixa (mediana 126 x 100 min). São ~57 horas de espera extra só nos urgentes."
- "E o CS só descobre o cliente insatisfeito quando ele cancela."

## 3 min · Demo do fluxo novo
1. **Processo**: mostrar AS-IS x TO-BE lado a lado. 7 etapas, 4 viram automáticas.
2. **Triagem IA**: escolher um cliente em risco Alto, colar "Sistema fora do ar". Mostrar: classificou, definiu fila, subiu prioridade pelo risco, estimou tempo, já sugeriu a primeira resposta. "Nenhuma dessas etapas precisou de uma pessoa."
3. **Fila repriorizada**: "os 40 pendentes, reordenados por regra única: prioridade + risco do cliente + dias em aberto."
4. **Ranking / Ficha**: "o CS recebe a lista de quem pode cancelar, o motivo e a ação sugerida, antes do cancelamento."

## 1 min · Resultado
- "Uma regra única no lugar de decisões individuais: prioridade padronizada e auditável."
- "Etapas manuais de triagem eliminadas: com as nossas premissas, ~150 h/mês liberadas para 1.000 chamados/mês (ajustável na tela)."
- "Roda em Docker, IA local ou em nuvem, e se a IA cair o processo continua por regras: o fluxo nunca para."
- Próximo passo: entrada única (integrar WhatsApp/E-mail/Portal) e alerta automático para o CS.

Regra de ouro: cada frase responde "que etapa do processo isso elimina ou padroniza?".
