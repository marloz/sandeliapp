from typing import Type

import pandas as pd
import streamlit as st
from src.database.loader import Loader
from src.database.tables import BaseTable, DiscountTable, ProductTable
from src.entities import Discount, DiscountLevel, Entity

from .app_template import AppTemplate
from .utils import generate_id


class DiscountApp(AppTemplate):
    def __init__(self, entity_type: Type[Entity], output_table: BaseTable, dataloader: Loader):
        super().__init__(entity_type, output_table, dataloader)

    def run(self):

        self.download_data()

        with st.container():
            (
                discount_level_col,
                discount_identifier_col,
                start_date_col,
                end_date_col,
                discount_percent_col,
            ) = st.columns(5)

            with discount_level_col:
                discount_levels = [level.name for level in DiscountLevel]
                discount_level = st.selectbox("Discount level", discount_levels)

            with discount_identifier_col:
                product_df = self.dataloader.data[ProductTable.name()]
                discount_identifiers = set(product_df[discount_level])
                discount_identifier = st.selectbox("Discount identifier", discount_identifiers)
            is_active = self.check_active_discounts_on_all_levels(
                product_df, discount_level, discount_identifier
            )

            with start_date_col:
                start_date = st.date_input("Discount start date")

            with end_date_col:
                end_date = st.date_input("Discount end date")

            with discount_percent_col:
                discount_percent = st.number_input(
                    "Discount percent", min_value=0.0, max_value=100.0
                )

            discount = Discount(
                discount_id=generate_id(),
                discount_level=discount_level,
                discount_identifier=discount_identifier,
                start_date=start_date,
                end_date=end_date,
                discount_percent=discount_percent,
            )

            discount_df = self.entity_processor().process([discount])

            if discount_percent > 0 and is_active is False:
                if st.button(f"Save {self.output_table.table_name}"):
                    self.save_entity_df(discount_df, output_table=self.output_table)
                    self.dataloader.update(self.output_table)

    def check_active_discounts_on_all_levels(
        self, product_df: pd.DataFrame, discount_level: str, discount_identifier: str
    ) -> bool:
        res = []

        res.append(
            self.check_active_discount(
                discount_level=discount_level, discount_identifier=discount_identifier
            )
        )

        def discount_level_condition(x):
            return x[discount_level] == discount_identifier

        for current_level, levels_to_check in [
            (
                DiscountLevel.product_name.name,
                [DiscountLevel.product_category.name, DiscountLevel.manufacturer.name],
            ),
            (DiscountLevel.product_category.name, [DiscountLevel.manufacturer.name]),
        ]:
            if discount_level == current_level:
                for product_attribute in levels_to_check:
                    identifier = product_df.loc[discount_level_condition, product_attribute].values[
                        0
                    ]
                    res.append(
                        self.check_active_discount(
                            discount_level=product_attribute, discount_identifier=identifier
                        )
                    )

        return any(res)

    def check_active_discount(self, discount_level: str, discount_identifier: str) -> bool:
        active_discount_df = self.dataloader.data[DiscountTable.name()].loc[
            lambda x: (x["discount_level"] == discount_level)
            & (x["discount_identifier"] == discount_identifier)
        ]
        if active_discount_df.shape[0] > 0:
            st.write(f"Active discount on {discount_level} {discount_identifier}")
            st.write(active_discount_df[Discount.attribute_list()])
            return True
        else:
            return False
