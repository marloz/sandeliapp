from abc import abstractmethod
from datetime import date, datetime
from enum import Enum, EnumMeta
from typing import Any, Optional, Type, Union

import pandas as pd
import streamlit as st
from config.formats import DATE_FORMAT
from hydralit import HydraHeadApp
from src import entities
from src.config import COLUMN_NAME_SEPARATOR, ID_SUFFIX
from src.database.exporter import Exporter
from src.database.loader import Loader
from src.database.tables import BaseTable
from src.entities import AccessLevel, Entity

from .utils import (
    EntityIdentifierType,
    generate_id,
    get_entity_from_selectbox,
    get_entity_identifier_column,
)

VALUE_TYPE_WIDGET_MAP = {
    list: st.selectbox,
    str: st.text_input,
    float: st.number_input,
    int: st.number_input,
    date: st.date_input,
}


class AppTemplate(HydraHeadApp):
    def __init__(
        self,
        entity_type: Type[Entity],
        output_table: BaseTable,
        dataloader: Loader,
        identifier_type: EntityIdentifierType,
    ) -> None:
        self.entity_type = entity_type
        self.entity_type_name = entity_type.name()
        self.dataloader = dataloader
        self.output_table = output_table
        self.identifier_type = identifier_type
        self.entity_to_edit: Optional[Entity] = None

    @abstractmethod
    def run(self) -> None:
        ...

    def select_entity_to_edit(self, identifier_type: EntityIdentifierType) -> Union[Entity, None]:
        entity_identifier_column = get_entity_identifier_column(self.entity_type, identifier_type)
        st.write(f"Edit existing {self.entity_type_name} details")
        return get_entity_from_selectbox(
            entity_type=self.entity_type,
            df=self.dataloader.data[self.output_table.query.table_name],
            entity_identifier_column=entity_identifier_column,
        )

    def fill_in_entity_details(self) -> Union[Entity, None]:
        st.write(f"Fill in new {self.entity_type_name} details")

        def _generate_caption(attribute_name: str) -> str:
            return attribute_name.replace(COLUMN_NAME_SEPARATOR, " ").capitalize()

        def _get_value(attribute_name: str, attribute_type: Union[type, EnumMeta]) -> Any:
            if self.entity_to_edit:
                value = self.entity_to_edit.__dict__[attribute_name]
                return value.value if isinstance(value, Enum) else value
            elif isinstance(attribute_type, EnumMeta):
                return [i.value for i in getattr(entities, attribute_type.__name__)]
            elif attribute_name.endswith("_date"):
                return datetime.now().date()
            else:
                return attribute_type()

        def _get_input_widget(attribute_name: str, attribute_type: type):
            caption = _generate_caption(attribute_name)
            value = _get_value(attribute_name, attribute_type)
            return VALUE_TYPE_WIDGET_MAP[type(value)](caption, value)

        entity_info_dict = {
            attribute_name: _get_input_widget(attribute_name, attribute_type)
            for attribute_name, attribute_type in self.entity_type.schema().items()
        }
        return self.entity_type(**entity_info_dict)

    def save_entity_df(self, entity_df: pd.DataFrame) -> None:
        Exporter().append_df_to_database(entity_df, self.output_table)
        st.success(f"Exported to {self.output_table.query.table_name} table")
        self.dataloader.load_single_table(self.output_table)

    def download_data(self):
        if st.session_state.current_user_access != AccessLevel.user.value:
            df = self.dataloader.data[self.output_table.query.table_name]
            data = df.to_csv(sep=";", index=False).encode("utf-8")
            output_name = COLUMN_NAME_SEPARATOR.join(
                [self.output_table.query.table_name, datetime.now().strftime(DATE_FORMAT)]
            )
            st.download_button(
                label=f"Download {self.entity_type_name} data",
                data=data,
                file_name=output_name + ".csv",
                mime="text/csv",
            )
