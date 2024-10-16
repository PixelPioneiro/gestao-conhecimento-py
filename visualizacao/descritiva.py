import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Seleção das dimensões, medidas e dimensão temporal
cols = st.columns(3)
colunas = cols[0].multiselect(
    'Dimensões Coluna',
    st.session_state['dimensao'] + st.session_state['medida']  # Combina dimensões e medidas para seleção
)
valor = cols[1].selectbox(
    'Medidas',
    st.session_state['medida']  # Medidas disponíveis (ex: taxa_aprovacao, nota_saeb_matematica)
)
cor = cols[2].selectbox(
    'Cor',
    colunas  # A coluna de cor será escolhida a partir das colunas selecionadas
)

# Adiciona a seleção da dimensão temporal
dimensao_tempo = st.selectbox(
    'Dimensão Temporal',
    st.session_state['dimensao_tempo']  # Seleciona as colunas relacionadas ao tempo (ano, mês, etc.)
)

# Definindo as abas para diferentes gráficos
tabs = st.tabs(['Treemap', 'Sunburst', 'Sankey', 'TimeSeries'])

# Verifica se há colunas suficientes para gerar os gráficos hierárquicos
if len(colunas) > 2:
    # Treemap
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

    # Sunburst
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

    # Sankey
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
                    rotulos[rotulos['conteudo'] == row[colunas[i + 1]]]['codigo'].values[0],
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
        font=dict(size=10),
    )
    fig = go.Figure(dict(data=[data_trace], layout=layout))
    with tabs[2]:
        st.plotly_chart(fig)

# Série Temporal (Time Series)
with tabs[3]:
    # Seleciona dados para a série temporal, usando a dimensão de tempo selecionada
    base = st.session_state['df'].pivot_table(
        index=dimensao_tempo,  # Dimensão de tempo (ex: 'ano', 'mês')
        columns=colunas,  # Dimensões selecionadas
        values=valor,  # Medida selecionada
        aggfunc='sum'  # Função de agregação
    ).reset_index()

    # Cria o gráfico de série temporal
    st.plotly_chart(
        px.line(
            base,
            x=dimensao_tempo,  # Eixo X será a dimensão temporal (ano, mês, etc.)
            y=base.columns[1:],  # Evita o uso da coluna temporal no eixo Y
            title=f'Evolução de {valor} ao longo de {dimensao_tempo}'
        )
    )
