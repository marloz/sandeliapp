from src.database.tables import BaseTable
from .app_template import AppTemplate
from src.database.loader import Loader
from src.entities import Entity, AccessLevel

import streamlit as st

from typing import Optional, Type


class EntityApp(AppTemplate):
    def __init__(self, entity_type: Type[Entity], output_table: BaseTable, dataloader: Loader):
        super().__init__(entity_type, output_table, dataloader)
        self.entity_to_edit: Optional[Entity] = None

    def run(self):

        self.download_data()

        new_entity_col, edit_entity_col = st.columns(2)

        if st.session_state.current_user_access != AccessLevel.user.value:
            with edit_entity_col:
                self.entity_to_edit = self.select_entity_to_edit()

        with new_entity_col:
            entity = self.fill_in_entity_details()

        entity_df = self.entity_processor().process([entity])

        if st.button(f"Save {self.output_table.table_name}"):
            self.save_entity_df(entity_df, output_table=self.output_table)
            self.dataloader.update(self.output_table)
