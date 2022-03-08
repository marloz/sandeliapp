import streamlit as st
from src.database.tables import DiscountTable
from src.entities import AccessLevel, Discount
from src.processing import RowStatus

from .app_template import AppTemplate


class DiscountApp(AppTemplate):
    def run(self):

        self.download_data()

        new_entry_col, edit_entry_col = st.columns(2)

        if st.session_state.current_user_access != AccessLevel.user.value:
            with edit_entry_col:
                self.entity_to_edit = self.select_entity_to_edit(self.identifier_type)

        with new_entry_col:
            discount = self.fill_in_entity_details()
            self.check_active_discount(
                discount.discount_level.value, discount.discount_identifier
            )

        save_col, del_col = st.columns(2)

        with save_col:
            if st.button(f"Save {self.output_table.query.table_name}"):
                row_status = RowStatus.UPDATE if self.entity_to_edit else RowStatus.INSERT
                entity_df = self.output_table.processing.process(
                    entity_list=[discount], row_status=row_status
                )
                self.save_entity_df(entity_df)

        with del_col:
            if st.button(f"Delete {self.output_table.query.table_name}"):
                entity_df = self.output_table.processing.process(
                    entity_list=[discount], row_status=RowStatus.DELETE
                )
                self.save_entity_df(entity_df)

    def check_active_discount(self, discount_level: str, discount_identifier: str) -> None:
        active_discount_df = self.dataloader.data[DiscountTable().query.table_name].loc[
            lambda x: (x.discount_level == discount_level)
            & (x.discount_identifier == discount_identifier)
        ]
        if active_discount_df.shape[0] > 0:
            st.write(f"Active discount on {discount_level} {discount_identifier}")
            st.write(active_discount_df[Discount.attribute_list()])
