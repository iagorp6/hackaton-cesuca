"""Apelidos lúdicos para os clientes fictícios (só camada de exibição).

Os CSV em data/ continuam intactos: o nome original fica em `nome_original`
e o `cliente_id` não muda. O apelido é escolhido pelo setor do cliente, de
forma determinística (mesmo cliente, mesmo apelido em toda execução).
Todos os nomes são inventados; qualquer semelhança com empresa real é coincidência.
"""

from __future__ import annotations

import pandas as pd

APELIDOS = {
    "Serviços": [
        "Contábil Tchê & Cia", "Faxina Relâmpago", "Consultoria Pé no Chão", "Cuia Cheia Eventos",
        "Despachante Carimbo de Ouro", "Lavanderia Bolha de Sabão", "Advocacia Martelo Justo",
        "Agência Pulo do Gato", "RH Gente Boa", "Segurança Olho de Coruja", "Buffet Bem Servido",
        "Imobiliária Chave Mestra", "Transportes Pampa Ligeiro", "Gráfica Tinta Fresca",
        "Autoescola Pisca-Alerta", "Academia Fôlego de Gato", "Salão Tesoura Afiada",
        "Mudanças Caixa Firme", "Jardinagem Grama Verde", "Dedetizadora Xô Inseto",
        "Cobrança Boa Prosa", "Fotografia Clique Certo", "Turismo Mala Pronta",
        "Idiomas Papagaio Poliglota", "Eventos Bah Que Festa", "Coworking Mesa Cheia",
        "Chaveiro Abre-te Sésamo", "Logística Lebre Veloz", "Limpeza Brilho de Espelho",
        "Escritório Café Passado",
    ],
    "Indústria": [
        "Metalúrgica Parafuso Feliz", "Móveis Cupim Nunca", "Calçados Passo Firme", "Malharia Fio da Meada",
        "Plásticos Pote Mágico", "Laticínios Vaca Contente", "Embalagens Caixa Forte",
        "Cerâmica Tijolo Esperto", "Vinícola Taça Cheia", "Erva-Mate Cuia de Ouro", "Tintas Arco-Íris",
        "Usinagem Torno Fino", "Esquadrias Janela Aberta", "Química Tubo de Ensaio",
        "Biscoitos Crocância Total", "Couros Bota de Sete Léguas", "Confecções Linha e Agulha",
        "Fundição Ferro Quente", "Borrachas Pneu Valente", "Molas Pula-Pula", "Papel Folha Branca",
        "Sabonetes Cheirinho Bom", "Doces Brigadeiro Nobre", "Cervejaria Colarinho Alto",
        "Estofados Sofá Macio", "Ferramentas Chave de Boca", "Rações Late-Late", "Velas Pavio Curto",
        "Gelo Polar Gaúcho", "Massas Nhoque da Sorte",
    ],
    "Tecnologia": [
        "Byte Bagual Sistemas", "Pixel Pilchado", "Nuvem do Pampa Cloud", "Bug Zero Software",
        "Código Chimarrão Labs", "Cabo Solto Redes", "Loop Infinito Dev", "Ctrl+Z Soluções",
        "Algoritmo Tchê", "Wi-Fi Tri Bom", "Servidor Sereno", "Firewall Porteira Fechada",
        "Backup Prevenido", "Dados Lapidados", "Robô Prestativo Automação", "Kernel Gaudério",
        "API Abre-Alas", "Commit Feliz", "Deploy de Sexta Tecnologia", "Startup Sem Café",
        "Tela Azul Nunca Mais", "Bit Bem Bolado", "Cookie Sem Migalha", "Ping Pronto Telecom",
        "Cache Esperto", "Sistema Tri Legal",
    ],
    "Comércio": [
        "Mercadinho Leva Tudo", "Ferragem Prego Certo", "Armazém Bah Tchê", "Papelaria Lápis de Cor",
        "Distribuidora Caixote", "Atacado Saco Cheio", "Bazar Agulha no Palheiro",
        "Hortifrúti Folha Verde", "Açougue Picanha Nobre", "Pet Shop Rabo Abanando", "Ótica Olho Vivo",
        "Livraria Traça Feliz", "Floricultura Bem-Me-Quer", "Padaria Pão Quentinho",
        "Materiais Tijolinho", "Brechó Achado Bom", "Empório Cuia & Bomba", "Bazar Tem de Tudo",
    ],
}


def aplicar_apelidos(clientes: pd.DataFrame) -> pd.DataFrame:
    """Devolve uma cópia com `nome_ficticio` trocado pelo apelido e `nome_original` preservado."""
    df = clientes.copy()
    df["nome_original"] = df["nome_ficticio"]
    usados: set[str] = set()
    for setor, grupo in df.sort_values("cliente_id").groupby("setor", sort=False):
        lista = APELIDOS.get(setor, [])
        for i, idx in enumerate(grupo.index):
            nome = lista[i] if i < len(lista) else df.at[idx, "nome_original"]
            if nome in usados:
                nome = df.at[idx, "nome_original"]
            usados.add(nome)
            df.at[idx, "nome_ficticio"] = nome
    return df
