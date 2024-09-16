import streamlit as st

st.title('Tabela')
st.dataframe(
    st.session_state['df'],
    hide_index=True,
    use_container_width=True,
    column_config={
        'ano': st.column_config.TextColumn(label='Ano'),
        'sigla_uf': st.column_config.TextColumn(label='UF'),
        'rede': st.column_config.TextColumn(label='Rede'),
        'ensino': st.column_config.TextColumn(label='Ensino'),
        'anos_escolares': st.column_config.TextColumn(label='Anos Escolares'),
        'taxa_aprovacao': st.column_config.NumberColumn(label='Taxa de Aprovação'),
        'indicador_rendimento': st.column_config.NumberColumn(label='Indicador de Rendimento'),
        'nota_saeb_matematica': st.column_config.NumberColumn(label='Nota Saeb Matemática'),
        'nota_saeb_lingua_portuguesa': st.column_config.NumberColumn(label='Nota Saeb Português'),
        'nota_saeb_media_padronizada': st.column_config.NumberColumn(label='Nota Saeb Média Padronizada'),
        'ideb': st.column_config.NumberColumn(label='Ideb'),
        'cidade': st.column_config.TextColumn(label='Cidade'),
        'nome_regiao_saude': st.column_config.TextColumn(label='Região de Saúde'),
        'nome_regiao_imediata': st.column_config.TextColumn(label='Região Imediata'),
        'nome_regiao_intermediaria': st.column_config.TextColumn(label='Região Intermediária'),
        'nome_microrregiao': st.column_config.TextColumn(label='Microregião'),
        'nome_mesorregiao': st.column_config.TextColumn(label='Mesorregião'),
        'nome_regiao_metropolitana': st.column_config.TextColumn(label='Região Metropolitana'),
        'nome_uf': st.column_config.TextColumn(label='Estado'),
        'nome_regiao': st.column_config.TextColumn(label='Região'),
        'amazonia_legal': st.column_config.TextColumn(label='Amazônia Legal')
    }
)