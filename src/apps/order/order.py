from datetime import date
from typing import List, Tuple, Union

import pandas as pd
import streamlit as st
from config.paths import INVOICE_PATH
from src.database.loader import Loader
from src.database.tables import (
    CustomerTable,
    InventoryTable,
    ManagerTable,
    OrdersTable,
    ProductTable,
)
from src.entities import (
    AccessLevel,
    Customer,
    CustomerType,
    Manager,
    Order,
    OrderType,
    PaymetTerms,
    Product,
)
from src.invoice.base import InvoiceInfo, InvoiceType
from src.invoice.vat import VATInvoice

from ..app_template import AppTemplate
from ..utils import (
    EntityIdentifierType,
    get_entity_from_df,
    get_entity_from_selectbox,
    get_entity_identifier_column,
)
from .product_info import ProductInfo
from .summary import OrderSummary

# TODO: need to have method to load seller from customer table
seller = Customer(
    customer_id="0",
    customer_name="UAB Medexy",
    customer_type=CustomerType.default,
    pricing_factor=1.0,
    payment_terms=PaymetTerms.days_30,
    address="Ukmergers g. 241",
    post_code="LT-12345",
    customer_location="Vilnius",
    email="info@medexy.lt",
    telephone="+370 526 53483",
    customer_code="300154866",
    vat_code="LT24 3500 0100 0132 3457",
)


class OrderApp(AppTemplate):
    @property
    def new_order_id(self) -> str:
        max_order_id = self.dataloader.data[OrdersTable().query.table_name]["order_id"].max()
        new_order_id_int = int(max_order_id.replace("MDS", "")) + 1
        return "MDS" + str(int(1e7) + new_order_id_int)[1:]

    def run(self):
        self.manager = self.write_manager_info()

        self.download_data()

        self.new_order()

        st.session_state.orders_rows = self.edit_order()

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

        if len(st.session_state.order_rows) > 0:
            order_summary = OrderSummary(
                order_rows=st.session_state.order_rows, processor=self.output_table.processing,
            )
            order_summary.show()

            if order_summary.submitted:
                order_df = order_summary.df
                self.save_entity_df(order_df)
                st.session_state.order_rows = []
                # TODO: debug, why invoice generation fails
                # self.download_invoice(order_df, customer)

    def write_manager_info(self) -> Manager:
        manager = get_entity_from_df(
            entity_type=Manager,
            df=self.dataloader.data[ManagerTable.query.table_name],
            entity_identifier_column=get_entity_identifier_column(Manager, EntityIdentifierType.ID),
            entity_identifier=st.session_state.current_user,
        )
        st.write(manager)
        return manager

    def new_order(self) -> None:
        product, customer = None, None

        order_date, order_type, customer = self.date_order_type_and_customer_selection()

        if customer:
            product, selected_quantity, discount = self.product_selection(customer)

        if product and customer:
            order_row = Order(
                order_id=self.new_order_id,
                manager=self.manager,
                customer=customer,
                order_date=order_date,
                order_type=order_type,
                product=product,
                quantity=selected_quantity,
                discount=discount,
            )

            if st.button("Add to order"):
                st.session_state.order_rows.append(order_row)

    def edit_order(self) -> Union[List[Order], None]:
        if st.session_state.current_user_access != AccessLevel.user.value:
            order_id = st.text_input("Enter order id to edit")
            order_df = self.dataloader.data[OrdersTable().query.table_name].loc[
                lambda x: x.order_id == order_id
            ]
            if order_df.shape[0] > 0:
                orders = []
                for _, row in order_df.iterrows():
                    kwargs = {}
                    for entity in [Product, Customer, Manager]:
                        identifier_column = get_entity_identifier_column(
                            entity, EntityIdentifierType.ID
                        )
                        kwargs[entity.name()] = get_entity_from_df(
                            entity,
                            self.dataloader.data[entity.name()],
                            entity_identifier_column=identifier_column,
                            entity_identifier=row[identifier_column],
                        )

                        kwargs.update(
                            dict(
                                order_id=row["order_id"],
                                order_date=row["order_date"],
                                order_type=row["order_type"],
                                quantity=row["quantity"],
                                discount=row["discount"],
                            )
                        )

                        order = Order(**kwargs)
                        orders.append(order)

                return orders

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
                active_product_df = self.dataloader.data[ProductTable().query.table_name].loc[
                    lambda x: x.product_name.isin(
                        self.dataloader.data[InventoryTable().query.table_name].product_name
                    )
                ]
                product = get_entity_from_selectbox(
                    entity_type=Product,
                    df=active_product_df,
                    entity_identifier_column=get_entity_identifier_column(
                        Product, EntityIdentifierType.NAME
                    ),
                )
                if product:
                    product_info = ProductInfo(self.dataloader)
                    product_info.show(product, customer)
                    active_discount = product_info.active_discount

            with quantity_col:
                selected_quantity = st.number_input("Enter quantity", min_value=1)

            return product, selected_quantity, active_discount

    @staticmethod
    def download_invoice(df: pd.DataFrame, customer: Customer) -> None:
        invoice_info = InvoiceInfo(
            # TODO: probably need select box, because order type != invoice type
            invoice_type=InvoiceType.VAT,
            invoice_number=df.iloc[0].order_id,
            invoice_date=df.iloc[0].order_date,
            buyer=customer,
            seller=seller,
            order_df=df,
        )
        invoice = VATInvoice(invoice_info)
        invoice.generate()

        filename_args = [invoice_info.invoice_type.name, "invoice", invoice_info.invoice_date]
        invoice_filename = "_".join(filename_args) + ".pdf"
        with open(INVOICE_PATH, "rb") as pdf:
            st.download_button(
                label="Download invoice pdf",
                data=pdf.read(),
                file_name=invoice_filename,
                mime="application/octet-stream",
            )
