from ..utils import get_entity_identifier_column
from src.database.loader import Loader
from src.entities import Customer, Discount, Orders, Product

import streamlit as st


class ProductInfo:

    def __init__(self, dataloader: Loader):
        self.dataloader = dataloader

    def show(self, product: Product, customer: Customer):
        self.check_inventory(product)
        self.calculate_price_for_customer(product, customer)
        self.show_active_discount(product)

    def check_inventory(self, product: Product) -> None:
        quantity_left = self.dataloader.data[Orders.name()] \
            .set_index(get_entity_identifier_column(Product, 'name')) \
            .loc[product.product_name].values[0]
        st.write(f'Left in stock: {quantity_left}')

    @staticmethod
    def calculate_price_for_customer(product: Product, customer: Customer):
        price = round(product.cost * customer.pricing_factor, 2)
        st.write(f'Price for customer before discount/VAT: {price}')

    def show_active_discount(self, product: Product) -> None:
        discount_df = self.dataloader.data[Discount.name()]

        def discount_condition(x):
            return (x['discount_identifier'] == product.product_name) \
                | (x['discount_identifier'] == product.product_category) \
                | (x['discount_identifier'] == product.manufacturer)

        columns_to_show = ['discount_percent', 'start_date', 'end_date']

        active_discounts = discount_df \
            .loc[lambda x: discount_condition(x), columns_to_show]
        if active_discounts.shape[0] > 0:
            st.write('Active discounts for selected product:')
            st.write(active_discounts)
        else:
            st.write('No active discounts')
