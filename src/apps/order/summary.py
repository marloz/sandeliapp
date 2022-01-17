from src.entities import Orders
import streamlit as st
import pandas as pd
from typing import List


ORDER_SUMMARY_COLUMNS = [
    'product_name',
    'quantity',
    'price',
    'discount',
    'price_with_discount',
    'sum',
    'sum_vat'
]


def remove_item(order_rows: List[Orders]) -> None:
    order_row_indices = list(range(len(order_rows)))
    order_row_to_remove_index = st.selectbox('Remove order row',
                                             order_row_indices)
    if st.button('Remove order row'):
        del st.session_state['order_rows'][order_row_to_remove_index]


def show_order_summary(order_df: pd.DataFrame) -> bool:
    summary_col, removal_col = st.columns([4, 1])
    order_rows = st.session_state['order_rows']

    with removal_col:
        remove_item(order_rows)

    with summary_col:
        order_summary = st.empty()
        with order_summary.form('Summary'):
            st.header(f'Order summary: {order_df.order_id[0]}')
            st.write(order_df[ORDER_SUMMARY_COLUMNS]
                     .style.format(precision=2))
            submitted = st.form_submit_button('Save order')
            return submitted
