import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

pyg_app = StreamlitRenderer(
    st.session_state['df'][
        st.session_state['dimensao'] +
        st.session_state['dimensao_tempo'] +
        st.session_state['medida']
    ]
)
pyg_app.explorer()