from typing import List

import pandas as pd
import streamlit as st
from config.paths import INVOICE_PATH
from src.apps import utils
from src.entities import Customer, CustomerType, Orders, PaymetTerms
from src.invoice.base import InvoiceInfo, InvoiceType
from src.invoice.vat import VATInvoice

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


def remove_item(order_rows: List[Orders]) -> None:
    order_row_indices = list(range(len(order_rows)))
    order_row_to_remove_index = st.selectbox("Remove order row", order_row_indices)
    if st.button("Remove order row"):
        del st.session_state["order_rows"][order_row_to_remove_index]


def download_invoice(order_df: pd.DataFrame, buyer: Customer):
    invoice_info = InvoiceInfo(
        # TODO: probably need select box, because order type != invoice type
        invoice_type=InvoiceType.VAT,
        invoice_number=order_df.iloc[0].order_id,
        invoice_date=order_df.iloc[0].order_date,
        buyer=buyer,
        seller=seller,
        order_df=order_df,
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


def show_order_summary(order_df: pd.DataFrame, buyer: Customer) -> bool:
    summary_col, removal_col = st.columns([4, 1])
    order_rows = st.session_state["order_rows"]

    with removal_col:
        remove_item(order_rows)
        download_invoice(order_df, buyer)

    with summary_col:
        order_summary = st.empty()
        with order_summary.form("Summary"):
            st.header("Order summary")
            order_df = order_df[ORDER_SUMMARY_COLUMNS]
            st.write(order_df.style.format(precision=2))
            order_summary = utils.calculate_order_summary(order_df)
            for key, value in order_summary.items():
                st.write(f"{key}: {value}")
            submitted = st.form_submit_button("Save order")
            return submitted

