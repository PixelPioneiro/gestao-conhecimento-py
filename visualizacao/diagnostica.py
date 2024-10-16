import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from itertools import combinations

style_metric_cards(
    border_left_color="#3D5077",
    background_color="#F0F2F6",
    border_size_px=3,
    border_color = "#CECED0",
    border_radius_px = 20,
    box_shadow=True
)

cols = st.columns(4)
coluna = cols[0].selectbox(
    'Dimensões Coluna',
    st.session_state['dimensao']
)
conteudo = cols[1].selectbox(
    'Classe:',
    st.session_state['df'][coluna].unique()
)
medida = cols[2].selectbox(
    'Medida',
    st.session_state['medida']
)
ano = cols[1].selectbox(
    'Ano',
    st.session_state['df'][['ano']].sort_values(by='ano').drop_duplicates()
)
ano_atual = st.session_state['df'][
    (st.session_state['df']['ano'] == 2024) & (st.session_state['df']['ano'] == ano)
]
cols = st.columns([1,3])
cols[0].subheader(f'Métrica de {medida} no ano {ano}')
if ano == 1:
    cols[0].metric(
        label=f'{medida} em relação ao ano anterior',
        value=round(ano_atual[medida].sum(), 2)
    )
else:
    mes_anterior = st.session_state['df'][
        (st.session_state['df']['ano'] == 2024) & (st.session_state['df']['ano'] == ano - 1)
    ]
    cols[0].metric(
        label=f'{medida} em relação ao ano anterior',
        value=round(ano_atual[medida].sum(), 2),
        delta=str(round(ano_atual[medida].sum() - mes_anterior[medida].sum(), 2)),
    )
mes_ano_anterior = st.session_state['df'][
    (st.session_state['df']['ano'] == 2023) & (st.session_state['df']['ano'] == ano)
    ]
cols[0].metric(
    label=f'{medida} em relação ao ano anterior',
    value=round(ano_atual[medida].sum(), 2),
    delta=str(round(ano_atual[medida].sum() - ano[medida].sum(), 2)),
)
cols[0].subheader(f'Comparativo em {coluna}')
cols[0].plotly_chart(
    px.box(
        ano_atual,
        x=coluna,
        y=medida
    )
)
tukeyhsd = pairwise_tukeyhsd(endog=ano_atual[medida], groups=ano_atual[coluna], alpha=0.05)
tukey = []
for grupo in list(combinations(tukeyhsd.groupsunique, 2)):
    tukey.insert(len(tukey), [grupo[0], grupo[1]])
tukey = pd.DataFrame(tukey, columns=['grupo1', 'grupo2'])
tukey['reject'] = tukeyhsd.reject
tukey['meandiffs'] = tukeyhsd.meandiffs
if cols[0].toggle('Todos'):
    cols[0].dataframe(tukey, use_container_width=True, hide_index=True)
else:
    cols[0].dataframe(tukey[tukey['reject']], use_container_width=True, hide_index=True)
with cols[1]:
    cols[1].subheader(f'Indicador de {medida} em {coluna}({conteudo}) no mês {ano}')
    anos = st.session_state['df'][
        st.session_state['df'][coluna] == conteudo
    ].groupby(['Order Year', 'Order Month'])[medida].sum().reset_index()
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge+delta",
            gauge={
                'shape': "bullet",
                'axis': {
                    'visible': True,
                    'range': [
                        anos[medida].min(),
                        anos[medida].max()
                    ]
                },
                'steps': [
                    {'range': [anos[medida].min(), anos[medida].quantile(0.25)], 'color': "salmon"},
                    {'range': [anos[medida].quantile(0.25), anos[medida].quantile(0.50)], 'color': "lightsalmon"},
                    {'range': [anos[medida].quantile(0.50), anos[medida].quantile(0.75)], 'color': "ivory"},
                    {'range': [anos[medida].quantile(0.75), anos[medida].max()], 'color': "linen"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': anos[medida].mean()
                },
                'bar': {'color': "blue"}
            },
            delta={'reference': anos[medida].mean()},
            value=ano_atual[ano_atual[coluna] == conteudo][medida].sum(),
            domain={'x': [0.2, 1], 'y': [0, 1]},
            title={'text': f'{conteudo}'},
        )
    )
    fig.update_layout(height=250)
    cols[1].plotly_chart(fig)
    st.subheader(f'Evolução de {medida} em {coluna} - {conteudo}')
    evolucao = st.session_state['df'][
        (st.session_state['df'][coluna] == conteudo)
    ].groupby(['ano'])[medida].sum().reset_index()
    media = evolucao[medida].mean()
    erro = evolucao[medida].std() * 1.96 / np.sqrt(len(evolucao))
    ls = media + erro
    li = media - erro
    iqr = evolucao[medida].quantile(0.75) - evolucao[medida].quantile(0.25)
    out_max = evolucao[medida].quantile(0.75) + (iqr * 1.5)
    out_min = evolucao[medida].quantile(0.25) - (iqr * 1.5)
    evolucao['classe'] = evolucao[medida].apply(
        lambda x : 'outlier acima' if x > out_max else (
            'acima da média' if x > ls else (
                'media' if x > li else (
                    'abaixo da média' if x > out_min else 'outlier abaixo'
                )
            )
        )
    )
    cols[1].plotly_chart(
        px.bar(
            evolucao,
            x='ano',
            y=medida,
            color='classe',
            hover_name=medida,
            color_discrete_map={
                "media": "yellow",
                "abaixo da média": "orange",
                "acima da média": "green",
                "outlier acima": "blue",
                "outlier abaixo": "red"
            }
        )
    )