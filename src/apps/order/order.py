from datetime import date
from typing import Tuple

import streamlit as st
from src.database.loader import Loader
from src.database.tables import CustomerTable, ManagerTable, ProductTable
from src.entities import Customer, Manager, Orders, OrderType, Product

from ..app_template import AppTemplate
from ..utils import get_entity_from_df, get_entity_from_selectbox, get_entity_identifier_column
from .product_info import ProductInfo
from .summary import show_order_summary

st.session_state["order_rows"] = []


class OrderApp(AppTemplate):
    def run(self):
        product, customer = None, None

        manager = self.write_manager_info()

        self.download_data()

        order_date, order_type, customer = self.date_order_type_and_customer_selection()

        if customer:
            product, selected_quantity, discount = self.product_selection(customer)

        if product and customer:
            order_row = Orders(
                manager=manager,
                customer=customer,
                order_date=order_date,
                order_type=order_type,
                product=product,
                quantity=selected_quantity,
                discount=discount,
            )

            if st.button("Add to order"):
                st.session_state["order_rows"].append(order_row)

            if len(st.session_state["order_rows"]) > 0:
                order_df = self.entity_processor().process(st.session_state["order_rows"])
                submitted = show_order_summary(order_df, customer)

                if submitted:
                    self.save_entity_df(order_df, output_table=self.output_table)
                    self.dataloader.update(self.output_table)
                    st.session_state["order_rows"] = []

    def write_manager_info(self: Loader) -> Manager:
        manager = get_entity_from_df(
            entity_type=Manager,
            df=self.dataloader.data[ManagerTable.name()],
            entity_identifier_column=get_entity_identifier_column(Manager, "id"),
            entity_identifier=st.session_state.current_user,
        )
        st.write(manager)
        return manager

    def date_order_type_and_customer_selection(self) -> Tuple[date, str, Customer]:
        with st.container():
            date_col, type_col, customer_col = st.columns([1, 1, 4])

            with date_col:
                order_date = st.date_input("Order date")

            with type_col:
                order_type = st.selectbox("Order type", [e.value for e in OrderType])

            with customer_col:
                df = self.dataloader.data[CustomerTable.name()]
                entity_identifier_column = get_entity_identifier_column(Customer, "name")
                customer = get_entity_from_selectbox(
                    entity_type=Customer, df=df, entity_identifier_column=entity_identifier_column
                )

        return order_date, order_type, customer

    def product_selection(self, customer: Customer) -> Tuple[Product, int, float]:
        with st.container():
            product_col, quantity_col = st.columns([4, 1])
            active_discount = 0.0

            with product_col:
                product = get_entity_from_selectbox(
                    entity_type=Product,
                    df=self.dataloader.data[ProductTable.name()],
                    entity_identifier_column=get_entity_identifier_column(Product, "name"),
                )
                if product:
                    product_info = ProductInfo(self.dataloader)
                    product_info.show(product, customer)
                    active_discount = product_info.active_discount

            with quantity_col:
                selected_quantity = st.number_input("Enter quantity", min_value=1)

            return product, selected_quantity, active_discount
