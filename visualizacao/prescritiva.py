import pandas as pd
import streamlit as st
import pulp

# Carregar o DataFrame já presente no st.session_state
df = st.session_state['df']

# Título da página
st.title("Análise Prescritiva: Melhoria nas Notas do Ensino Superior")

# Explicação
st.write("""
Nesta página, você pode cruzar as notas dos alunos no Ensino Fundamental e Médio para identificar padrões que influenciam nas notas no Ensino Superior.
A partir disso, você poderá prescrever ações para melhorar o desempenho acadêmico.
""")

# Filtrando os dados
# Assumindo que o DataFrame contenha colunas com notas em diferentes níveis de ensino, como 'nota_saeb_matematica', 'nota_saeb_lingua_portuguesa', 'taxa_aprovacao', etc.
# Vamos cruzar as notas do Ensino Fundamental, Médio e o Ensino Superior.

st.subheader("Seleção de Notas para Análise")

# Seleção de colunas
notas_fundamental_medio = st.multiselect(
    "Selecione as Notas do Ensino Fundamental e Médio",
    [col for col in df.columns if 'nota' in col or 'taxa_aprovacao' in col]
)

nota_superior = st.selectbox(
    "Selecione a Nota do Ensino Superior",
    ['nota_saeb_media_padronizada']  # Supondo que esta seja a coluna que represente o desempenho superior
)

# Garantir que o usuário selecionou as colunas necessárias
if notas_fundamental_medio and nota_superior:

    # Criando um DataFrame com as colunas selecionadas
    df_filtered = df[notas_fundamental_medio + [nota_superior]]

    st.subheader("Analisando o Impacto das Notas no Ensino Superior")

    # Exibe o DataFrame filtrado
    st.write("Notas selecionadas para a análise:")
    st.write(df_filtered.head())

    # Criando a correlação entre as notas do Ensino Fundamental/Médio e a nota do Ensino Superior
    correlacao = df_filtered.corr()[nota_superior].sort_values(ascending=False)
    st.write("Correlação das notas do Ensino Fundamental e Médio com a Nota do Ensino Superior:")
    st.dataframe(correlacao)

    st.write("""
    As notas com maior correlação positiva indicam quais disciplinas ou áreas do Ensino Fundamental e Médio mais influenciam no 
    sucesso no Ensino Superior. A partir dessa análise, podemos sugerir ações específicas para melhorar o desempenho nas áreas mais relevantes.
    """)

    # Parâmetros de entrada para a prescrição
    st.subheader("Parâmetros de Ação Prescritiva")

    # Impactos das variáveis de decisão (recursos para cada nível de ensino)
    impacto_recursos_fundamental_medio = st.number_input(
        "Impacto de Recursos no Ensino Fundamental e Médio (%)", min_value=0.0, value=1.0
    )

    # Limite de orçamento para melhorar as áreas com maior impacto
    orcamento = st.number_input("Orçamento Disponível (R$)", min_value=0.0, value=50000.0)

    # Definir pesos com base na correlação
    pesos = {col: correlacao[col] * impacto_recursos_fundamental_medio for col in notas_fundamental_medio}

    # Modelo de otimização
    if st.button("Resolver Otimização"):
        # Criando o problema de otimização
        problema = pulp.LpProblem("Maximização_Notas_Ensino_Superior", pulp.LpMaximize)

        # Variáveis de decisão: Alocação de recursos para cada nota
        alocacao_recursos = {col: pulp.LpVariable(f"Recursos_{col}", lowBound=0, cat='Continuous') for col in
                             notas_fundamental_medio}

        # Função objetivo: Maximizar a nota do Ensino Superior com base nas correlações
        problema += pulp.lpSum(
            [pesos[col] * alocacao_recursos[col] for col in notas_fundamental_medio]), "Função Objetivo"

        # Restrição de orçamento
        problema += pulp.lpSum(alocacao_recursos.values()) <= orcamento, "Restrição de Orçamento"

        # Resolvendo o problema
        problema.solve()

        # Resultados
        st.subheader("Resultados da Otimização")

        if problema.status == pulp.LpStatusOptimal:
            st.success("Solução Ótima Encontrada!")
            st.write("Recursos alocados para melhorar as notas do Ensino Fundamental e Médio:")
            for col in notas_fundamental_medio:
                st.write(f"{col}: R$ {alocacao_recursos[col].varValue:.2f}")

            st.write(
                f"Orçamento total utilizado: R$ {sum([alocacao_recursos[col].varValue for col in notas_fundamental_medio]):.2f}")
        else:
            st.error("Não foi possível encontrar uma solução ótima.")

    # Exibe o status da solução
    st.write(f"Status da Solução: {pulp.LpStatus[problema.status]}")
else:
    st.error("Por favor, selecione as notas do Ensino Fundamental, Médio e Superior.")
