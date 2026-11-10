# Referência de help desk: Zendesk, GLPI e o que o Vértice Desk faz a mais

> Legenda: **[FATO]** = confirmado na documentação oficial (link). **[MEMÓRIA]** = conhecimento geral das ferramentas, não conferido linha a linha, então conferir antes de afirmar na banca. **[PROPOSTA]** = decisão de design do Vértice Desk (fictício).

## 1. Zendesk Support

**Campos do ticket**
- **[FATO]** Prioridade (campo de sistema): Baixa, Normal, Alta, Urgente. O SLA só se aplica se esse campo estiver preenchido. Fonte: https://support.zendesk.com/hc/en-us/articles/4408829459866
- **[MEMÓRIA]** Solicitante, assunto, tipo (pergunta, incidente, problema, tarefa), grupo, atendente, organização, tags, canal.

**Status**
- **[FATO]** New, Open, On-hold e Pending (na documentação de métricas); o ciclo termina em Solved e Closed **[MEMÓRIA]**. O tempo em Pending pausa o relógio do cliente. Fonte: https://support.zendesk.com/hc/en-us/articles/204770038

**SLA**
- **[FATO]** Métricas: First reply time, Next reply time, Requester wait time e Agent work time (entre outras, até sete). Cada política define alvo por prioridade e condições para se aplicar. Fonte: https://support.zendesk.com/hc/en-us/articles/4408822410650
- **[FATO]** Requester wait time = tempo em New + Open + On-hold. Fonte: https://handbook.gitlab.com/handbook/security/customer-support-operations/zendesk/metrics-definitions/

**Lista (visões)**
- **[MEMÓRIA]** Colunas típicas: solicitante, assunto, data, prioridade, status, atendente; visões salvas por fila.

## 2. GLPI

**Campos do ticket**
- **[FATO]** Urgência (importância dada pelo solicitante), impacto (dada pelo técnico) e prioridade, calculada por uma matriz urgência × impacto (ITIL). Cada um tem 5 níveis: Muito baixa a Muito alta. Fontes: https://help.glpi-project.org/glpi-12/assistance/tickets/ticketmanagement e https://glpi-python-client.readthedocs.io/en/stable/_modules/glpi_python_client/models/api_schema/assistance/_ticket.html
- **[FATO]** Origem da requisição (direta, e-mail, helpdesk, telefone, escrita, outra). Fonte: https://demisto.pan.dev/docs/reference/integrations/glpi
- **[MEMÓRIA]** Categoria, entidade, solicitante, técnico/grupo atribuído, localização.

**Status**
- **[FATO]** Novo, Em processamento (atribuído), Em processamento (planejado), Pendente, Solucionado, Fechado. Fonte: https://xsoar.pan.dev/docs/reference/integrations/glpi

**SLA**
- **[FATO]** TTO (Time To Own: tempo máximo para alguém assumir) e TTR (Time To Resolve: tempo máximo para resolver); existem também OLAs (acordos internos) e níveis de escalonamento automático. Fonte: https://help.glpi-project.org/glpi-12/setup/service-levels

## 3. Comparativo rápido

| Aspecto | Zendesk | GLPI | Vértice Desk |
|---|---|---|---|
| Prioridade | Campo manual (4 níveis) | Calculada: urgência × impacto (5 níveis) | **[PROPOSTA]** Sugerida pela IA, com motivo |
| Status | New, Open, Pending, On-hold, Solved, Closed | Novo, Processando, Pendente, Solucionado, Fechado | Mesmo ciclo básico, para ser familiar |
| SLA | Primeira resposta, próxima resposta, tempo de espera, tempo de trabalho | TTO e TTR | Mesmo conceito, mostrado na lista |
| Foco | Atendimento ao cliente | Gestão de serviços de TI | Atendimento a clientes de software B2B |

## 4. O que o Vértice Desk faz a mais **[PROPOSTA]**

1. **Triagem por IA:** ao entrar, o ticket recebe categoria, severidade sugerida, sentimento e resumo de uma linha; o atendente confirma ou corrige.
2. **Risco de churn por cliente:** um score (por exemplo 0 a 100) que combina sinais do ticket (ameaça de cancelamento, reincidência, tom) com contexto do cliente (tempo de casa, MRR, chamados recentes).
3. **Motivos visíveis:** o score mostra por que foi dado (ex.: "3º chamado em 90 dias", "cita concorrente"), alinhado à demanda por IA explicável (ver `numeros-setor.md`, item 5).
4. **Fila priorizada por risco e SLA:** em vez de só ordenar por prioridade, o ticket de cliente grande em risco sobe na lista.
5. **Encaminhamento ao time certo:** ticket comercial (ex.: reajuste) vai para CS/comercial, e não para o suporte técnico.

> Tudo no item 4 é o que o protótipo se propõe a demonstrar. Confirmem com o que de fato está implementado antes de apresentar.
