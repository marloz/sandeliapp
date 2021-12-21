import streamlit as st
from src.pages import welcome


def app():

    st.write('Sandeliapp [tm]')
    email = st.text_input('Enter email')
    password = st.text_input('Enter password')

    if st.button('Login'):
        st.write(f'Login successful')
        welcome.app()
