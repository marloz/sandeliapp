from typing import Type, Union
from uuid import uuid1

import pandas as pd
import streamlit as st
from src.config import COLUMN_NAME_SEPARATOR
from src.entities import Entity


def get_value_from_selectbox(values: pd.Series, default_value: str) -> str:
    value_list = [default_value] + values.tolist()
    selected_value = st.selectbox(f"Select {values.name}", value_list)
    return selected_value


def get_entity_from_df(
    entity_type: Type[Entity],
    df: pd.DataFrame,
    entity_identifier_column: str,
    entity_identifier: str,
) -> Entity:
    required_columns = entity_type.attribute_list()
    entity_df = df.loc[
        lambda x: x[entity_identifier_column] == entity_identifier, required_columns
    ]
    entity_dict = entity_df.to_dict("records")[0]
    return entity_type(**entity_dict)


def get_entity_from_selectbox(
    entity_type: Type[Entity],
    df: pd.DataFrame,
    entity_identifier_column: str,
    default_value: str = "",
) -> Union[Entity, None]:
    values = df[entity_identifier_column]
    entity_identifier = get_value_from_selectbox(
        values=values, default_value=default_value
    )
    if entity_identifier != default_value:
        return get_entity_from_df(
            entity_type=entity_type,
            df=df,
            entity_identifier_column=entity_identifier_column,
            entity_identifier=entity_identifier,
        )
    else:
        return None


def generate_id(len: int = 10) -> str:
    return str(uuid1())[:len]


def get_entity_identifier_column(
    entity_type: Type[Entity], identifier_type: str
) -> str:
    return COLUMN_NAME_SEPARATOR.join([entity_type.name(), identifier_type])
