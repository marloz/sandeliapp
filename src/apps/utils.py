from src.entities import Entity
from src.config import DEFAULT_VALUE

from uuid import uuid1
from typing import Union, Type

import streamlit as st
import pandas as pd


def get_value_from_selectbox(values: pd.Series,
                             add_default: bool = True) -> str:
    value_list = values.tolist()
    value_list = [DEFAULT_VALUE] + value_list if add_default else value_list
    selected_value = st.selectbox(f'Select {values.name}', value_list)
    return selected_value


def get_entity_from_df(entity_type: Type[Entity],
                       df: pd.DataFrame,
                       entity_identifier_column: str,
                       entity_identifier: str) -> Entity:
    required_columns = entity_type.attribute_list()
    entity_df = (df.loc[lambda x: x[entity_identifier_column] == entity_identifier,
                        required_columns])
    entity_dict = entity_df.to_dict("records")[0]
    return entity_type(**entity_dict)


def get_entity_from_selectbox(entity_type: Type[Entity],
                              df: pd.DataFrame,
                              entity_identifier_column: str,
                              add_default: bool = True) -> Union[Entity, None]:
    values = df[entity_identifier_column]
    entity_identifier = get_value_from_selectbox(values=values,
                                                 add_default=add_default)
    if entity_identifier != DEFAULT_VALUE:
        return get_entity_from_df(entity_type=entity_type,
                                  df=df,
                                  entity_identifier_column=entity_identifier_column,
                                  entity_identifier=entity_identifier)
    else:
        return None


def generate_id(len: int = 10) -> str:
    return str(uuid1())[:len]
