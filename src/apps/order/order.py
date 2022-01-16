from .product_info import ProductInfo
from .summary import show_order_summary
from ..utils import get_entity_from_selectbox, get_entity_from_df, get_entity_identifier_column
from ..app_template import AppTemplate
from src.database.loader import Loader
from src.entities import Customer, Manager, Product, Orders, Entity, OrderType

import streamlit as st

from datetime import date
from typing import Tuple, Type

st.session_state['order_rows'] = []


class OrderApp(AppTemplate):

    def __init__(self, entity_type: Type[Entity],
                 dataloader: Loader) -> None:
        super().__init__(entity_type, dataloader)
        self.dataloader = dataloader

    def run(self):
        product, customer = None, None

        manager = self.write_manager_info()
        order_date, order_type, customer = self.date_order_type_and_customer_selection()

        if customer:
            product, selected_quantity, entered_discount = \
                self.product_quantity_and_discount_selection(customer)

        if product and customer:
            order_row = Orders(manager=manager,
                               customer=customer,
                               order_date=order_date,
                               order_type=order_type,
                               product=product,
                               quantity=selected_quantity,
                               discount=entered_discount)

            if st.button('Add to order'):
                st.session_state['order_rows'].append(order_row)

            if len(st.session_state['order_rows']) > 0:
                order_df = self.entity_processor() \
                    .process(st.session_state['order_rows'])
                submitted = show_order_summary(order_df)

                if submitted:
                    self.save_entity_df(order_df,
                                        output_table=self.output_table)
                    self.dataloader.update(self.output_table)
                    st.session_state['order_rows'] = []

    def write_manager_info(self: Loader) -> Manager:
        manager = get_entity_from_df(
            entity_type=Manager,
            df=self.dataloader.data[Manager.name()],
            entity_identifier_column=get_entity_identifier_column(
                Manager, 'id'),
            entity_identifier=st.session_state.current_user)
        st.write(manager)
        return manager

    def date_order_type_and_customer_selection(self) -> Tuple[date, str, Customer]:
        with st.container():
            date_col, type_col, customer_col = st.columns([1, 1, 4])

            with date_col:
                order_date = st.date_input('Order date')

            with type_col:
                order_type = st.selectbox(
                    'Order type', [e.value for e in OrderType])

            with customer_col:
                df = self.dataloader.data[Customer.name()]
                entity_identifier_column = get_entity_identifier_column(Customer,
                                                                        'name')
                customer = get_entity_from_selectbox(
                    entity_type=Customer,
                    df=df,
                    entity_identifier_column=entity_identifier_column)

        return order_date, order_type, customer

    def product_quantity_and_discount_selection(self, customer: Customer
                                                ) -> Tuple[Product, int, float]:
        with st.container():
            product_col, quantity_col, discount_col = st.columns([4, 1, 1])

            with product_col:
                product = get_entity_from_selectbox(
                    entity_type=Product,
                    df=self.dataloader.data[Product.name()],
                    entity_identifier_column=get_entity_identifier_column(Product, 'name'))
                if product:
                    ProductInfo(self.dataloader).show(product, customer)

            with quantity_col:
                selected_quantity = st.number_input('Enter quantity',
                                                    min_value=1)

            with discount_col:
                entered_discount = st.number_input('Enter discount %', min_value=0.,
                                                   max_value=100., step=10.)

            return product, selected_quantity, entered_discount
