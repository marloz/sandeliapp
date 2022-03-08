from typing import List

import pandas as pd
import streamlit as st
from config.paths import INVOICE_PATH
from src.apps import utils
from src.entities import Customer, CustomerType, Order, PaymetTerms
from src.invoice.base import InvoiceInfo, InvoiceType
from src.invoice.vat import VATInvoice
from src.processing import ProcessingStrategy, RowStatus

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

ORDER_SUMMARY_COLUMNS = [
    "order_id",
    "product_name",
    "quantity",
    "price",
    "discount",
    "price_with_discount",
    "sum",
    "sum_vat",
    "payment_due",
]


class OrderSummary:
    def __init__(
        self, order_rows: List[Order], buyer: Customer, processor: ProcessingStrategy
    ) -> None:
        self.order_rows = order_rows
        self.buyer = buyer
        self.processor = processor
        self.submitted: bool = False

    @property
    def df(self) -> pd.DataFrame:
        return self.processor.process(self.order_rows, row_status=RowStatus.INSERT)

    def show(self) -> None:
        summary_col, removal_col = st.columns([4, 1])

        with removal_col:
            self.remove_items()
            self.download_invoice()

        with summary_col:
            order_summary = st.empty()
            with order_summary.form("Summary"):
                st.header("Order summary")
                order_df = self.df[ORDER_SUMMARY_COLUMNS]
                st.write(order_df.style.format(precision=2))
                order_summary = utils.calculate_order_summary(order_df)
                for key, value in order_summary.items():
                    st.write(f"{key}: {value}")
                self.submitted = st.form_submit_button("Save order")

    def remove_items(self):
        order_row_indices = list(range(len(self.order_rows)))
        order_row_to_remove_index = st.selectbox("Remove order row", order_row_indices)
        if st.button("Remove order row"):
            del self.order_rows[order_row_to_remove_index]

    def download_invoice(self):
        df = self.df
        invoice_info = InvoiceInfo(
            # TODO: probably need select box, because order type != invoice type
            invoice_type=InvoiceType.VAT,
            invoice_number=df.iloc[0].order_id,
            invoice_date=df.iloc[0].order_date,
            buyer=self.buyer,
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
