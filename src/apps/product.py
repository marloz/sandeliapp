import streamlit as st
from hydralit import HydraHeadApp
from src.entities import Product
from src.io.exporter import Exporter
from src.config import DATA_PATH
from uuid import uuid1
import os


class ProductApp(HydraHeadApp):

    def run(self):

        st.write('Add new product')
        product_name = st.text_input('Product name')
        product_price = st.number_input('Product price EUR')
        product_category = st.text_input('Product category')
        manufacturer = st.text_input('Manufacturer')

        product = Product(product_id=str(uuid1()),
                          product_name=product_name,
                          price=product_price,
                          product_category=product_category,
                          manufacturer=manufacturer)

        if st.button('Save product'):
            output_path = os.path.join(DATA_PATH, 'product.csv')
            Exporter(product).export(output_path)
            st.write(f'Product {product} added to database')
