from src.entities import Customer
from src.io.exporter import Exporter
from src.io.loader import EntityDataLoader
from src.config import DATA_PATH, DEFAULT_CUSTOMER, COLUMN_NAME_SEPARATOR, ID_SUFFIX
from .utils import get_entity_from_selectbox, generate_id

import streamlit as st
from hydralit import HydraHeadApp

import os
from typing import Optional, Union


class CustomerApp(HydraHeadApp):

    def __init__(self, entity_dataloader: EntityDataLoader):
        self.entity_dataloader = entity_dataloader
        self.customer_current: Optional[Customer] = None

    def run(self):

        new_customer_col, edit_customer_col = st.columns(2)

        with edit_customer_col:
            self.customer_current = self.get_customer_to_edit()

        with new_customer_col:
            customer = self.fill_in_customer_details()

        self.save_customer(customer)

    def get_customer_to_edit(self) -> Union[Customer, None]:
        st.write('Edit customer info')
        selected_customer = get_entity_from_selectbox(
            Customer, self.entity_dataloader)
        if selected_customer != DEFAULT_CUSTOMER:
            return self.entity_dataloader.get_single_entity_instance(
                Customer, selected_customer, identifier_type='name')

    def fill_in_customer_details(self) -> Customer:
        st.write('Fill in new customer details')

        def _gen_caption(attribute_name: str) -> str:
            return attribute_name.replace(COLUMN_NAME_SEPARATOR, ' ').capitalize()

        def _get_value(attribute_name: str) -> str:
            return self.customer_current.__dict__[attribute_name] if self.customer_current else "" \
                if ID_SUFFIX not in attribute_name else generate_id()

        customer_dict = {
            attribute_name: st.text_input(_gen_caption(attribute_name),
                                          value=_get_value(attribute_name))
            for attribute_name in Customer.__annotations__.keys()
        }
        return Customer(**customer_dict)

    def save_customer(self, customer: Customer):
        if st.button('Save customer'):
            output_path = os.path.join(DATA_PATH, 'customer.csv')
            Exporter(customer).export(output_path)
            st.write(f'Customer {customer} added to database {output_path}')
            self.entity_dataloader.load_data()
