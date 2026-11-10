# Exemplos de tickets (Vértice Desk)

> Tudo aqui é **fictício** (clientes, valores, datas). Os campos "Gabarito" são rótulos sintéticos para a demo: **[SUPOSIÇÃO]**, não verdade de mercado.
> Produtos fictícios da Vértice: ERP, Fiscal, Financeiro, Estoque, PDV, Folha, BI e API.
> Datas em novembro/2026. MRR em reais por mês.

## Mapeamento para os dados do desafio
Os tickets são **sintéticos de demo** (texto livre que a base não tem). Para casar com os 4 serviços da base:
| Produto citado no ticket | Serviço na base |
|---|---|
| ERP, Fiscal, Estoque, PDV | Sistema Alfa |
| Financeiro, Folha, Contrato/Cobrança | Sistema Beta |
| BI, API/integração | Portal Web |
| uso pelo celular | Aplicativo Mobile |
MRR, tempo de casa e nº de funcionários **não existem na base**: são só contexto narrativo. Na demo, cole a **Mensagem** na aba de triagem e escolha um cliente da base com o mesmo nível de risco do gabarito.

## Visão geral

| ID | Cliente | Produto | Severidade | Tom | Risco de churn (gabarito) |
|---|---|---|---|---|---|
| VD-1001 | Sabor da Serra Alimentos | Fiscal | Crítica | Furioso | Alto |
| VD-1002 | TransLog Express | ERP | Alta | Educado, insistente | Médio |
| VD-1003 | Moda Viva Store | PDV | Crítica | Informal, urgente | Médio |
| VD-1004 | EduNext Cursos | Financeiro | Média | Confuso | Baixo |
| VD-1005 | ConstruMax Engenharia | BI | Baixa | Elogioso | Baixo |
| VD-1006 | Mercadinho Bom Preço | Estoque | Alta | Seco, técnico | Médio |
| VD-1007 | Escritório Contábil Prisma | Contrato/Cobrança | Média | Irritado, ameaça | Alto |
| VD-1008 | Distribuidora Aurora | API | Alta | Técnico | Médio |
| VD-1009 | Metalúrgica Souza & Filhos | Folha | Crítica | Formal, tenso | Alto |
| VD-1010 | Padaria Pão Quente | ERP (onboarding) | Baixa | Perdido, gentil | Médio |

---

## VD-1001 — NF-e rejeitada, emissão parada
- **Cliente:** Sabor da Serra Alimentos (indústria, 80 func.) | **Produto:** Vértice Fiscal | **Canal:** telefone → e-mail
- **Contexto:** 4 anos de casa, MRR R$ 6.800, 3 chamados em 90 dias
- **Mensagem:** "Desde a atualização de ontem à noite todas as notas estão sendo rejeitadas. Tenho 9 caminhões parados na doca esperando nota para sair. Isso é a terceira vez este ano! Se não resolverem HOJE vou pedir o cancelamento e cobrar o prejuízo."
- **Gabarito:** categoria *Bug pós-atualização*; prioridade *Crítica*; sentimento *Raiva*; churn *Alto*. Sinais: ameaça explícita, reincidência, impacto operacional direto.

## VD-1002 — Relatório de frota lento (3º chamado)
- **Cliente:** TransLog Express (logística, 120 func.) | **Produto:** Vértice ERP | **Canal:** portal
- **Contexto:** 2 anos, MRR R$ 11.400
- **Mensagem:** "Bom dia, tudo bem? Voltando ao assunto do chamado anterior: o relatório de custo por veículo ainda leva uns 6 minutos para abrir. Sei que vocês estão trabalhando nisso, mas nossa diretoria pede esse relatório toda segunda. Teriam uma previsão?"
- **Gabarito:** categoria *Desempenho*; prioridade *Alta*; sentimento *Paciência no limite*; churn *Médio*. Sinais: reincidência sem solução, cliente cordial mas cobrando prazo.

## VD-1003 — PDV travando na véspera de promoção
- **Cliente:** Moda Viva Store (varejo, 25 func.) | **Produto:** Vértice PDV | **Canal:** chat
- **Contexto:** 1 ano, MRR R$ 1.900
- **Mensagem:** "gente o caixa travou de novo!! tá aparecendo erro de sincronização e a fila tá dando volta na loja. semana que vem é a promo e eu NÃO posso ter isso. me liga pfv"
- **Gabarito:** categoria *Incidente PDV/sincronização*; prioridade *Crítica*; sentimento *Urgência/estresse*; churn *Médio*. Sinais: pico de vendas iminente, pedido de contato humano.

