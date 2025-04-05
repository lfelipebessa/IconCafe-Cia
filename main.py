import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


# Leitura do banco de dados
df = pd.read_csv('dados_cafe_e_cia.csv')

# Configurando visual da página
st.set_page_config(layout="wide")

# CSS para padronizar os filtros
st.markdown("""
<style>
    /* Estiliza todos os elementos de input (como selectbox e multiselect) */
    div[data-baseweb="select"] > div {
        background-color: #f1ece6; /* bege claro */
        color: #3b2f2f; /* marrom escuro para o texto */
        border-radius: 8px;
    }
    div[data-baseweb="select"] > div:hover {
        background-color: #e6ded3; /* hover */
    }

    /* Estilo do label dos filtros */
    label {
        color: #3b2f2f !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#3E2C1C;'>📊 Dashboard - Café & Cia</h1>", unsafe_allow_html=True)

# Definição da paleta de cores
cafe_palette1 = ['#8B5E3C', '#A47148', '#C19A6B', '#D2B48C']
cafe_palette2 = ['#4e342e', '#6d4c41', '#a1887f', '#bcaaa4', '#d7ccc8', '#efebe9']
cafe_palette3_contrast = [
    '#3E2723',  # Marrom escuro - café torrado
    '#6D4C41',  # Marrom médio - canela
    '#A1887F',  # Marrom claro - cappuccino
    '#D7CCC8',  # Bege acinzentado - leite com café
    '#FFE0B2',  # Caramelo claro
    '#A67C52'   # Caramelo escuro / noz-moscada
]
cafe_palette_contrast = ['#4B2E2B', '#7B3F00', '#A47149', '#D6A77A']  # unidades
total_color = '#8B5E3C'  # total



# Puxar Dados da data de venda
df['Data da venda'] = pd.to_datetime(df['Data da venda'])
df['Ano'] = df['Data da venda'].dt.year
df['Mês'] = df['Data da venda'].dt.month
df['Dia da semana'] = df['Data da venda'].dt.day_name()
df['Hora'] = df['Data da venda'].dt.hour
df['MêsAno'] = df['Data da venda'].dt.strftime('%b/%Y')  # Ex: Jan/2024, Fev/2024



#FILTROS
# Filtro por mês
df['MêsAno'] = df['Data da venda'].dt.strftime('%b/%Y')
meses_unicos = sorted(df['MêsAno'].unique().tolist(), key=lambda x: pd.to_datetime(x, format="%b/%Y"))

if 'mes_selecionado' not in st.session_state:
    st.session_state.mes_selecionado = 'Todos'
if 'local_selecionado' not in st.session_state:
    st.session_state.local_selecionado = 'Todas'

col_filtros = st.columns([1, 1, 1])
with col_filtros[0]:
    local_selecionado = st.selectbox("Filtrar por Localização da Compra:", ['Todas'] + sorted(df['Localização da compra'].unique().tolist()), index=0)
    st.session_state.local_selecionado = local_selecionado

with col_filtros[1]:
    mes_selecionado = st.selectbox("Filtrar por Mês:", ['Todos'] + meses_unicos, index=0)
    st.session_state.mes_selecionado = mes_selecionado

with col_filtros[2]:
    categorias_unicas = sorted(df['Categoria do produto'].dropna().unique().tolist())
    categorias_selecionadas = st.multiselect(
        "Filtrar por Tipo de Produto:",
        options=categorias_unicas,
        default=[],
        help="Selecione uma ou mais categorias"
    )

# Aplica filtros combinados
df_filtrado = df.copy()

if st.session_state.local_selecionado != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Localização da compra'] == st.session_state.local_selecionado]

if st.session_state.mes_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['MêsAno'] == st.session_state.mes_selecionado]

if categorias_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Categoria do produto'].isin(categorias_selecionadas)]






# 1. Faturamento mensal por unidade (versão com gráfico de linhas)
def faturamento_mes_unidade(df):
    st.subheader("Faturamento Mensal por Unidade")

    # Faturamento base
    df['Faturamento'] = df['Valor unitário'] * df['Quantidade vendida']
    df['MêsAno_ordenado'] = df['Data da venda'].dt.to_period('M').dt.to_timestamp()

    # Filtra apenas as unidades (sem o total)
    df_unidades = df.groupby(['MêsAno_ordenado', 'Localização da compra'])['Faturamento'].sum().reset_index()

    df_unidades = df_unidades.sort_values('MêsAno_ordenado')

    fig = px.line(
        df_unidades,
        x='MêsAno_ordenado',
        y='Faturamento',
        color='Localização da compra',
        markers=True,
        labels={
            'Faturamento': 'Faturamento (R$)',
            'MêsAno_ordenado': 'Mês',
            'Localização da compra': 'Unidade'
        },
        color_discrete_sequence=['#6F4E37',  # Marrom café tradicional
                                  '#D2691E',  # Chocolate/caramelo queimado
                                  '#4682B4',  # Azul acinzentado (quebra o padrão sem agredir)
                                  '#556B2F']
    )

    fig.update_traces(
        mode='lines+markers',
        hovertemplate='<b>%{x|%b/%Y}</b><br>Unidade: %{fullData.name}<br>Faturamento: R$ %{y:,.2f}<extra></extra>'
    )

    fig.update_layout(xaxis=dict(tickformat="%b/%Y"), height=450)
    st.plotly_chart(fig, use_container_width=True)



# 2. Vendas por categoria e produto (versão estável sem interatividade)
def grafico_interativo_vendas_categoria(df):
    st.subheader("Análise de Vendas por Categoria e Produto")

    # Cálculo de faturamento e agrupamentos
    df['Faturamento'] = df['Valor unitário'] * df['Quantidade vendida']
    categorias = df.groupby('Categoria do produto')['Quantidade vendida'].sum().reset_index()
    produtos = df.groupby(['Categoria do produto', 'Nome Produto'])['Quantidade vendida'].sum().reset_index()

    # === GRÁFICO 1: Categorias de Produto ===
    fig_categoria = px.bar(
        categorias,
        x='Categoria do produto',
        y='Quantidade vendida',
        title='Categorias de Produto',
        labels={'Quantidade vendida': 'Quantidade Vendida'},
        color='Categoria do produto',
        color_discrete_sequence=cafe_palette1
    )

    fig_categoria.update_layout(height=400)
    st.plotly_chart(fig_categoria, use_container_width=True)

    # === GRÁFICO 2: Produtos (sem seleção interativa) ===
    fig_produtos = px.bar(
        produtos,
        x='Nome Produto',
        y='Quantidade vendida',
        color='Categoria do produto',
        title='Produtos Mais Vendidos (Todas as Categorias)',
        labels={'Quantidade vendida': 'Quantidade Vendida'},
        color_discrete_sequence=cafe_palette_contrast
    )

    fig_produtos.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig_produtos, use_container_width=True)


    
def faturamento_mensal_total(df):
    st.subheader("Faturamento Mensal Total")

    df['Faturamento'] = df['Valor unitário'] * df['Quantidade vendida']
    df['MêsAno_ordenado'] = df['Data da venda'].dt.to_period('M').dt.to_timestamp()

    total_mensal = df.groupby('MêsAno_ordenado')['Faturamento'].sum().reset_index()

    fig = px.line(
        total_mensal,
        x='MêsAno_ordenado',
        y='Faturamento',
        markers=True,
        text='Faturamento',
        labels={'Faturamento': 'Faturamento (R$)', 'MêsAno_ordenado': 'Mês'},
        color_discrete_sequence=['#4B3621']  # Café escuro
    )

    fig.update_traces(
        mode='lines+markers+text',
        texttemplate='R$ %{text:,.0f}',
        textposition='top center',
        hovertemplate='<b>%{x|%b/%Y}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
    )

    fig.update_layout(
        xaxis=dict(tickformat="%b/%Y"),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)


# 3. Ticket Médio por Canal de Venda
def grafico_ticket_medio(df):
    st.subheader("Ticket Médio por Canal de Venda")

    df['Faturamento'] = df['Valor unitário'] * df['Quantidade vendida']
    ticket_medio = df.groupby('Localização da compra').apply(
        lambda x: (x['Faturamento'].sum() / x.shape[0])
    ).reset_index(name='Ticket médio')

    ticket_medio['Ticket médio'] = ticket_medio['Ticket médio'].round(2)
    ticket_medio = ticket_medio.sort_values(by='Ticket médio', ascending=False)

    fig = px.bar(
        ticket_medio,
        x='Localização da compra',
        y='Ticket médio',
        color='Localização da compra',
        text='Ticket médio',
        labels={'Ticket médio': 'R$', 'Localização da compra': 'Unidade'},
        color_discrete_sequence=cafe_palette1
    )

    fig.update_traces(
        texttemplate='R$ %{text:.2f}',
        textposition='outside'
    )

    fig.update_layout(
        clickmode='event+select',
        height=500,
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    # Mostra o gráfico e capta o clique
    clicked = st.plotly_chart(fig, use_container_width=True)

    # Captura seleção da barra (se possível)
    clicked_data = st.session_state.get('plotly_click_event', None)
    if clicked_data:
        unidade_nome = clicked_data['points'][0]['curveNumber']
        try:
            unidade_real = clicked_data['points'][0]['data']['name']  # Nome da unidade (ex: 'Brasília')
            if unidade_real in df['Localização da compra'].unique():
                st.session_state.local_selecionado = unidade_real
        except:
            pass


# 4. Perfil dos clientes
def perfil_clientes(df):
    st.subheader("Perfil dos Clientes")
    col1, col2 = st.columns(2)

    # Gráfico de Pizza - Gênero
    with col1:
        genero_counts = df['Gênero do cliente'].value_counts().reset_index()
        genero_counts.columns = ['Gênero', 'Quantidade']

        fig_genero = px.pie(
            genero_counts,
            names='Gênero',
            values='Quantidade',
            title='Distribuição por Gênero',
            color_discrete_sequence=cafe_palette3_contrast
        )
        fig_genero.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_genero, use_container_width=True)

    # Gráfico de barras horizontais - Faixa Etária
    with col2:
        faixa_counts = df['Faixa etária do cliente'].value_counts().sort_index().reset_index()
        faixa_counts.columns = ['Faixa etária', 'Quantidade']

        fig_faixa = px.bar(
            faixa_counts,
            x='Quantidade',
            y='Faixa etária',
            orientation='h',
            title='Distribuição por Faixa Etária',
            text='Quantidade',
            color='Faixa etária',
            color_discrete_sequence=cafe_palette3_contrast
        )
        fig_faixa.update_layout(showlegend=False, height=400)
        fig_faixa.update_traces(textposition='outside')
        st.plotly_chart(fig_faixa, use_container_width=True)



# 5. Horarios com mais vendas
def vendas_por_hora(df):
    st.subheader("Vendas por Hora do Dia")

    # Agrupamento e ajuste de hora
    vendas_hora = df.groupby('Hora')['Quantidade vendida'].sum().reset_index()
    vendas_hora['Hora ajustada'] = vendas_hora['Hora'].apply(lambda h: 24 if h == 0 else h)
    vendas_hora = vendas_hora.sort_values('Hora ajustada')

    # Remove duplicidade entre 0h e 24h
    vendas_hora = vendas_hora.drop_duplicates(subset='Hora ajustada')

    # Cria gráfico de linha com pontos e rótulos
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vendas_hora['Hora ajustada'],
        y=vendas_hora['Quantidade vendida'],
        mode='lines+markers+text',
        text=vendas_hora['Quantidade vendida'],
        textposition='top center',
        line=dict(color=cafe_palette1[0], width=2),  # Usa a primeira cor da paleta
        marker=dict(size=7),
        hovertemplate=
            '<b>Hora do Dia:</b> %{x}h<br>' +
            '<b>Qtd. Vendida:</b> %{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Hora do Dia',
        yaxis_title='Qtd. Vendida',
        xaxis=dict(
        tickmode='linear',
        tick0=1,
        dtick=1,
        range=[0.5, 24.5],  # margem extra à esquerda e à direita
        ),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)



# 6. Vendas por dia da semana
def vendas_por_dia_semana(df):
    st.subheader("Vendas por Dia da Semana")

    
    dias_pt = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    dias_ordem = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    df['Dia da semana (pt)'] = df['Dia da semana'].map(dias_pt)
    vendas_dia = df.groupby('Dia da semana (pt)')['Quantidade vendida'].sum().reindex(dias_ordem).reset_index()
    vendas_dia.columns = ['Dia da semana', 'Quantidade vendida']

    fig = px.bar(
        vendas_dia,
        x='Dia da semana',
        y='Quantidade vendida',
        text='Quantidade vendida',
        labels={'Quantidade vendida': 'Qtd. Vendida'},
        color='Dia da semana',
        color_discrete_sequence=cafe_palette1
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)



# ROW 1: Visão Geral - Faturamento Total (mais importante e primeiro)
faturamento_mensal_total(df_filtrado)  # Gráfico novo exclusivo do total

st.markdown("---")

# ROW 2: Faturamento detalhado por unidade + Ticket médio (lado a lado)
col1, col2 = st.columns([1.5, 1])
with col1:
    faturamento_mes_unidade(df_filtrado)  # Gráfico 1 - Por unidade
with col2:
    grafico_ticket_medio(df_filtrado)     # Gráfico 3 - Ticket médio

st.markdown("---")

# ROW 3: Análise de vendas por categoria e produtos
grafico_interativo_vendas_categoria(df_filtrado)  # Gráfico 2

st.markdown("---")

# ROW 4: Perfil dos clientes (gênero e faixa etária lado a lado)
perfil_clientes(df_filtrado)  # Gráfico 4

st.markdown("---")

# ROW 5: Comportamento de consumo (hora x dia da semana)
col3, col4 = st.columns(2)
with col3:
    vendas_por_hora(df_filtrado)         # Gráfico 5
with col4:
    vendas_por_dia_semana(df_filtrado)   # Gráfico 6
