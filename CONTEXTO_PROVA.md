# Hackathon Data Cempro + Cesuca 2026: contexto da prova

Fonte: pasta "Hackathon" no Google Drive (regulamento, desafio, dicionário e 3 planilhas).

## Desafio
Empresa fictícia de software com 100 clientes, 300 atendimentos (jul a set/2026) e uso mensal de 4 serviços
(Portal Web, Aplicativo Mobile, Sistema Alfa, Sistema Beta). Identificar um problema, risco ou oportunidade e entregar
um protótipo funcional que transforme os dados em solução útil (informar, automatizar, prever, organizar, priorizar).

## Cronograma (09/11/2026)
- 19:20 a 21:20: desenvolvimento no laboratório
- 21:30: todos no auditório
- 21:30 a 22:10: pitch de 5 min (1 min problema/público, 3 min demo, 1 min resultados/limitações/próximo passo)

## Avaliação (100 pts)
| Critério | Peso |
|---|---|
| Criatividade e inovação | 25 |
| Utilidade prática | 25 |
| Funcionamento do protótipo | 25 |
| Uso adequado da tecnologia e dos dados | 15 |
| Clareza da apresentação | 10 |

Desempate: funcionamento, depois utilidade. A banca registra notas preliminares durante o desenvolvimento.

## Entregáveis
- Protótipo executável ou demo funcional (local ou web)
- Descrição em até 5 frases (problema, público, solução)
- Código-fonte ou link de repositório
- README com execução, dependências e limitações (e recursos de IA usados)
- Pitch de até 5 min com demo

## Regras
- Desenvolvimento só nos PCs do laboratório (dispositivo pessoal desclassifica)
- IA generativa e libs open source liberadas, com identificação
- Usar pelo menos um dos arquivos fornecidos
- Saber explicar e demonstrar o que foi implementado
- Não inferir causalidade a partir de correlação

## Dados (data/)
- clientes.csv: cliente_id, nome_ficticio, porte (Micro/Pequena/Média), setor, cidade, data_cadastro (M/D/AAAA)
- atendimentos.csv: 300 chamados, status Resolvido/Pendente, tempo_resolucao_min e satisfacao_1_a_5 vazios para pendentes
- uso_servicos.csv: 1 linha por cliente por mês (jul, ago, set), acessos e operacoes_realizadas

## Inconsistências encontradas
- data_cadastro em M/D/AAAA (dicionário diz AAAA-MM-DD)
- Dicionário cita clientes.csv, arquivos originais são .xlsx
- uso_servicos: o serviço do cliente muda de mês para mês
- 74 linhas com operacoes_realizadas > acessos; 6 linhas com acessos = 0

## Números-chave
- 40 pendentes (13%): 13 Alta, 15 Normal, 12 Baixa
- Satisfação média 3.8; 39 avaliações com nota <= 2
- Tempo médio de resolução 114 min; prioridade Alta leva 130 min vs Baixa 102 min (SLA invertido)
- "Erro no sistema" é o assunto mais lento (183 min); "Relatório" e "Lentidão" têm a pior satisfação (3.4)
- Portal Web tem a pior satisfação (3.6), Sistema Alfa a melhor (4.1)
- Correlação tempo x satisfação ~0 (0.04)
- 26 clientes com queda de mais de 50% nos acessos de jul para set
- Clientes com mais chamados: C070 (8), C028, C048, C097 (7)