## VD-1004 — Dúvida de conciliação bancária
- **Cliente:** EduNext Cursos (educação, 18 func.) | **Produto:** Vértice Financeiro | **Canal:** e-mail
- **Contexto:** 8 meses, MRR R$ 780
- **Mensagem:** "Olá! Importei o extrato do banco mas não sei por que alguns lançamentos ficam como 'não conciliado'. Fiz algo errado? Não entendi bem a tela. Obrigada!"
- **Gabarito:** categoria *Dúvida de uso*; prioridade *Média*; sentimento *Neutro/confuso*; churn *Baixo*. Resposta ideal: tutorial curto + oferta de chamada.

## VD-1005 — Elogio e pedido de funcionalidade
- **Cliente:** ConstruMax Engenharia (construção, 95 func.) | **Produto:** Vértice BI | **Canal:** portal
- **Contexto:** 3 anos, MRR R$ 5.200
- **Mensagem:** "Equipe, o painel de custo por obra está ótimo, mudou nossas reuniões. Uma sugestão: dá para exportar o dashboard em PDF com o logo da empresa? Nosso diretor quer enviar para os clientes."
- **Gabarito:** categoria *Solicitação de melhoria*; prioridade *Baixa*; sentimento *Positivo*; churn *Baixo*. Possível oportunidade de upsell.

## VD-1006 — Saldo de estoque divergente após inventário
- **Cliente:** Mercadinho Bom Preço (varejo alimentar, 14 func.) | **Produto:** Vértice Estoque | **Canal:** e-mail
- **Contexto:** 2 anos, MRR R$ 1.100, 2 chamados em 90 dias
- **Mensagem:** "Após o inventário de domingo o sistema mostra saldo negativo em 37 itens. Anexo a planilha da contagem. Preciso do ajuste ou de explicação de como o sistema calculou. Aguardo retorno."
- **Gabarito:** categoria *Inconsistência de dados*; prioridade *Alta*; sentimento *Seco/cobrando*; churn *Médio*. Sinais: tom frio, evidência anexada, perda de confiança nos dados.

## VD-1007 — Reajuste de 18% na renovação
- **Cliente:** Escritório Contábil Prisma (serviços, 12 func.) | **Produto:** Contrato/Cobrança | **Canal:** e-mail
- **Contexto:** 5 anos, MRR R$ 950, renovação em 20 dias
- **Mensagem:** "Recebi a proposta de renovação com 18% de aumento, sem nenhuma melhoria visível. Já tenho orçamento de outro sistema por bem menos. Antes de assinar quero entender essa conta, senão vou migrar."
- **Gabarito:** categoria *Comercial/Renovação*; prioridade *Média* (mas com prazo); sentimento *Irritação*; churn *Alto*. Sinais: concorrente citado, renovação próxima, valor percebido baixo. Deve ir ao time comercial/CS.

## VD-1008 — Integração com e-commerce quebrou
- **Cliente:** Distribuidora Aurora (distribuição, 40 func.) | **Produto:** Vértice API | **Canal:** portal (dev do cliente)
- **Contexto:** 18 meses, MRR R$ 3.300
- **Mensagem:** "Desde ontem o endpoint de pedidos retorna 401 com o mesmo token que funcionava. Nada mudou do nosso lado. Logs e timestamps em anexo. Houve mudança de autenticação sem aviso? Pedidos do site não estão entrando no ERP."
- **Gabarito:** categoria *Integração/autenticação*; prioridade *Alta*; sentimento *Neutro-técnico*; churn *Médio*. Sinais: mudança sem comunicação, pedidos parados.

## VD-1009 — Folha com encargos divergentes
- **Cliente:** Metalúrgica Souza & Filhos (indústria, 150 func.) | **Produto:** Vértice Folha | **Canal:** telefone → e-mail
- **Contexto:** 6 anos, MRR R$ 9.600, 4 chamados em 90 dias
- **Mensagem:** "Prezados, a prévia da folha apresenta cálculo de encargos diferente do mês anterior para 14 colaboradores, sem alteração cadastral. O pagamento é na quinta-feira. Solicito retorno formal em 24 horas, pois já reportamos situação semelhante em setembro."
- **Gabarito:** categoria *Erro de cálculo*; prioridade *Crítica*; sentimento *Tensão formal*; churn *Alto*. Sinais: prazo de pagamento, reincidência, linguagem formal (pode virar questão contratual).

## VD-1010 — Primeiro mês e ninguém ensinou a emitir boleto
- **Cliente:** Padaria Pão Quente (alimentação, 9 func.) | **Produto:** Vértice ERP (onboarding) | **Canal:** chat
- **Contexto:** 3 semanas de contrato, MRR R$ 450
- **Mensagem:** "oi, tudo bem? contratei vocês faz 3 semanas e ainda não consegui emitir boleto pros meus clientes de encomenda. vi um vídeo mas não achei a opção. será que o sistema faz isso? to começando a achar que não era pra mim 😅"
- **Gabarito:** categoria *Onboarding/dúvida de uso*; prioridade *Baixa*; sentimento *Desanimado*; churn *Médio*. Sinais: cliente novo sem valor percebido, risco de abandono precoce.
