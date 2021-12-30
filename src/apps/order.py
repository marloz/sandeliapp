from .utils import get_entity_from_selectbox

from src.entities import Customer, Manager, Product, OrderRow, Entity
from src.io.loader import CountDataLoader, CountTable, EntityDataLoader, fill_table_info_from_alias
from src.io.exporter import Exporter
from src.config import DATA_PATH, ORDER_TYPES, VAT, DEFAULT_CUSTOMER

import streamlit as st
from hydralit import HydraHeadApp
import pandas as pd
import os
from datetime import date
from typing import Tuple, List, Optional
from uuid import uuid1

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
MANAGER_ID = 'some_email@medexy.lt'
NEGATIVE_QUANTITY_TYPES = ['stock refill', 'return']
OUTPUT_PATH = os.path.join(DATA_PATH, 'order.csv')


class OrderApp(HydraHeadApp):

    def __init__(self, entity_dataloader: EntityDataLoader) -> None:
        self.order_rows: List[OrderRow] = []
        self.entity_dataloader = entity_dataloader
        self.order_dataloader: Optional[CountDataLoader] = None

    def run(self):

        self.order_dataloader = self.load_orders()

        manager = self.entity_dataloader.get_single_entity_instance(
            entity=Manager, entity_identifier=MANAGER_ID
        )
        st.write(manager)

        order_date, order_type, customer = self.select_fixed_order_variables()
        product, selected_quantity, entered_discount = self.get_item_details()

        order_row = OrderRow(manager=manager,
                             customer=customer,
                             order_date=order_date,
                             order_type=order_type,
                             product=product,
                             quantity=selected_quantity,
                             discount=entered_discount)

        if st.button('Add to order'):
            st.session_state['order_rows'].append(order_row)
        self.show_order_summary()

    def load_orders(self) -> CountDataLoader:
        table_info = fill_table_info_from_alias(
            'order',
            groupby='product_name',
            aggregation_dict={'quantity': 'sum'})
        self.order_table_info = CountTable(**table_info)
        loader = CountDataLoader([self.order_table_info])
        loader.load_data()
        return loader

    def select_fixed_order_variables(self) -> Tuple[date, str, str]:
        with st.container():
            date_col, type_col, customer_col = st.columns([1, 1, 4])

            with date_col:
                order_date = st.date_input('Order date')

            with type_col:
                order_type = st.selectbox('Order type', ORDER_TYPES)

            with customer_col:
                if order_type in NEGATIVE_QUANTITY_TYPES:
                    selected_customer = DEFAULT_CUSTOMER
                else:
                    selected_customer = get_entity_from_selectbox(
                        Customer, self.entity_dataloader)
                customer = self.entity_dataloader.get_single_entity_instance(
                    Customer,
                    entity_identifier=selected_customer,
                    identifier_type='name')

        return order_date, order_type, customer

    def get_item_details(self) -> Tuple[Product, int, float]:
        with st.container():
            (product_col, quantity_col,
             discount_col, inventory_col) = st.columns([4, 1, 1, 1])

            with product_col:
                selected_product = get_entity_from_selectbox(
                    Product, self.entity_dataloader)
                product = self.entity_dataloader.get_single_entity_instance(
                    Product,
                    entity_identifier=selected_product,
                    identifier_type='name')

            with quantity_col:
                selected_quantity = st.number_input(
                    'Enter quantity', min_value=1)

            with discount_col:
                entered_discount = st.number_input('Enter discount %', min_value=0.,
                                                   max_value=100., step=10.)

            with inventory_col:
                self.check_inventory(selected_product)

        return product, selected_quantity, entered_discount

    def check_inventory(self, selected_product: str) -> None:
        if st.button('Check inventory'):
            st.write(self.order_dataloader.data['order'].loc[selected_product])

    def show_order_summary(self):
        if len(st.session_state['order_rows']) > 0:
            summary_col, removal_col = st.columns([4, 1])
            order_rows = st.session_state['order_rows']

            with removal_col:
                self.remove_item(order_rows)

            with summary_col:
                order_summary = st.empty()

                with order_summary.form('Summary'):
                    st.header('Order summary')
                    order_df = self.prepare_order_df(order_rows)
                    st.write(
                        order_df[ORDER_SUMMARY_COLUMNS].style.format(precision=2))
                    submit = st.form_submit_button('Save order')

                if submit:
                    self.save_order(OUTPUT_PATH, order_df)
                    st.session_state['order_rows'] = []
                    order_summary = st.empty()

    @staticmethod
    def remove_item(order_rows: List[OrderRow]) -> None:
        order_row_indices = list(range(len(order_rows)))
        order_row_to_remove_index = st.selectbox(
            'Remove order row', order_row_indices)
        if st.button('Remove order row'):
            del st.session_state['order_rows'][order_row_to_remove_index]

    def prepare_order_df(self, order_rows: List[OrderRow]) -> pd.DataFrame:
        return pd.concat((Exporter(order_row).prepare_for_export()
                          for order_row in order_rows)) \
            .pipe(self.add_order_amounts) \
            .reset_index(drop=True) \
            .assign(order_id=str(uuid1()))[self.order_table_info.table_columns]

    @staticmethod
    def add_order_amounts(order_df: pd.DataFrame) -> pd.DataFrame:
        if order_df['order_type'].unique()[0] in NEGATIVE_QUANTITY_TYPES:
            order_df['quantity'] = order_df['quantity'] * -1
        return order_df.assign(
            discount_amount=lambda x: x['unit_price'].mul(
                x['discount']).div(100),
            unit_price_vat=lambda x: x['unit_price'] * VAT,
            unit_price_discount=lambda x: x['unit_price'].sub(
                x['discount_amount']),
            unit_price_discount_vat=lambda x: x['unit_price_discount'] * VAT,
            sum=lambda x: x['unit_price_discount'] * x['quantity'],
            sum_vat=lambda x: x['unit_price_discount_vat'] * x['quantity']
        )

    def save_order(self, output_path: str, order_df: pd.DataFrame) -> None:
        Exporter(Entity).write(order_df, output_path)
        st.success(f'Order exported to {output_path}')
