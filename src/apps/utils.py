from src.entities import Entity
from src.io.loader import EntityDataLoader
import streamlit as st
from uuid import uuid1


def get_entity_from_selectbox(entity: Entity, dataloader: EntityDataLoader) -> str:
    entity_name = entity.__name__.lower()
    table_info = dataloader.table_info_dict[entity_name]
    entity_list = dataloader.data[entity_name][table_info.name_column] \
        .tolist()
    selected_entity = st.selectbox(f'Select {entity_name}', entity_list)
    return selected_entity


def generate_id(len: int = 10) -> str:
    return str(uuid1())[:len]
