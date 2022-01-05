from .utils import get_entity_from_selectbox, generate_id, get_output_path, get_entity_name, save_entity
from src.io.loader import EntityDataLoader
from src.entities import Entity
from src.config import COLUMN_NAME_SEPARATOR, ID_SUFFIX
from hydralit import HydraHeadApp
import streamlit as st
from typing import Optional, Union, Type


class EntityAppTemplate(HydraHeadApp):

    def __init__(self, entity: Type[Entity],
                 dataloader: EntityDataLoader,
                 add_default: bool = True):
        self.entity = entity
        self.entity_name = get_entity_name(entity)
        self.dataloader = dataloader
        self.entity_to_edit: Optional[Entity] = None
        self.add_default = add_default

    def run(self):
        new_entity_col, edit_entity_col = st.columns(2)

        with edit_entity_col:
            st.write(f'Edit existing {self.entity_name} details')
            self.entity_to_edit = get_entity_from_selectbox(
                self.entity, self.dataloader, add_default=self.add_default)

        with new_entity_col:
            self.entity = self.fill_in_entity_details()

        output_path = get_output_path(self.entity_name)
        save_entity(self.entity, output_path)
        self.dataloader.load_data()

    def fill_in_entity_details(self) -> Union[Entity, None]:
        st.write(f'Fill in new {self.entity_name} details')

        def _gen_caption(attribute_name: str) -> str:
            return attribute_name.replace(COLUMN_NAME_SEPARATOR, ' ').capitalize()

        def _get_value(attribute_name: str, attribute_type: type) -> str:
            return self.entity_to_edit.__dict__[attribute_name] if self.entity_to_edit else attribute_type() \
                if ID_SUFFIX not in attribute_name else generate_id()

        entity_info_dict = {
            attribute_name: st.text_input(_gen_caption(attribute_name),
                                          value=_get_value(attribute_name, attribute_type))
            for attribute_name, attribute_type in self.entity.__annotations__.items()
        }
        return self.entity(**entity_info_dict)
