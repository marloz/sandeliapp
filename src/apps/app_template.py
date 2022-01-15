from abc import abstractmethod
from .utils import get_entity_from_selectbox, generate_id, get_entity_identifier_column
from src.database.loader import Loader
from src.database.tables import BaseTable
from src.database.exporter import Exporter
from src.entities import Entity
from src.config import COLUMN_NAME_SEPARATOR, ID_SUFFIX
from src import processing

from hydralit import HydraHeadApp
import streamlit as st
import pandas as pd

from typing import Union, Type


class AppTemplate(HydraHeadApp):

    def __init__(self, entity_type: Type[Entity],
                 dataloader: Loader) -> None:
        self.entity_type = entity_type
        self.entity_type_name = entity_type.name()
        self.dataloader = dataloader
        self.output_table = self.dataloader.table_info[self.entity_type_name]
        self.entity_processor: processing.ProcessingStrategy = self._get_entity_processor()

    def _get_entity_processor(self) -> processing.ProcessingStrategy:
        return getattr(processing, self.output_table.processing)

    @abstractmethod
    def run(self) -> None:
        ...

    def select_entity_to_edit(self) -> Union[Entity, None]:
        entity_identifier_column = get_entity_identifier_column(
            self.entity_type, 'name')
        st.write(f'Edit existing {self.entity_type_name} details')
        return get_entity_from_selectbox(
            entity_type=self.entity_type,
            df=self.dataloader.data[self.entity_type_name],
            entity_identifier_column=entity_identifier_column)

    def fill_in_entity_details(self) -> Union[Entity, None]:
        st.write(f'Fill in new {self.entity_type_name} details')

        def _generate_caption(attribute_name: str) -> str:
            return attribute_name.replace(COLUMN_NAME_SEPARATOR, ' ').capitalize()

        def _get_value(attribute_name: str, attribute_type: type) -> str:
            if attribute_name in ID_SUFFIX:
                return generate_id()
            elif self.entity_to_edit:
                return self.entity_to_edit.__dict__[attribute_name]
            else:
                return attribute_type()

        entity_info_dict = {
            attribute_name: st.text_input(_generate_caption(attribute_name),
                                          value=_get_value(attribute_name, attribute_type))
            for attribute_name, attribute_type in self.entity_type.schema().items()
        }
        return self.entity_type(**entity_info_dict)

    @ staticmethod
    def save_entity_df(entity_df: pd.DataFrame, output_table: BaseTable) -> None:
        Exporter().append_df_to_database(entity_df, output_table)
        st.success(f'Exported to {output_table.table_name} table')
