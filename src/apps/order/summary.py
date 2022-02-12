import base64
from typing import List

import pandas as pd
import streamlit as st
from config.paths import PROJECT_ROOT
from src.entities import Orders
from src.invoice import invoice

ORDER_SUMMARY_COLUMNS = [
    "product_name",
    "quantity",
    "price",
    "discount",
    "price_with_discount",
    "sum",
    "sum_vat",
]


def remove_item(order_rows: List[Orders]) -> None:
    order_row_indices = list(range(len(order_rows)))
    order_row_to_remove_index = st.selectbox("Remove order row", order_row_indices)
    if st.button("Remove order row"):
        del st.session_state["order_rows"][order_row_to_remove_index]


def download_invoice():
    with open(PROJECT_ROOT + "/output.pdf", "rb") as pdf:
        st.download_button(
            label="Download invoice pdf",
            data=pdf.read(),
            file_name="vat_invoice_2020_02_06.pdf",
            mime="application/octet-stream",
        )


def show_order_summary(order_df: pd.DataFrame) -> bool:
    summary_col, removal_col = st.columns([4, 1])
    order_rows = st.session_state["order_rows"]

    with removal_col:
        remove_item(order_rows)
        download_invoice()

    with summary_col:
        order_summary = st.empty()
        with order_summary.form("Summary"):
            st.header(f"Order summary: {order_df.order_id[0]}")
            st.write("Payment due", order_df["payment_due"][0])
            order_df = order_df[ORDER_SUMMARY_COLUMNS]
            st.write(order_df.style.format(precision=2))
            st.write("Total sum without VAT:", order_df["sum"].sum())
            st.write("Total sum with VAT:", order_df["sum_vat"].sum())
            submitted = st.form_submit_button("Save order")
            return submitted

