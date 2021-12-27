from hydralit import HydraHeadApp
import streamlit as st


class HomeApp(HydraHeadApp):

    def run(self):
        st.write('Welcome to inventory management app')
