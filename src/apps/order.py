from .utils import get_entity_from_selectbox, generate_id, get_entity_name, get_output_path
from src.entities import Customer, Discount, Manager, Product, OrderRow, Entity
from src.io.loader import CountDataLoader, CountTable, DiscountDataLoader, DiscountTable, EntityDataLoader, fill_table_info_from_alias
from src.io.exporter import Exporter
from src.config import ORDER_TYPES, VAT

import streamlit as st
from hydralit import HydraHeadApp
import pandas as pd
from datetime import date
from typing import Tuple, List, Optional

st.session_state['order_rows'] = []

ORDER_SUMMARY_COLUMNS = [
    'product_name',
    'quantity',
    'price',
    'discount',
    'price_with_discount',
    'sum',
    'sum_vat'
]
MANAGER_ID = 'some_email@medexy.lt'
NEGATIVE_QUANTITY_TYPES = ['stock refill', 'return']
OUTPUT_NAME = 'order'
GROUPBY_INVENTORY = 'product_name'
INVENTORY_AGGREGATION_DICT = {'quantity': 'sum'}


class OrderApp(HydraHeadApp):

    def __init__(self, dataloader: EntityDataLoader) -> None:
        self.dataloader = dataloader

    def run(self):

        # TODO: include these in a single dataloader
        self.order_dataloader = self.load_orders()

        manager = self.dataloader.get_single_entity_instance(
            entity=Manager, entity_identifier=MANAGER_ID
        )
        st.write(manager)

        order_date, order_type, customer = self.select_fixed_order_variables()
        product, selected_quantity, entered_discount = self.get_item_details(
            customer)

        if product is not None and customer is not None:
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
            OUTPUT_NAME,
            groupby=GROUPBY_INVENTORY,
            aggregation_dict=INVENTORY_AGGREGATION_DICT)
        self.order_table_info = CountTable(**table_info)
        loader = CountDataLoader([self.order_table_info])
        loader.load_data()
        return loader

    def load_discounts(self, order_date: date) -> DiscountDataLoader:
        entity_name = get_entity_name(Discount)
        discount_table_dict = fill_table_info_from_alias(
            entity_name, filter_date=order_date)
        self.discount_table_info = DiscountTable(**discount_table_dict)
        loader = DiscountDataLoader([self.discount_table_info])
        loader.load_data()
        return loader

    def select_fixed_order_variables(self) -> Tuple[date, str, str]:
        with st.container():
            date_col, type_col, customer_col = st.columns([1, 1, 4])

            with date_col:
                order_date = st.date_input('Order date')
                self.discount_dataloader = self.load_discounts(order_date)

            with type_col:
                order_type = st.selectbox('Order type', ORDER_TYPES)

            with customer_col:
                customer = get_entity_from_selectbox(
                    Customer, self.dataloader, add_default=False)

        return order_date, order_type, customer

    def get_item_details(self, customer: Customer) -> Tuple[Product, int, float]:
        with st.container():
            product_col, quantity_col, discount_col = st.columns([4, 1, 1])

            with product_col:
                product = get_entity_from_selectbox(Product, self.dataloader)
                if product:
                    self.check_inventory(product.product_name)
                    self.calculate_price_for_customer(product, customer)
                    self.show_active_discount(product)

            with quantity_col:
                selected_quantity = st.number_input(
                    'Enter quantity', min_value=1)

            with discount_col:
                entered_discount = st.number_input('Enter discount %', min_value=0.,
                                                   max_value=100., step=10.)

        return product, selected_quantity, entered_discount

    def check_inventory(self, selected_product: str) -> None:
        quantity_left = self.order_dataloader.data[OUTPUT_NAME].loc[selected_product].values[0]
        st.write(f'Left in stock: {quantity_left}')

    @staticmethod
    def calculate_price_for_customer(product: Product, customer: Customer):
        price = round(product.cost * customer.pricing_factor, 2)
        st.write(f'Price for customer before discount/VAT: {price}')

    def show_active_discount(self, product: Product) -> None:
        discount_df = self.discount_dataloader.data[get_entity_name(Discount)]

        def discount_condition(x):
            return (x['discount_identifier'] == product.product_name) \
                | (x['discount_identifier'] == product.product_category) \
                | (x['discount_identifier'] == product.manufacturer)
        columns_to_show = ['discount_identifier',
                           'discount_level',
                           'discount_percent']
        active_discounts = discount_df.loc[discount_condition, columns_to_show]
        st.write(f'Active discounts for selected product:')
        st.write(active_discounts)

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
                    output_path = get_output_path(OUTPUT_NAME)
                    self.save_order(output_path, order_df)
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
            .assign(order_id=generate_id())[self.order_table_info.table_columns]

    @staticmethod
    def add_order_amounts(order_df: pd.DataFrame) -> pd.DataFrame:
        if order_df['order_type'].unique()[0] in NEGATIVE_QUANTITY_TYPES:
            order_df['quantity'] = order_df['quantity'] * -1
        return order_df.assign(
            price=lambda x: x['cost'].mul(x['pricing_factor']),
            discount_amount=lambda x: x['price'].mul(x['discount']).div(100),
            price_with_vat=lambda x: x['price'] * VAT,
            price_with_discount=lambda x: x['price'].sub(x['discount_amount']),
            price_with_discount_vat=lambda x: x['price_with_discount'] * VAT,
            sum=lambda x: x['price_with_discount'] * x['quantity'],
            sum_vat=lambda x: x['price_with_discount_vat'] * x['quantity']
        )

    def save_order(self, output_path: str, order_df: pd.DataFrame) -> None:
        Exporter(Entity).write(order_df, output_path)
        st.success(f'Order exported to {output_path}')
