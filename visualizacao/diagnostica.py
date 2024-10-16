import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from itertools import combinations

# Estilo para os cartões de métricas
style_metric_cards(
    border_left_color="#3D5077",
    background_color="#F0F2F6",
    border_size_px=3,
    border_color="#CECED0",
    border_radius_px=20,
    box_shadow=True
)

# Seleção de Dimensão, Classe, Medida e Ano
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
ano = cols[3].selectbox(
    'Ano',
    sorted(st.session_state['df']['ano'].unique())
)

# Filtrando os dados do ano atual
ano_atual = st.session_state['df'][
    (st.session_state['df']['ano'] == ano)
]

# Exibindo métricas comparativas
cols = st.columns([1,3])
cols[0].subheader(f'Métrica de {medida} no ano {ano}')

# Comparação com o ano anterior
if ano == st.session_state['df']['ano'].min():
    cols[0].metric(
        label=f'{medida} em relação ao ano anterior',
        value=round(ano_atual[medida].sum(), 2)
    )
else:
    ano_anterior = st.session_state['df'][
        (st.session_state['df']['ano'] == ano - 1)
    ]
    cols[0].metric(
        label=f'{medida} em relação ao ano anterior',
        value=round(ano_atual[medida].sum(), 2),
        delta=str(round(ano_atual[medida].sum() - ano_anterior[medida].sum(), 2)),
    )

# Boxplot e Teste de Tukey HSD
cols[0].subheader(f'Comparativo em {coluna}')
cols[0].plotly_chart(
    px.box(
        ano_atual,
        x=coluna,
        y=medida
    )
)

# Teste de Tukey HSD para comparação entre grupos
tukeyhsd = pairwise_tukeyhsd(endog=ano_atual[medida], groups=ano_atual[coluna], alpha=0.05)
tukey = []
for grupo in list(combinations(tukeyhsd.groupsunique, 2)):
    tukey.insert(len(tukey), [grupo[0], grupo[1]])
tukey = pd.DataFrame(tukey, columns=['grupo1', 'grupo2'])
tukey['reject'] = tukeyhsd.reject
tukey['meandiffs'] = tukeyhsd.meandiffs

# Exibir os resultados de Tukey
if cols[0].checkbox('Mostrar todos os grupos'):
    cols[0].dataframe(tukey, use_container_width=True, hide_index=True)
else:
    cols[0].dataframe(tukey[tukey['reject']], use_container_width=True, hide_index=True)

# Indicador Gráfico e Evolução Temporal
with cols[1]:
    cols[1].subheader(f'Indicador de {medida} em {coluna} ({conteudo}) no ano {ano}')
    anos = st.session_state['df'][
        st.session_state['df'][coluna] == conteudo
    ].groupby(['ano'])[medida].sum().reset_index()

    # Gráfico de Indicador
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge+delta",
            gauge={
                'shape': "bullet",
                'axis': {'range': [anos[medida].min(), anos[medida].max()]},
                'steps': [
                    {'range': [anos[medida].min(), anos[medida].quantile(0.25)], 'color': "salmon"},
                    {'range': [anos[medida].quantile(0.25), anos[medida].quantile(0.50)], 'color': "lightsalmon"},
                    {'range': [anos[medida].quantile(0.50), anos[medida].quantile(0.75)], 'color': "ivory"},
                    {'range': [anos[medida].quantile(0.75), anos[medida].max()], 'color': "linen"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'value': anos[medida].mean()
                },
                'bar': {'color': "blue"}
            },
            delta={'reference': anos[medida].mean()},
            value=ano_atual[ano_atual[coluna] == conteudo][medida].sum(),
            title={'text': f'{conteudo}'}
        )
    )
    fig.update_layout(height=250)
    cols[1].plotly_chart(fig)

    # Evolução Temporal
    st.subheader(f'Evolução de {medida} em {coluna} - {conteudo}')
    evolucao = st.session_state['df'][
        st.session_state['df'][coluna] == conteudo
    ].groupby(['ano'])[medida].sum().reset_index()

    # Cálculo de limites para definir outliers e classes
    media = evolucao[medida].mean()
    erro = evolucao[medida].std() * 1.96 / np.sqrt(len(evolucao))
    ls = media + erro
    li = media - erro
    iqr = evolucao[medida].quantile(0.75) - evolucao[medida].quantile(0.25)
    out_max = evolucao[medida].quantile(0.75) + (iqr * 1.5)
    out_min = evolucao[medida].quantile(0.25) - (iqr * 1.5)

    # Classificando os valores em categorias
    evolucao['classe'] = evolucao[medida].apply(
        lambda x: 'outlier acima' if x > out_max else (
            'acima da média' if x > ls else (
                'média' if x > li else (
                    'abaixo da média' if x > out_min else 'outlier abaixo'
                )
            )
        )
    )

    # Gráfico de Barras com Classificação
    cols[1].plotly_chart(
        px.bar(
            evolucao,
            x='ano',
            y=medida,
            color='classe',
            color_discrete_map={
                "média": "yellow",
                "abaixo da média": "orange",
                "acima da média": "green",
                "outlier acima": "blue",
                "outlier abaixo": "red"
            }
        )
    )
