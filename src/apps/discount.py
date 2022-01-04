from hydralit import HydraHeadApp
import streamlit as st

from src.io.loader import EntityDataLoader
from .utils import generate_id, get_entity_name, get_output_path, save_entity
from src.entities import Product, Discount

from enum import Enum, auto


class DiscountLevel(Enum):
    product_name = auto()
    product_category = auto()
    manufacturer = auto()


class DiscountApp(HydraHeadApp):

    def __init__(self, product_dataloader: EntityDataLoader):
        self.product_dataloader = product_dataloader

    def __str__(self):
        return self.__class__.__name__.replace('App', '').lower()

    def run(self):
        with st.container():
            (discount_level_col, discount_identifier_col,
             start_date_col, end_date_col, discount_percent_col) = st.columns(5)

            with discount_level_col:
                discount_levels = [level.name for level in DiscountLevel]
                discount_level = st.selectbox(
                    'Discount level', discount_levels)

            with discount_identifier_col:
                discount_identifiers = self.get_discount_identifiers(
                    discount_level)
                discount_identifier = st.selectbox(
                    'Discount identifier', discount_identifiers)

            with start_date_col:
                start_date = st.date_input('Discount start date')

            with end_date_col:
                end_date = st.date_input('Discount end date')

            with discount_percent_col:
                discount_percent = st.number_input(
                    'Discount percent', min_value=0., max_value=100.)

            discount = Discount(discount_id=generate_id(),
                                discount_level=discount_level,
                                discount_identifier=discount_identifier,
                                start_date=start_date,
                                end_date=end_date,
                                discount_percent=discount_percent)

            output_path = get_output_path(get_entity_name(discount))
            save_entity(discount, output_path=output_path)

    def get_discount_identifiers(self, discount_level: str):
        product_table_name = get_entity_name(Product)
        return set(self.product_dataloader.data[product_table_name][discount_level])
