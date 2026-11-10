from regras_risco import classificar_nivel, reavaliar

casos = [
    ("Sistema Beta caiu, não conseguimos emitir nota", "Baixo", "Crítico"),
    ("Erro ao fechar pedido para vários usuários", "Baixo", "Alto"),
    ("Portal lento hoje", "Baixo", "Médio"),
    ("Portal lento hoje", "Alto", "Alto"),
    ("Como exporto o relatório?", "Baixo", "Baixo"),
    ("Seria bom exportar em Excel", "Baixo", "Planejado"),
]
for texto, risco, esperado in casos:
    r = classificar_nivel(texto, risco_cliente=risco)
    assert r["nivel"] == esperado, (texto, risco, r)
    print("ok", r["emoji"], r["nivel"], "|", texto)
assert reavaliar("Médio", 300) == "Alto" and reavaliar("Médio", 10) == "Médio"
print("todos os testes passaram")
