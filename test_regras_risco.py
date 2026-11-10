from regras_risco import classificar_nivel, reavaliar


assert classificar_nivel("Sistema Beta caiu, não conseguimos emitir nota")["nivel"] == "Crítico"
assert classificar_nivel("Erro ao fechar pedido para vários usuários")["nivel"] == "Alto"
assert classificar_nivel("Portal lento hoje")["nivel"] == "Médio"
assert classificar_nivel("Portal lento hoje", risco_cliente="Alto")["nivel"] == "Alto"
assert classificar_nivel("Como exporto o relatório?")["nivel"] == "Baixo"
assert classificar_nivel("Seria bom exportar em Excel")["nivel"] == "Planejado"

assert reavaliar("Alto", 121) == "Crítico"
assert reavaliar("Alto", 120) == "Alto"
assert reavaliar("Crítico", 61) == "Crítico"
