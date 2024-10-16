import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


cols = st.columns(3)
colunas = cols[0].multiselect(
    'Dimensões Coluna',
    st.session_state['dimensao'] + st.session_state['medida']
)
valor = cols[1].selectbox(
    'Medidas',
    st.session_state['medida']
)
cor = cols[2].selectbox(
    'Cor',
    colunas
)
tabs = st.tabs(['Treemap', 'Sunburst', 'Sankey', 'TimeSeries'])
if len(colunas) > 2:
    with tabs[0]:
        fig = px.treemap(
            st.session_state['df'],
            path=colunas,
            values=valor,
            color=cor,
            height=800,
            width=1200
        )
        fig.update_traces(textinfo='label+value')
        st.plotly_chart(fig)
    with tabs[1]:
        fig = px.sunburst(
            st.session_state['df'],
            path=colunas,
            values=valor,
            color=cor,
            height=800,
            width=1200
        )
        fig.update_traces(textinfo='label+value')
        st.plotly_chart(fig)
    with tabs[2]:
        grupo = st.session_state['df'].groupby(colunas)[valor].sum().reset_index().copy()
        rotulos, codigo = [], 0
        for coluna in colunas:
            for conteudo in grupo[coluna].unique():
                rotulos.insert(len(rotulos), [codigo, conteudo])
                codigo += 1
        rotulos = pd.DataFrame(rotulos, columns=['codigo', 'conteudo'])
        rotulos['codigo'] = rotulos['codigo'].astype(int)
        sankey = []
        for i in range(0, len(colunas) - 1):
            for index, row in grupo.iterrows():
                sankey.insert(
                    len(sankey),
                    [
                        rotulos[rotulos['conteudo'] == row[colunas[i]]]['codigo'].values[0],
                        rotulos[rotulos['conteudo'] == row[colunas[i+1]]]['codigo'].values[0],
                        row[valor],
                        row[valor]
                    ]
                )
        sankey = pd.DataFrame(sankey, columns=['source', 'target', 'value', 'label'])
        data_trace = dict(
            type='sankey', domain=dict(x=[0, 1], y=[0, 1]),
            orientation="h",
            valueformat=".2f",
            node=dict(pad=10, thickness=30, line=dict(color="black", width=0.5),
                label=rotulos['conteudo'].to_list()
            ),
            link=dict(
                source=sankey['source'].dropna(axis=0, how='any'),
                target=sankey['target'].dropna(axis=0, how='any'),
                value=sankey['value'].dropna(axis=0, how='any'),
                label=sankey['label'].dropna(axis=0, how='any'),
            )
        )
        layout = dict(
            title="Hierarquias",
            height=800,
            width=1200,
            font=dict(
                size=10
            ),
        )
        fig = go.Figure(dict(data=[data_trace], layout=layout))
        st.plotly_chart(fig)
    with tabs[3]:
        for coluna in colunas:
            base = st.session_state['df'][
                (st.session_state['df']['taxa_aprovacao'] == st.session_state['df']['taxa_aprovacao'].max()) &
                (st.session_state['df']['nota_saeb_matematica'] == st.session_state['df']['nota_saeb_matematica'].max())
            ].pivot_table(index='ano', columns=coluna, values=valor, aggfunc='sum').reset_index()
            st.plotly_chart(
                px.line(
                    base,
                    x='nome_regiao',
                    y=base.columns,
                )
            )