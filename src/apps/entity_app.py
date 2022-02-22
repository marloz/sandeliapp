from sqlite3 import Row
from .app_template import AppTemplate
from src.entities import AccessLevel
from src.processing import RowStatus

import streamlit as st


class EntityApp(AppTemplate):
    def run(self):

        self.download_data()

        new_entity_col, edit_entity_col = st.columns(2)

        if st.session_state.current_user_access != AccessLevel.user.value:
            with edit_entity_col:
                self.entity_to_edit = self.select_entity_to_edit()

        with new_entity_col:
            entity = self.fill_in_entity_details()

        row_status = RowStatus.UPDATE if self.entity_to_edit else RowStatus.INSERT
        st.write(f"These records will be exported using write mode: {row_status.name}")
        entity_df = self.output_table.processing.process(
            entity_list=[entity], row_status=row_status
        )

        if st.button(f"Save {self.output_table.query.table_name}"):
            self.save_entity_df(entity_df, output_table=self.output_table)
            self.dataloader.load_single_table(self.output_table)
