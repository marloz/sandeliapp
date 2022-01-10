from .app_template import AppTemplate
from .utils import generate_id
from src.database.loader import Loader
from src.database.tables import ProductTable
from src.entities import Entity, Discount

import streamlit as st

from enum import Enum, auto
from typing import Type


class DiscountLevel(Enum):
    product_name = auto()
    product_category = auto()
    manufacturer = auto()


class DiscountApp(AppTemplate):

    def __init__(self, entity_type: Type[Entity],
                 dataloader: Loader):
        super().__init__(entity_type, dataloader)
        self.product_dataloader = dataloader

    def run(self):
        with st.container():
            (discount_level_col, discount_identifier_col,
             start_date_col, end_date_col, discount_percent_col) = st.columns(5)

            with discount_level_col:
                discount_levels = [level.name for level in DiscountLevel]
                discount_level = st.selectbox(
                    'Discount level', discount_levels)

            with discount_identifier_col:
                product_df = self.product_dataloader.data[ProductTable.table_name]
                discount_identifiers = set(product_df[discount_level])
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

            discount_df = self.entity_processor().process([discount])

            if st.button(f'Save {self.output_table.table_name}'):
                self.save_entity_df(
                    discount_df, output_table=self.output_table)
                self.dataloader.update(self.output_table)
