# Contexto (coleta de dados e informações)

Pasta para os colegas da coleta jogarem tudo que alimenta o contexto do projeto: pesquisa sobre a empresa, processo de atendimento, números do setor, frases para o pitch, exemplos reais de chamados (anonimizados).

## Como enviar
**Pelo GitHub (mais fácil, sem instalar nada):**
1. Abra o repo, troque para a branch `docs/contexto`
2. Entre na pasta `contexto/` > **Add file** > **Create new file** (ou **Upload files**)
3. Commit direto na branch `docs/contexto`

**Pelo terminal:**
```bash
git fetch origin && git checkout docs/contexto
# coloque os arquivos em contexto/
git add contexto/ && git commit -m "contexto: <assunto>" && git push
```

## Formato
- Um arquivo `.md` por assunto, nome curto: `processo-atendimento.md`, `concorrentes.md`, `numeros-setor.md`, `exemplos-chamados.md`
- Sempre com **fonte** (link ou "entrevista com X") e se é **fato** ou **suposição**
- Nada de senha, chave de API ou dado pessoal real

## Modelo de arquivo
```markdown
# <Assunto>
**Fonte:** <link / quem disse>
**Tipo:** fato | suposição

- ponto 1
- ponto 2

**Como usar no projeto:** <pitch / triagem / front>
```

Não mexer em `app.py`, `triagem.py` ou `radar.py` nesta branch: ela é só de contexto. Depois a gente consolida no pitch e no código.
