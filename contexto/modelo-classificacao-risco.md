# Níveis de severidade para chamados da Data Cempro

**Fonte:** pesquisa do time. A ideia de "classificar por gravidade, não por ordem de chegada" é comum em protocolos de triagem (o Protocolo de Manchester foi só inspiração); as regras abaixo são **nossa proposta** para suporte de software. **Tipo:** suposição/proposta.
**Como usar:** triagem (regras e prompt), front (cores e alertas), pitch.

## A ideia em 1 frase
O nível é a **severidade do impacto no cliente**, não a ordem de chegada. Quanto mais severo, **menos dado se exige antes de agir**, e quem estoura a meta do seu nível **sobe de nível**.

## Os 5 níveis

| Nível | Significado | Exemplo de chamado | Meta de 1º atendimento | Meta de resolução |
|---|---|---|---|---|
| 🔴 Crítico | Sistema parado / operação do cliente parada | "Sistema Beta caiu, não conseguimos emitir nota" | 5 min | 60 min |
| 🟠 Alto | Função crítica com erro, vários usuários afetados | "Erro ao fechar pedido no Sistema Alfa" | 15 min | 120 min |
| 🟡 Médio | Erro com contorno, lentidão, acesso de 1 usuário | "Portal lento", "senha bloqueada" | 60 min | 240 min |
| 🟢 Baixo | Dúvida de uso, instalação, relatório | "Como exporto o relatório?" | 4 h | 1 dia útil |
| 🔵 Planejado | Melhoria, pedido administrativo | "Seria bom exportar em Excel" | 1 dia útil | backlog |

Hoje a base só tem Alta/Normal/Baixa. Mapeamento: Alta ≈ 🟠, Normal ≈ 🟡, Baixa ≈ 🟢. Crítico e Planejado são novos (o primeiro vem de sinais no texto, o segundo de "Solicitação de melhoria").

**Evidência nos dados** (meta: Alta 60 min, Normal 120, Baixa 240): **84% dos chamados Alta estouraram a meta**, 48% dos Normal e 0% dos Baixa.

## Sinais no texto que definem o nível
- **🔴 Crítico:** "parou", "fora do ar", "caiu", "não consigo faturar / emitir nota / vender", "todos os usuários", "urgente" + Sistema Beta (faturamento).
- **🟠 Alto:** "erro" + "vários usuários", "perdi dados", "pedido não fecha", prazo fiscal/hoje.
- **🟡 Médio:** "lento", "travando", "senha", "bloqueado", "1 usuário", "consigo contornar".
- **🟢 Baixo:** "como faço", "dúvida", "instalar", "relatório".
- **🔵 Planejado:** "sugestão", "seria bom", "melhoria", "quando puderem".
- **Modificadores do radar:** cliente com risco de churn **Alto** sobe 1 nível; pendência aberta há > 7 dias sobe 1 nível. Teto em 🔴.

## Dado mínimo por nível

| Nível | Dado mínimo para classificar e agir | Pode ficar para depois |
|---|---|---|
| 🔴 | cliente, produto afetado, texto do chamado | canal, usuário, prints, versão |
| 🟠 | + quantos usuários afetados, desde quando | prints, passos para reproduzir |
| 🟡 | + usuário afetado, passos para reproduzir | logs |
| 🟢 | + qual tela/relatório | — |
| 🔵 | descrição do pedido | — |

**Regra de atalho:** chamado 🔴 **não espera cadastro completo**: abre, aciona N2 e o cadastro se completa depois.
**Regra de dado incompleto:** campo faltando nunca bloqueia a triagem; vira pergunta automática na primeira resposta.

## De onde vem o dado quando o chamado é vago
- **Histórico de chamados do cliente** (`atendimentos`): assuntos recorrentes, satisfação, pendências.
- **Uso do serviço** (`uso_servicos`): acessos caindo indicam problema ou desengajamento.
- **Outros clientes no mesmo produto**: vários chamados do mesmo produto ao mesmo tempo indicam falha geral.
- **Gestor da conta / outro usuário da empresa**.

## Reavaliação (alertas automáticos)
- Chamado passou da meta do seu nível → **sobe 1 nível** e vai para o topo da fila.
- 3+ chamados 🟠/🔴 do mesmo produto em 1 hora → **alerta de incidente**.
- Cliente de risco Alto com chamado aberto → **alerta para o CS**.

## Campos (o que existe x o que falta)
| Campo | Existe na base? | Uso |
|---|---|---|
| cliente_id, servico, assunto, canal, prioridade, status | sim | classificação e fila |
| data_abertura | sim (só data, sem hora) | tempo de espera em dias |
| tempo_resolucao_min, satisfacao_1_a_5 | sim (só resolvidos) | metas e qualidade |
| acessos / operações por mês | sim | saúde de uso do cliente |
| **texto do chamado** | **não** | IA classificar de verdade |
| **hora de abertura e do 1º atendimento** | **não** | medir meta de 1º atendimento |
| **nº de usuários afetados** | **não** | sinal de 🟠/🔴 |
| **nível 1 a 5** | **não** (só 3 níveis) | substituir Alta/Normal/Baixa |

## Frase para o pitch
"Hoje a Data Cempro atende por ordem de chegada e decide a prioridade no feeling. Com níveis de severidade por regra, o chamado que para a operação do cliente passa na frente, e quem espera demais sobe de nível automaticamente."
