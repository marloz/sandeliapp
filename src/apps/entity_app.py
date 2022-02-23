from .app_template import AppTemplate
from src.entities import AccessLevel, Entity
from src.processing import RowStatus
from src.database.tables import BaseTable
from src.database.loader import Loader
from .utils import EntityIdentifierType

import streamlit as st
from typing import Type


class EntityApp(AppTemplate):
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

