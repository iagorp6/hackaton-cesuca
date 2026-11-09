# Classificação de risco para chamados (analogia com o Protocolo de Manchester)

**Fonte:** pesquisa do time sobre acolhimento com classificação de risco (SUS / Manchester). **Tipo:** inspiração de processo, não regra clínica.
**Como usar:** triagem (regras e prompt), front (cores e alertas), pitch ("a Nexo faz com chamados o que o pronto-socorro faz com pacientes").

## A ideia em 1 frase
A cor é a **urgência**, não a ordem de chegada. Quanto mais grave, **menos dado se exige antes de agir**, e quem estoura o tempo da sua cor é **reclassificado**.

## As 5 cores aplicadas à Nexo Sistemas

| Cor | Nível | Exemplo de chamado | Meta de 1º atendimento | Meta de resolução |
|---|---|---|---|---|
| 🔴 Vermelho | Sistema parado / faturamento parado | "Sistema Beta caiu, não conseguimos emitir nota" | imediato (5 min) | 60 min |
| 🟠 Laranja | Função crítica com erro, vários usuários afetados | "Erro ao fechar pedido no Sistema Alfa" | 15 min | 120 min |
| 🟡 Amarelo | Erro com contorno, lentidão, acesso de 1 usuário | "Portal lento", "senha bloqueada" | 60 min | 240 min |
| 🟢 Verde | Dúvida de uso, instalação, relatório | "Como exporto o relatório?" | 4 h | 1 dia útil |
| 🔵 Azul | Melhoria, pedido administrativo | "Seria bom exportar em Excel" | 1 dia útil | backlog |

Hoje a base só tem Alta/Normal/Baixa. Mapeamento: Alta ≈ 🟠, Normal ≈ 🟡, Baixa ≈ 🟢. Vermelho e Azul são novos (o primeiro vem de discriminadores no texto, o segundo de "Solicitação de melhoria").

**Evidência nos dados** (meta: Alta 60 min, Normal 120, Baixa 240): **84% dos chamados Alta estouraram a meta**, 48% dos Normal e 0% dos Baixa. A fila trata urgente como se não fosse.

## Discriminadores (sinais no texto que empurram a cor)
- **Sobe para 🔴:** "parou", "fora do ar", "caiu", "não consigo faturar / emitir nota / vender", "todos os usuários", "urgente" + Sistema Beta (faturamento).
- **Sobe para 🟠:** "erro" + "vários usuários", "perdi dados", "pedido não fecha", prazo fiscal/hoje.
- **🟡:** "lento", "travando", "senha", "bloqueado", "1 usuário", "consigo contornar".
- **🟢:** "como faço", "dúvida", "instalar", "relatório".
- **🔵:** "sugestão", "seria bom", "melhoria", "quando puderem".
- **Modificadores (não clínicos, do nosso radar):** cliente com risco de churn **Alto** sobe 1 cor; cliente com pendência aberta há > 7 dias sobe 1 cor. Teto em 🔴.

## Dados necessários por cor (o "dado mínimo")

| Cor | Dado mínimo para classificar e agir | Pode ficar para depois |
|---|---|---|
| 🔴 | cliente (ou CNPJ/e-mail), produto afetado, texto do chamado | tudo o resto: canal, usuário, prints, versão |
| 🟠 | + quantos usuários afetados, desde quando | prints, passos para reproduzir |
| 🟡 | + usuário afetado, passos para reproduzir | logs |
| 🟢 | + qual tela/relatório | — |
| 🔵 | descrição do pedido | — |

**Regra de atalho:** se o texto bate em discriminador 🔴, o chamado **não espera cadastro completo**: abre, aciona N2 e o cadastro se completa depois (como o paciente inconsciente).
**Regra de dado incompleto:** campo faltando nunca bloqueia a triagem; vira pergunta automática na primeira resposta.

## De onde vem o dado quando o cliente "não fala" (texto curto ou vago)
| No pronto-socorro | Na Nexo |
|---|---|
| Acompanhante / testemunha | Outro usuário da mesma empresa, gestor da conta |
| SAMU traz sinais vitais | Monitoramento: acessos do mês, erros, uso caindo (`uso_servicos`) |
| Prontuário anterior | Histórico de chamados do cliente (`atendimentos`) |
| Exame físico | Status do serviço (sistema fora do ar para vários clientes ao mesmo tempo) |

## Reavaliação (o que vira alerta automático)
- Chamado passou da meta da sua cor → **sobe 1 cor** e aparece no topo da fila.
- 3+ chamados 🟠/🔴 do mesmo produto em 1 hora → **alerta de incidente** (provável falha geral).
- Cliente de risco Alto com chamado aberto → **alerta para o CS**.

## Campos do sistema (o que existe x o que falta)
| Campo | Existe na base? | Uso |
|---|---|---|
| cliente_id, servico, assunto, canal, prioridade, status | sim | classificação e fila |
| data_abertura | sim (só data, sem hora) | tempo de espera em dias |
| tempo_resolucao_min, satisfacao_1_a_5 | sim (só resolvidos) | metas e qualidade |
| acessos / operações por mês | sim | "sinal vital" do cliente |
| **texto do chamado** | **não** | precisa para a IA classificar de verdade |
| **hora de abertura e do 1º atendimento** | **não** | medir meta de 1º atendimento |
| **nº de usuários afetados** | **não** | discriminador 🟠/🔴 |
| **cor / nível 1 a 5** | **não** (só 3 níveis) | substituir Alta/Normal/Baixa |

## Frase para o pitch
"No pronto-socorro ninguém é atendido por ordem de chegada: quem está mais grave passa na frente, e quem espera demais é reavaliado. A Nexo atende chamados por ordem de chegada e no feeling. Nós trouxemos a lógica da classificação de risco para o suporte, automatizada."

> Analogia educativa. Critérios clínicos reais variam por protocolo e instituição e são aplicados por profissional habilitado.
