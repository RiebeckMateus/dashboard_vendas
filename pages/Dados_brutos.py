import streamlit as st
import requests
import pandas as pd
import time

## func

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon= "✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', dados.columns.to_list(), default=dados.columns.to_list())
    # dados = dados[[colunas]]

st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', min_value=0, max_value=5000 ,value=(0,5000))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', min_value=dados['Data da Compra'].min(), max_value=dados['Data da Compra'].max(), value= (dados['Data da Compra'].min(), dados['Data da Compra'].max()), format='DD/MM/YYYY' )

## fazer filtros pras outras colunas

with st.sidebar.expander('Categoria'):
    categoria = st.multiselect('Selecione as categorias de produto', options=dados['Categoria do Produto'].unique(), default=dados['Categoria do Produto'].unique())

with st.sidebar.expander('Frete'):
    frete = st.slider('Selecione o frete', min_value=0, max_value=int(dados['Frete'].max().round(0)), value=(0, int(dados['Frete'].max().round(0))))

with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione os vendedores', options=dados['Vendedor'].unique(), default=dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    local = st.multiselect('Selecione os locais de busca', options=dados['Local da compra'].unique(), default=dados['Local da compra'].unique())



query = '''
Produto in @produtos and  \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria and \
@frete[0] <= Frete <= @frete[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e\n:blue[{dados_filtrados.shape[1]}]')

st.markdown('Escreva um nome para o arquivo')

col1, col2 = st.columns(2)

with col1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'

with col2:
    st.download_button('Fazer o download da tabela em csv', data= converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click= mensagem_sucesso)
