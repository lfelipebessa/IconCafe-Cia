import pandas as pd
import random
import numpy as np
from faker import Faker
from datetime import datetime, timedelta, date

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Categorias e produtos fictícios
categorias = {
    "Cafés Especiais": ["Café Arábica", "Café Robusta", "Café Orgânico"],
    "Chás Artesanais": ["Chá Verde", "Chá de Hibisco", "Chá de Camomila"],
    "Doces": ["Brownie", "Cookie", "Bolo de Cenoura"],
    "Salgados": ["Coxinha Vegana", "Empada de Palmito", "Quiche de Alho-poró"]
}

# Dicionário de preços fixos
precos_produtos = {
    "Café Arábica": 12.90,
    "Café Robusta": 10.90,
    "Café Orgânico": 14.50,
    "Chá Verde": 8.50,
    "Chá de Hibisco": 9.20,
    "Chá de Camomila": 8.90,
    "Brownie": 7.50,
    "Cookie": 6.80,
    "Bolo de Cenoura": 9.90,
    "Coxinha Vegana": 10.20,
    "Empada de Palmito": 9.80,
    "Quiche de Alho-poró": 11.00
}

faixas_etarias = ["18-25", "26-35", "36-45", "46-55", "56+"]
generos = ["Masculino", "Feminino", "Outro"]
locais_compra = ["Brasília", "São Paulo", "Paraná", "Online"]

# Gerar uma lista com 500 nomes únicos de clientes
clientes_nomes = [fake.name() for _ in range(2000)]

linhas = []
for _ in range(5000):
    categoria = random.choice(list(categorias.keys()))
    nome_produto = random.choice(categorias[categoria])
    valor_unitario = precos_produtos[nome_produto]  # preço fixo
    quantidade = np.random.randint(1, 5)
    nome_cliente = random.choice(clientes_nomes)
    faixa_etaria_cliente = random.choices(faixas_etarias, weights=[0.25, 0.3, 0.2, 0.15, 0.1])[0]
    genero_cliente = random.choice(generos)
    local_compra = random.choice(locais_compra)
    data_venda = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2024, 12, 31))
    hora_venda = fake.time_object()
    datahora_venda = datetime.combine(data_venda, hora_venda)



    linhas.append([
        datahora_venda,
        nome_produto,
        categoria,
        valor_unitario,
        quantidade,
        nome_cliente,
        faixa_etaria_cliente,
        genero_cliente,
        local_compra
    ])

# Criar DataFrame
df = pd.DataFrame(linhas, columns=[
    "Data da venda",
    "Nome Produto",
    "Categoria do produto",
    "Valor unitário",
    "Quantidade vendida",
    "Nome do cliente",
    "Faixa etária do cliente",
    "Gênero do cliente",
    "Localização da compra"
])

# Salvar como CSV
df.to_csv("dados_cafe_e_cia.csv", index=False)