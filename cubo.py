import pandas as pd
import streamlit as st

cols = st.columns(4)
linhas = cols[0].multiselect(
    'Dimensões Linha',
    st.session_state['dimensao']
)
colunas = cols[1].multiselect(
    'Dimensões Coluna',
    st.session_state['dimensao']
)
valor = cols[2].selectbox(
    'Medidas',
    st.session_state['medida']
)
agg = cols[3].selectbox(
    'Agregador',
    st.session_state['agregador']
)
if (len(linhas) > 0) & (len(colunas) > 0) & (linhas != colunas):
    st.dataframe(
        st.session_state['df'].pivot_table(
            index=linhas,
            columns=colunas,
            values=valor,
            aggfunc=agg,
            fill_value=0
        )
    )
    st.dataframe(
        st.session_state['df'].groupby(linhas)[valor].sum().reset_index()
    )
