from typing import List

import pandas as pd
import streamlit as st
from src.apps import utils
from src.entities import Order
from src.processing import ProcessingStrategy, RowStatus

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
        self, order_rows: List[Order], processor: ProcessingStrategy, row_status=RowStatus
    ) -> None:
        self.order_rows = order_rows
        self.processor = processor
        self.submitted: bool = False
        self.row_status = row_status

    @property
    def df(self) -> pd.DataFrame:
        return self.processor.process(self.order_rows, row_status=self.row_status)

    def show(self) -> None:
        summary_col, removal_col = st.columns([4, 1])

        with removal_col:
            self.remove_items()
            # self.download_invoice()

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

                if st.form_submit_button("Delete order"):
                    self.row_status = RowStatus.DELETE
                    self.submitted = True

                if st.form_submit_button("Cancel",):
                    st.session_state.order_rows = []

    def remove_items(self):
        order_row_indices = list(range(len(self.order_rows)))
        order_row_to_remove_index = st.selectbox("Remove order row", order_row_indices)
        if st.button("Remove order row"):
            del self.order_rows[order_row_to_remove_index]

