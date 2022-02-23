import streamlit as st
from src.database.tables import DiscountTable, ProductTable, BaseTable
from src.database.loader import Loader
from src.entities import Discount, DiscountLevel, Entity
from src.processing import RowStatus

from .app_template import AppTemplate
from .utils import generate_id, EntityIdentifierType

from typing import Type


class DiscountApp(AppTemplate):
    def __init__(
        self,
        entity_type: Type[Entity],
        output_table: BaseTable,
        dataloader: Loader,
        identifier_type: EntityIdentifierType,
    ):
        super().__init__(entity_type, output_table, dataloader)
        self.identifier_type = identifier_type

    def run(self):

        self.download_data()

        new_entry_col, edit_entry_col = st.columns(2)

        with edit_entry_col:
            self.entity_to_edit = self.select_entity_to_edit(self.identifier_type)

        with new_entry_col:
            discount = self.fill_in_entity_details()
            is_active = self.check_active_discount(
                discount.discount_level.value, discount.discount_identifier
            )

            if discount.discount_percent > 0 and is_active is False:
                discount_df = self.output_table.processing.process(
                    [discount], row_status=RowStatus.INSERT
                )
                if st.button(f"Save {self.output_table.query.table_name}"):
                    self.save_entity_df(discount_df)

    def check_active_discount(self, discount_level: str, discount_identifier: str) -> bool:
        active_discount_df = self.dataloader.data[DiscountTable().query.table_name].loc[
            lambda x: (x.discount_level == discount_level)
            & (x.discount_identifier == discount_identifier)
        ]
        if active_discount_df.shape[0] > 0:
            st.write(f"Active discount on {discount_level} {discount_identifier}")
            st.write(active_discount_df[Discount.attribute_list()])
            return True
        else:
            return False
