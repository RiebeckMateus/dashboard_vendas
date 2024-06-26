import pandas as pd
import streamlit as st
import requests
import plotly.express as px

st.set_page_config(layout='wide')

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:,.2f} {unidade}'
        valor /=1000
    return f'{prefixo} {valor:,.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

## filtros

regioes = ['Brasil', 'Centro-Oeste', 'Sul', 'Sudeste', 'Nordeste', 'Norte']

st.sidebar.title('Filtros')
with st.sidebar:
    regiao = st.selectbox('Região', options=regioes)

if regiao == 'Brasil':
    regiao=''

with st.sidebar:
    todos_anos = st.checkbox('Dados de todo o período', value=True)

if todos_anos:
    ano=''
else:
    with st.sidebar:
        ano = st.slider('Ano', min_value=2020, max_value=2023)

## carregamento da página

query_string = {'regiao': regiao.lower(), 'ano': ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'	], format='%d/%m/%Y')

with st.sidebar:
    filtro_vendedores = st.multiselect('Vendedores', options=dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### Tabelas de Receita

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

receita_vendedor = dados.groupby('Vendedor')[['Preço']].sum()

### Tabelas de Vendas

qntd_estados = dados.value_counts('Local da compra')
qntd_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(qntd_estados, left_on='Local da compra', right_index=True).sort_values('count', ascending=False)

qntd_mensal = dados[['Data da Compra']].copy()
qntd_mensal['Mês'] = qntd_mensal['Data da Compra'].dt.month_name()
qntd_mensal['Ano'] = qntd_mensal['Data da Compra'].dt.year
qntd_mensal['junt'] = qntd_mensal['Data da Compra'].dt.strftime('%Y-%m')
qntd_mensal = qntd_mensal.groupby('junt')[['Mês', 'Ano']].value_counts().sort_index(ascending=True).reset_index()
# qntd_mensal = qntd_mensal.groupby(['Ano', 'Mês'])

vendas_categoria = dados.value_counts('Categoria do Produto').to_frame()

vendas_vendedor = dados.value_counts('Vendedor').to_frame()

### Tabelas de Vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

fig_mapa_receita = px.scatter_geo(data_frame=receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america', # em resumo, aonde vai estar focado o mapa
                                  size='Preço', # tamanho dos scatters
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita po Estado')

fig_receita_mensal = px.line(data_frame=receita_mensal,
                             x='Mês',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto= True,
                             title='Top Estados (receita)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categoria,
                                text_auto=True,
                                title='Receita por categorias')
fig_receita_categorias.update_layout(yaxis_title='Receita')

fig_qntd_estado = px.scatter_geo(data_frame=qntd_estados,
                                 lat='lat',
                                 lon='lon',
                                 size='count',
                                 scope='south america',
                                 hover_data={'lat':False, 'lon':False},
                                 hover_name='Local da compra',
                                 title='Quantidade de vendas por estado')

fig_top_estados = px.bar(qntd_estados.head(),
                         x='Local da compra',
                         y='count',
                         text_auto=True,
                         title='Top Estados (vendas)')
fig_top_estados.update_layout(yaxis_title='Vendas')

fig_qntd_mensal = px.line(data_frame=qntd_mensal,
                             x='Mês',
                             y='count',
                             markers=True,
                             range_y=(0,qntd_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Quantidade de vendas mensais')
fig_qntd_mensal.update_layout(yaxis_title='Vendas')

fig_qntd_cat = px.bar(data_frame=vendas_categoria,x=vendas_categoria.index, y='count', text_auto=True, title='Vendas por categoria')
fig_qntd_cat.update_layout(yaxis_title='Vendas')

## Visualização

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
    st.dataframe(dados)
    st.write(vendas_categoria)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_qntd_estado, use_container_width=True)
        st.plotly_chart(fig_top_estados, use_container_width=True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qntd_mensal, use_container_width=True)
        st.plotly_chart(fig_qntd_cat, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', min_value=2, max_value=10, value=5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True, title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
        
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True, title=f'Top {qtd_vendedores} vendedores (quantidade vendas)')
        st.plotly_chart(fig_vendas_vendedores)

