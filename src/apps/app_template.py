from .utils import get_entity_from_selectbox, generate_id, get_entity_identifier_column
from src.database.loader import Loader
from src.database.tables import BaseTable
from src.database.exporter import Exporter
from src import entities
from src.entities import Entity
from src.config import COLUMN_NAME_SEPARATOR, ID_SUFFIX
from src import processing

from hydralit import HydraHeadApp
import streamlit as st
import pandas as pd

from typing import Union, Type, Any
from enum import EnumMeta, Enum
from abc import abstractmethod

VALUE_TYPE_WIDGET_MAP = {
    list: st.selectbox,
    str: st.text_input,
    float: st.number_input
}


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

        def _get_value(attribute_name: str, attribute_type: Union[type, EnumMeta]) -> Any:
            if self.entity_to_edit:
                value = self.entity_to_edit.__dict__[attribute_name]
                return value.value if isinstance(value, Enum) else value
            elif ID_SUFFIX in attribute_name:
                return generate_id()
            else:
                return [i.value for i in getattr(entities, attribute_type.__name__)] \
                    if isinstance(attribute_type, EnumMeta) else attribute_type()

        def _get_input_widget(attribute_name: str, attribute_type: type):
            caption = _generate_caption(attribute_name)
            value = _get_value(attribute_name, attribute_type)
            return VALUE_TYPE_WIDGET_MAP[type(value)](caption, value)

        entity_info_dict = {
            attribute_name: _get_input_widget(attribute_name, attribute_type)
            for attribute_name, attribute_type in self.entity_type.schema().items()
        }
        return self.entity_type(**entity_info_dict)

    @ staticmethod
    def save_entity_df(entity_df: pd.DataFrame, output_table: BaseTable) -> None:
        Exporter().append_df_to_database(entity_df, output_table)
        st.success(f'Exported to {output_table.table_name} table')
