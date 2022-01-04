from src.entities import Entity
from src.io.loader import EntityDataLoader
from src.io.exporter import Exporter
from src.config import DEFAULT_VALUE, DATA_PATH, TABLE_FORMAT
import streamlit as st
from uuid import uuid1
import os
from typing import Union, Type


def get_entity_name_from_selectbox(entity_name: str, dataloader: EntityDataLoader,
                                   add_default: bool = True) -> str:
    table_info = dataloader.table_info_dict[entity_name]
    entity_list = dataloader.data[entity_name][table_info.name_column] \
        .tolist()
    entity_list = [DEFAULT_VALUE] + entity_list if add_default else entity_list
    selected_entity = st.selectbox(f'Select {entity_name}', entity_list)
    return selected_entity


def get_entity_name(entity: Union[Entity, Type[Entity]]) -> str:
    entity = entity if isinstance(entity, type) else entity.__class__
    return entity.__name__.lower()


def get_entity_from_selectbox(entity: Entity, dataloader: EntityDataLoader,
                              add_default: bool = True) -> Union[Entity, None]:
    selected_entity = get_entity_name_from_selectbox(entity_name=get_entity_name(entity),
                                                     dataloader=dataloader,
                                                     add_default=add_default)
    if selected_entity != DEFAULT_VALUE:
        return dataloader.get_single_entity_instance(entity, selected_entity, identifier_type='name')
    else:
        return None


def get_output_path(entity_name: str) -> str:
    return os.path.join(DATA_PATH, '.'.join([entity_name, TABLE_FORMAT]))


def generate_id(len: int = 10) -> str:
    return str(uuid1())[:len]


def save_entity(entity: Entity, output_path: str) -> None:
    entity_name = get_entity_name(entity)
    if st.button(f'Save {entity_name}'):
        Exporter(entity).export(output_path)
        st.write(f'{entity} exported to database {output_path}')
