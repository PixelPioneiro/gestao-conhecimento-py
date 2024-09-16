import streamlit as st
import plotly.express as px

cols = st.columns(3)
meds = cols[0].multiselect(
    'Medidas', st.session_state['medida'])
dims = cols[1].selectbox(
    'Dimensões', st.session_state['dimensao'])
time = cols[2].selectbox(
    'Dimensões Tempo', st.session_state['dimensao_tempo'])
st.text('Visualização')
if len(meds) > 0:
    if len(meds) >= 1:
        st.subheader('Distribuição - Histograma')
        st.plotly_chart(
            px.histogram(st.session_state['df'], x=meds)
        )
    if len(meds) >= 2:
        st.subheader('Relacionamento - Pontos/Dispersão')
        st.plotly_chart(
            px.scatter(
                st.session_state['df'], x=meds[0], y=meds[1]
            )
        )
    if len(meds) == 3:
        st.subheader('Relacionamento - Bolhas')
        try:
            st.plotly_chart(
                px.scatter(st.session_state['df'],
                    x=meds[0], y=meds[1], size=meds[2]
                )
            )
        except:
            st.text('Não pode haver valores negativos')
    gr = st.session_state['df'].groupby(dims)[
        meds[0]].sum().reset_index()
    with st.expander(label='mostrar tabela', expanded=False):
        st.dataframe(
            gr, hide_index=True, use_container_width=True
        )
    st.plotly_chart(
        px.pie(gr, names=dims, values=meds[0], hole=0.5))
    gr = st.session_state['df'].groupby(
        [time] + [dims])[meds[0]].sum().reset_index()
    with st.expander(label='Mostrar Tabela', expanded=False):
        st.dataframe(
            gr, hide_index=True, use_container_width=True
        )
    if len(gr[time].unique()) <= 6:
        if len(gr[dims].unique()) <= 6:
            st.plotly_chart(
                px.bar(
                    data_frame=gr, x=str(time),
                    y=meds[0], color=dims))
        else:
            st.plotly_chart(
                px.area(
                    data_frame=gr,
                    x=str(time),
                    y=meds[0],
                    color=dims
                )
            )
    else:
        st.plotly_chart(
            px.line(
                data_frame=gr,
                x=str(time),
                y=meds[0],
                color=dims
            )
        )
