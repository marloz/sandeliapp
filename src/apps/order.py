from src.entities import Customer, Manager, Product, OrderRow
from src.io.loader import preload_data, EntityDataLoader
from src.io.exporter import Exporter
from src.config import DATA_PATH, DATASOURCES, ORDER_TYPES, VAT
import streamlit as st
from hydralit import HydraHeadApp
import pandas as pd
import os
import time

st.session_state['order_rows'] = []

ORDER_SUMMARY_COLUMNS = [
    'product_name',
    'quantity',
    'unit_price',
    'discount',
    'unit_price_discount',
    'sum',
    'sum_vat'
]


class OrderApp(HydraHeadApp):

    def __init__(self):
        self.order_rows = []

    def run(self):

        MANAGER_ID = 'some_email@medexy.lt'

        # Load and cache data to be used
        data_loader = preload_data(DATASOURCES)

        # Print out manager
        manager = data_loader.get_single_entity_instance(
            entity=Manager, entity_identifier=MANAGER_ID
        )
        st.write(manager)
        self._select_fixed_order_variables(data_loader)
        self._add_item_to_order(data_loader)
        self._show_order_summary()

    def _select_fixed_order_variables(self, data_loader: EntityDataLoader):
        with st.container():
            date_col, type_col, customer_col = st.columns([1, 1, 4])
            with date_col:
                order_date = st.date_input('Order date')
            with type_col:
                order_type = st.selectbox('Order type', ORDER_TYPES)
            with customer_col:
                customer_list = data_loader.data['customer']['customer_name'] \
                    .tolist()
                selected_customer = st.selectbox(
                    'Select customer', customer_list)
                customer = data_loader.get_single_entity_instance(
                    Customer,
                    entity_identifier=selected_customer,
                    identifier_type='name')

    def _check_inventory(self, selected_product: str) -> None:
        if st.button('Check inventory'):
            st.write(f'Inventory holds 2 {selected_product} items')

    def _add_item_to_order(self, data_loader: EntityDataLoader) -> None:
        with st.container():
            product_col, quantity_col, discount_col = st.columns([4, 1, 1])
            with product_col:
                product_list = data_loader.data['product']['product_name'] \
                    .tolist()
                selected_product = st.selectbox('Select product', product_list)
                self._check_inventory(selected_product)
                product = data_loader.get_single_entity_instance(
                    Product,
                    entity_identifier=selected_product,
                    identifier_type='name')
            with quantity_col:
                selected_quantity = st.number_input(
                    'Enter quantity', min_value=1)
            with discount_col:
                entered_discount = st.number_input('Enter discount %', min_value=0.,
                                                   max_value=100., step=10.)
        order_row = OrderRow(product=product,
                             quantity=selected_quantity,
                             discount=entered_discount)
        if st.button('Add to order'):
            st.session_state['order_rows'].append(order_row)

    def _show_order_summary(self):
        if len(st.session_state['order_rows']) > 0:
            summary_col, removal_col = st.columns([4, 1])
            order_rows = st.session_state['order_rows']

            with removal_col:
                order_row_indices = list(range(len(order_rows)))
                order_row_to_remove_index = st.selectbox(
                    'Remove order row', order_row_indices)
                if st.button('Remove order row'):
                    del st.session_state['order_rows'][order_row_to_remove_index]

            with summary_col:
                order_summary = st.empty()

                with order_summary.form('Summary'):
                    st.header('Order summary')
                    order_df = pd.concat((Exporter(order_row).prepare_for_export()
                                          for order_row in order_rows))
                    order_df = add_order_amounts(order_df) \
                        .reset_index(drop=True)
                    st.write(
                        order_df[ORDER_SUMMARY_COLUMNS].style.format(precision=2))

                # Write to history
                    submit = st.form_submit_button('Save order')

                if submit:
                    output_path = os.path.join(DATA_PATH, 'orders.csv')
                    with st.spinner("🤓 now redirecting to application...."):
                        st.success(f'Order exported to {output_path}')
                        time.sleep(1)
                        st.session_state['order_rows'] = []
                    order_summary = st.empty()


def add_order_amounts(order_df: pd.DataFrame) -> pd.DataFrame:
    return order_df.assign(
        discount_amount=lambda x: x['unit_price'].mul(x['discount']).div(100),
        unit_price_vat=lambda x: x['unit_price'] * VAT,
        unit_price_discount=lambda x: x['unit_price'].sub(
            x['discount_amount']),
        unit_price_discount_vat=lambda x: x['unit_price_discount'] * VAT,
        sum=lambda x: x['unit_price_discount'] * x['quantity'],
        sum_vat=lambda x: x['unit_price_discount_vat'] * x['quantity']
    )
