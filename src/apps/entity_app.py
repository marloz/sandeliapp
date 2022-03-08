import streamlit as st
from src.entities import AccessLevel
from src.processing import RowStatus

from .app_template import AppTemplate


class EntityApp(AppTemplate):
    def run(self):

        self.download_data()

        new_entity_col, edit_entity_col = st.columns(2)

        if st.session_state.current_user_access != AccessLevel.user.value:
            with edit_entity_col:
                self.entity_to_edit = self.select_entity_to_edit(self.identifier_type)

        with new_entity_col:
            entity = self.fill_in_entity_details()

        save_col, del_col = st.columns(2)

        with save_col:
            if st.button(f"Save {self.output_table.query.table_name}"):
                row_status = RowStatus.UPDATE if self.entity_to_edit else RowStatus.INSERT
                entity_df = self.output_table.processing.process(
                    entity_list=[entity], row_status=row_status
                )
                self.save_entity_df(entity_df)

        if self.entity_to_edit:
            with del_col:
                if st.button(f"Delete {self.output_table.query.table_name}"):
                    entity_df = self.output_table.processing.process(
                        entity_list=[entity], row_status=RowStatus.DELETE
                    )
                    self.save_entity_df(entity_df)

