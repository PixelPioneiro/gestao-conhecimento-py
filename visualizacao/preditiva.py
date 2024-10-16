import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px

# Configurações de layout da página
st.title("Análise Preditiva: Modelos Supervisionados e Não Supervisionados")

df = st.session_state['df']  # Carrega o dataframe da sessão


# Função para transformar colunas categóricas em numéricas
def encode_features(df, features):
    df_encoded = df.copy()
    for col in features:
        if df_encoded[col].dtype == 'object':  # Verifica se a coluna é categórica
            encoder = LabelEncoder()
            df_encoded[col] = encoder.fit_transform(df_encoded[col])
    return df_encoded


# Seleção de colunas para modelagem
st.subheader("Seleção de Variáveis")

# Escolha da variável alvo (target) e features (X)
target = st.selectbox("Selecione a variável alvo (target)", df.columns)
features = st.multiselect("Selecione as variáveis preditoras (features)", df.columns.difference([target]))

if target and features:
    # Certifica que as features e o target são numéricos
    df_encoded = encode_features(df, features + [target])

    X = df_encoded[features]
    y = df_encoded[target]

    # Divisão dos dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # -------------------- Modelos Supervisionados --------------------

    st.subheader("Modelos Supervisionados")

    # 1. Regressão Linear
    st.subheader("Regressão Linear")

    if y_train.dtype in [int, float]:  # Verifica se a variável alvo é contínua
        model_linear = LinearRegression()
        model_linear.fit(X_train, y_train)
        y_pred_linear = model_linear.predict(X_test)
        mse_linear = mean_squared_error(y_test, y_pred_linear)
        st.write(f"Erro Quadrático Médio (MSE): {mse_linear}")

        # Gráfico Regressão Linear
        fig_linear = px.scatter(x=y_test, y=y_pred_linear, labels={'x': 'Valores Reais', 'y': 'Valores Previstos'},
                                title="Regressão Linear: Valores Reais vs Previsão")
        st.plotly_chart(fig_linear)

    # 2. Regressão Logística
    st.subheader("Regressão Logística")

    if y_train.nunique() == 2:  # Verifica se é uma classificação binária
        model_logistic = LogisticRegression(max_iter=1000)
        model_logistic.fit(X_train, y_train)
        y_pred_logistic = model_logistic.predict(X_test)
        precision_logistic = accuracy_score(y_test, y_pred_logistic)
        st.write(f"Precisão: {precision_logistic}")
        st.write("Valores reais vs previsões")
        st.write(pd.DataFrame({'Real': y_test, 'Previsão': y_pred_logistic}))

    # 3. Árvore de Decisão
    st.subheader("Árvore de Decisão")

    model_tree = DecisionTreeClassifier(random_state=42)
    model_tree.fit(X_train, y_train)
    y_pred_tree = model_tree.predict(X_test)
    precision_tree = accuracy_score(y_test, y_pred_tree)
    st.write(f"Precisão: {precision_tree}")
    st.write("Valores reais vs previsões")
    st.write(pd.DataFrame({'Real': y_test, 'Previsão': y_pred_tree}))

    # -------------------- Modelos Não Supervisionados --------------------

    st.subheader("Modelos Não Supervisionados")

    # 1. KMeans
    st.subheader("KMeans")

    # Número de clusters para KMeans
    n_clusters = st.slider('Número de Clusters (K)', 2, 10, 3)
    model_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = model_kmeans.fit_predict(X)

    st.write(f"Soma dos Quadrados das Distâncias aos Centróides: {model_kmeans.inertia_}")

    # Adiciona os clusters ao DataFrame original para visualização
    df_encoded['Cluster'] = cluster_labels
    fig_kmeans = px.scatter_matrix(df_encoded, dimensions=features, color='Cluster',
                                   title=f"KMeans com {n_clusters} Clusters")
    st.plotly_chart(fig_kmeans)

    # 2. PCA (Análise de Componentes Principais)
    st.subheader("PCA (Análise de Componentes Principais)")

    # Evitar o erro do slider: Certificar que há mais de uma feature para o PCA
    if len(features) > 1:
        max_components = min(len(features), 10)  # Limite de componentes para o PCA
        # Garantir que o valor máximo seja maior que o valor mínimo
        if max_components > 2:
            # Número de componentes para PCA
            n_components = st.slider('Número de Componentes (PCA)', 2, max_components, 2)
            model_pca = PCA(n_components=n_components)
            X_pca = model_pca.fit_transform(X)

            st.write(f"Proporção de variância explicada por componente: {model_pca.explained_variance_ratio_}")
            st.write(f"Variância explicada acumulada: {model_pca.explained_variance_ratio_.cumsum()}")

            # DataFrame com componentes principais
            pca_df = pd.DataFrame(X_pca, columns=[f'PC{i + 1}' for i in range(n_components)])
            fig_pca = px.scatter(pca_df, x='PC1', y='PC2', title="PCA - Componentes Principais")
            st.plotly_chart(fig_pca)
        else:
            st.warning("O número de componentes PCA deve ser maior que 2.")
    else:
        st.warning("PCA requer mais de uma feature. Selecione ao menos duas variáveis.")
