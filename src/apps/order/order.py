from datetime import date
from typing import Tuple

import streamlit as st
from src.database.loader import Loader
from src.database.tables import CustomerTable, ManagerTable, OrdersTable, ProductTable
from src.entities import AccessLevel, Customer, Manager, Order, OrderType, Product

from ..app_template import AppTemplate
from ..utils import (
    EntityIdentifierType,
    get_entity_from_df,
    get_entity_from_selectbox,
    get_entity_identifier_column,
)
from .product_info import ProductInfo
from .summary import OrderSummary


class OrderApp(AppTemplate):
    @property
    def new_order_id(self) -> str:
        max_order_id = self.dataloader.data[OrdersTable().query.table_name]["order_id"].max()
        order_id_int = int(max_order_id.replace("MDS", ""))
        return "MDS" + str(int(1e7) + order_id_int)[1:]

    def run(self):
        product, customer = None, None

        manager = self.write_manager_info()

        self.download_data()

        # TODO: Order editing
        # add select box for getting order id for editing
        # filter orders_df in dataloader to selected id
        # overwrite manager with currently logged in
        # get customer id and load customer entity
        # extract rest of fixed variables (date, type)
        # loop through rows instantiate Orders and append to st.session_state.order_rows
        # show summary will be invoked automatically
        # now new items can be added or rows removed as in typical order

        # TODO: Order deletion
        # if order id is selected for editing, load as described above
        # but now pressing 'Save' button saves using UPDATE status tyep

        order_date, order_type, customer = self.date_order_type_and_customer_selection()

        if customer:
            product, selected_quantity, discount = self.product_selection(customer)

        if product and customer:
            order_row = Order(
                order_id=self.new_order_id,
                manager=manager,
                customer=customer,
                order_date=order_date,
                order_type=order_type,
                product=product,
                quantity=selected_quantity,
                discount=discount,
            )

            if st.button("Add to order"):
                st.session_state.order_rows.append(order_row)

            if len(st.session_state.order_rows) > 0:
                order_summary = OrderSummary(
                    order_rows=st.session_state.order_rows,
                    buyer=customer,
                    processor=self.output_table.processing,
                )
                order_summary.show()

                if order_summary.submitted:
                    order_df = order_summary.df
                    self.save_entity_df(order_df)
                    st.session_state.order_rows = []

    def write_manager_info(self: Loader) -> Manager:
        manager = get_entity_from_df(
            entity_type=Manager,
            df=self.dataloader.data[ManagerTable.query.table_name],
            entity_identifier_column=get_entity_identifier_column(Manager, EntityIdentifierType.ID),
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
                df = self.dataloader.data[CustomerTable().query.table_name]
                entity_identifier_column = get_entity_identifier_column(
                    Customer, EntityIdentifierType.NAME
                )
                customer = get_entity_from_selectbox(
                    entity_type=Customer, df=df, entity_identifier_column=entity_identifier_column
                )

        return order_date, order_type, customer

    def product_selection(self, customer: Customer) -> Tuple[Product, int, float]:
        with st.container():
            product_col, quantity_col = st.columns([4, 1])
            active_discount = 0.0

            with product_col:
                # TODO: get product list from inventory table (grouped orders)
                # otherwise it's populated with inactive products
                product = get_entity_from_selectbox(
                    entity_type=Product,
                    df=self.dataloader.data[ProductTable().query.table_name],
                    entity_identifier_column=get_entity_identifier_column(
                        Product, EntityIdentifierType.NAME
                    ),
                )
                if product:
                    product_info = ProductInfo(self.dataloader)
                    st.write("initialize prod info")
                    product_info.show(product, customer)
                    active_discount = product_info.active_discount

            with quantity_col:
                selected_quantity = st.number_input("Enter quantity", min_value=1)

            return product, selected_quantity, active_discount
