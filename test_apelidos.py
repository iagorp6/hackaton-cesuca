import pandas as pd

from apelidos import aplicar_apelidos
from radar import carregar_dados


def test_apelidos_unicos_e_deterministicos():
    clientes, _, _ = carregar_dados()
    a = aplicar_apelidos(clientes)
    b = aplicar_apelidos(clientes.sample(frac=1, random_state=1))
    assert a["nome_ficticio"].is_unique
    assert not a["nome_ficticio"].str.startswith("Empresa Exemplo").any()
    assert a.set_index("cliente_id")["nome_ficticio"].equals(
        b.set_index("cliente_id").loc[a["cliente_id"], "nome_ficticio"])
    # dados originais intactos
    assert clientes["nome_ficticio"].str.startswith("Empresa Exemplo").all()
    assert (a["nome_original"] == clientes["nome_ficticio"]).all()
