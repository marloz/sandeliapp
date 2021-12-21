import streamlit as st
from src.entities import Customer
from src.io.exporter import Exporter
from src.config import DATA_PATH
from uuid import uuid1
import os


def app():

    st.write('Add new customer')
    new_customer_name = st.text_input('Customer name')
    customer = Customer(customer_id=str(uuid1()),
                        customer_name=new_customer_name)

    if st.button('Save customer'):
        output_path = os.path.join(DATA_PATH, 'customer.csv')
        Exporter(customer).export(output_path)
        st.write(f'Customer {new_customer_name} added to database')
