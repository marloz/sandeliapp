from datetime import date
from typing import List, Optional, Tuple, Union

import pandas as pd
import streamlit as st
from config.paths import INVOICE_PATH
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
from src.processing import RowStatus

from ..app_template import AppTemplate
from ..utils import (
    EntityIdentifierType,
    get_entity_from_df,
    get_entity_from_selectbox,
    get_entity_identifier_column,
)
from .product_info import ProductInfo
from .summary import OrderSummary

# # TODO: need to have method to load seller from customer table
# seller = Customer(
#     customer_id="0",
#     customer_name="UAB Medexy",
#     customer_type=CustomerType.default,
#     pricing_factor=1.0,
#     payment_terms=PaymetTerms.days_30,
#     address="Ukmergers g. 241",
#     post_code="LT-12345",
#     customer_location="Vilnius",
#     email="info@medexy.lt",
#     telephone="+370 526 53483",
#     customer_code="300154866",
#     vat_code="LT24 3500 0100 0132 3457",
# )

# TODO: this is too complex to navigate with editing conditionals
# TODO: solve by creating subpages (if needed, use complex_nav here https://opensourcelibs.com/lib/hydralit)
# TODO: also see do_redicted method from login page
# TODO: where relevant, refactor widgets to use on_click callbacks and use session state attributes
# TODO: https://docs.streamlit.io/knowledge-base/using-streamlit/widget-updating-session-state
class OrderApp(AppTemplate):
    @property
    def orders_df(self) -> pd.DataFrame:
        return self.dataloader.data[OrdersTable().query.table_name]

    # TODO: this needs to dependent on order type: MDS, MDK, MDT, ...
    def generate_new_order_id(self) -> str:
        max_order_id = self.orders_df["order_id"].max()
        new_order_id_int = int(max_order_id.replace("MDS", "")) + 1
        return "MDS" + str(int(1e7) + new_order_id_int)[1:]

    def run(self) -> None:
        self.download_data()
        self.order_date, self.order_type, self.customer_name = None, None, None
        self.order_id_to_edit = self.get_order_id_to_edit()
        st.session_state.order_rows = self.load_order_to_edit()
        self.order_date = self.select_order_date()
        st.session_state.order_type = self.select_order_type()
        self.print_order_id()
        st.session_state.customer = self.select_customer()
        self.proceed_to_next()

    def get_order_id_to_edit(self) -> str:
        order_id_to_edit = ""
        if st.session_state.current_user_access != AccessLevel.user.value:
            order_id_to_edit = st.text_input("Enter order id to edit")
            existing_ids = self.orders_df["order_id"].unique()
            if order_id_to_edit not in existing_ids and order_id_to_edit != "":
                st.write("Provided id not found in order history!")
        return order_id_to_edit

    def load_order_to_edit(self) -> Union[List[Order], None]:
        if self.order_id_to_edit != "":
            order_df = self.orders_df.loc[lambda x: x.order_id == self.order_id_to_edit]
            order_rows = [self._load_order_row(row) for _, row in order_df.iterrows()]
            self.order_date, self.order_type, self.customer_name = (
                order_rows[0].order_date,
                order_rows[0].order_type,
                order_rows[0].customer.customer_name,
            )
            return order_rows

    def _load_order_row(self, row: pd.Series) -> Order:
        kwargs = {}
        for entity in [Product, Customer, Manager]:
            identifier_column = get_entity_identifier_column(entity, EntityIdentifierType.ID)
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
        return Order(**kwargs)

    def select_order_date(self) -> date:
        return st.date_input("Order date", value=self.order_date)

    def select_order_type(self) -> str:
        options = [self.order_type.value] if self.order_type else [e.value for e in OrderType]
        return st.selectbox("Order type", options)

    def print_order_id(self) -> None:
        if self.order_id_to_edit == "":
            self.order_id = self.generate_new_order_id()
            st.write(f"Order id: {self.order_id}")

    def select_customer(self) -> Customer:
        df = self.dataloader.data[CustomerTable().query.table_name]
        entity_identifier_column = get_entity_identifier_column(Customer, EntityIdentifierType.NAME)
        return get_entity_from_selectbox(
            entity_type=Customer,
            df=df,
            entity_identifier_column=entity_identifier_column,
            default_value=self.customer_name,
        )

    def proceed_to_next(self) -> None:
        if st.button("Next", key="proceed_to_order_items"):
            required_items = ["order_id", "order_date", "order_type", "customer"]
            try:
                assert all(st.session_state[item] is not None for item in required_items)
                self.do_redirect(redirect_target_app="OrderItems")
            except AssertionError:
                st.write("Fill in all fields before proceeding")

    # def new_order(self) -> None:
    #     product = None

    #     order_date, order_type, customer = self.date_order_type_and_customer_selection()

    #     if customer:
    #         product, selected_quantity, discount = self.product_selection(customer)

    #     if product and customer:
    #         order_row = Order(
    #             order_id=st.session_state.order_id,
    #             manager=self.manager,
    #             customer=customer,
    #             order_date=order_date,
    #             order_type=order_type,
    #             product=product,
    #             quantity=selected_quantity,
    #             discount=discount,
    #         )

    #         if st.button("Add to order"):
    #             st.session_state.order_rows.append(order_row)

    # def date_order_type_and_customer_selection(self) -> Tuple[date, str, Customer]:
    #     with st.container():
    #         date_col, type_col, customer_col = st.columns([1, 1, 4])

    #         with date_col:
    #             st.date_input(
    #                 "Order date",
    #                 value=getattr(st.session_state, "order_date", None),
    #                 key="order_date",
    #             )

    #         with type_col:
    #             options = getattr(st.session_state, "order_type", None)
    #             options = [options] if options else [e.value for e in OrderType]
    #             st.selectbox("Order type", options, key="order_type")

    #         with customer_col:
    #             df = self.dataloader.data[CustomerTable().query.table_name]
    #             entity_identifier_column = get_entity_identifier_column(
    #                 Customer, EntityIdentifierType.NAME
    #             )
    #             customer = get_entity_from_selectbox(
    #                 entity_type=Customer,
    #                 df=df,
    #                 entity_identifier_column=entity_identifier_column,
    #                 default_value=st.session_state.customer_name,
    #             )

    #     return st.session_state.order_date, st.session_state.order_type, customer

    # def product_selection(self, customer: Customer) -> Tuple[Product, int, float]:
    #     with st.container():
    #         product_col, quantity_col = st.columns([4, 1])
    #         active_discount = 0.0

    #         with product_col:
    #             active_product_df = self.dataloader.data[ProductTable().query.table_name].loc[
    #                 lambda x: x.product_name.isin(
    #                     self.dataloader.data[InventoryTable().query.table_name].product_name
    #                 )
    #             ]
    #             product = get_entity_from_selectbox(
    #                 entity_type=Product,
    #                 df=active_product_df,
    #                 entity_identifier_column=get_entity_identifier_column(
    #                     Product, EntityIdentifierType.NAME
    #                 ),
    #             )
    #             if product:
    #                 product_info = ProductInfo(self.dataloader)
    #                 product_info.show(product, customer)
    #                 active_discount = product_info.active_discount

    #         with quantity_col:
    #             st.number_input("Enter quantity", min_value=1, key="selected_quantity")

    #         return product, st.session_state.selected_quantity, active_discount

    # def show_order_summary(self) -> None:
    #     if len(st.session_state.order_rows) > 0:
    #         order_summary = OrderSummary(
    #             order_rows=st.session_state.order_rows,
    #             processor=self.output_table.processing,
    #             row_status=self.row_status,
    #         )
    #         order_summary.show()

    #         if order_summary.submitted:
    #             self.save_entity_df(order_summary.df)
    #             st.session_state.order_rows = []
    #             # TODO: debug, why invoice generation fails
    #             # self.download_invoice(order_df, customer)

    # @staticmethod
    # def download_invoice(df: pd.DataFrame, customer: Customer) -> None:
    #     invoice_info = InvoiceInfo(
    #         # TODO: probably need select box, because order type != invoice type
    #         invoice_type=InvoiceType.VAT,
    #         invoice_number=df.iloc[0].order_id,
    #         invoice_date=df.iloc[0].order_date,
    #         buyer=customer,
    #         seller=seller,
    #         order_df=df,
    #     )
    #     invoice = VATInvoice(invoice_info)
    #     invoice.generate()

    #     filename_args = [invoice_info.invoice_type.name, "invoice", invoice_info.invoice_date]
    #     invoice_filename = "_".join(filename_args) + ".pdf"
    #     with open(INVOICE_PATH, "rb") as pdf:
    #         st.download_button(
    #             label="Download invoice pdf",
    #             data=pdf.read(),
    #             file_name=invoice_filename,
    #             mime="application/octet-stream",
    #         )
