import pandas as pd
import streamlit as st
import datetime as dt
@st.cache_data
def load_database():
    df = pd.read_excel('data/ideb.xlsx')
    df = df.drop(columns=['ddd','capital_uf'])
    return df

st.set_page_config(page_title="Gestão do Conhecimento", layout="wide")
st.session_state['df'] = load_database()
st.session_state['dimensao'] = [
    'cidade', 'nome_uf','nome_regiao','rede','ensino','anos_escolares', 'nome_regiao_saude', 'nome_regiao_imediata', 'nome_regiao_intermediaria', 'nome_microrregiao', 'nome_mesorregiao','nome_regiao_metropolitana','nome_uf','nome_regiao','amazonia_legal'
]
st.session_state['dimensao_tempo'] = ['ano']
st.session_state['medida'] = ['taxa_aprovacao', 'nota_saeb_matematica', 'nota_saeb_lingua_portuguesa','nota_saeb_media_padronizada', 'indicador_rendimento','ideb']
st.session_state['agregador'] = ['sum', 'mean', 'count', 'min', 'max']
st.title('Gestão do Conhecimento')

pg = st.navigation(
    {
        "Menu": [
            st.Page(page='tabela.py', title='Tabela', icon=':material/house:'),
            st.Page(page='cubo.py', title='Cubo', icon=':material/grid_on:'),
            st.Page(page='dashboard.py', title='Dashboard', icon=':material/analytics:'),
            st.Page(page='visualizacao.py', title='Visualização', icon=':material/dvr:'),
        ],
        "Visualização": [
            st.Page(page='visualizacao/descritiva.py', title='Análise Descritiva',
                    icon=':material/house:'),
            st.Page(page='visualizacao/diagnostica.py', title='Análise Diagnóstica',
                    icon=':material/house:'),
            st.Page(page='visualizacao/preditiva.py', title='Análise Preditiva',
                    icon=':material/house:'),
            st.Page(page='visualizacao/prescritiva.py', title='Análise Prescritiva',
                    icon=':material/house:'),
            ],
    }
)
pg.run()