from src.logger import Logger
from pydantic.dataclasses import dataclass
from abc import abstractmethod
from src.entities import Entity
from src.config import SEP, DATA_PATH, SORT_COLUMN, TABLE_FORMAT, ID_SUFFIX, \
    ENTITY_NAME_COLUMN_SUFFIX, COLUMN_NAME_SEPARATOR
from typing import List, Dict, Any, Optional
import os
import pandas as pd
import streamlit as st

log = Logger()


@dataclass
class TableInfo:
    alias: str
    path: str
    id_column: str
    entity_name_column: str
    sort_column: str


class BaseDataLoader:
    def __init__(self, tables: List[TableInfo]) -> None:
        self.table_info_dict = {table.alias: table for table in tables}
        self.data: Dict[str, pd.DataFrame]

    def load_data(self) -> None:
        self.data = {table.alias: (self.load_table(table.path)
                                   .pipe(self.process_table, table_info=table))
                     for table in self.table_info_dict.values()}

    def load_table(self, table_name: str) -> pd.DataFrame:
        log(f"Loading data from: {table_name}")
        return pd.read_csv(table_name, sep=SEP)

    @abstractmethod
    def process_table(self, df: pd.DataFrame, table_info: TableInfo) -> pd.DataFrame:
        log("Processing loaded table...")
        pass


class EntityDataLoader(BaseDataLoader):
    def __init__(self, tables: List[TableInfo]) -> None:
        super().__init__(tables)

    def process_table(self, df: pd.DataFrame, table_info: TableInfo) -> pd.DataFrame:
        return self.filter_latest_rows_in_df(
            df, id_column=table_info.id_column, sort_column=table_info.sort_column
        )

    @staticmethod
    def filter_latest_rows_in_df(df: pd.DataFrame,
                                 id_column: str,
                                 sort_column: str) -> pd.DataFrame:
        log(f"Filtering latest row using {id_column} sorted by {sort_column}")
        return df.loc[lambda x: (x.groupby(id_column)[sort_column]
                                 .transform(max) == x[sort_column])]

    def get_single_entity_instance(self, entity: Entity,
                                   entity_identifier: str,
                                   identifier_type: str = 'id') -> Entity:
        log(f"Fetching single {entity} data using {identifier_type}: {entity_identifier}")
        entity_name = entity.__name__.lower()
        table_info = self.table_info_dict[entity_name]
        required_columns = list(entity.__annotations__.keys())
        identifier_column = (table_info.id_column if identifier_type == 'id'
                             else table_info.entity_name_column)
        entity_df = (self.data[entity_name]
                     .loc[lambda x: x[identifier_column] == entity_identifier, required_columns])
        entity_dict = entity_df.to_dict("records")[0]
        return entity(**entity_dict)


def fill_table_info_from_alias(alias: str,
                               data_path: Optional[str] = DATA_PATH) -> Dict[str, Any]:
    return dict(
        alias=alias,
        path=os.path.join(data_path, ".".join([alias, TABLE_FORMAT])),
        id_column=COLUMN_NAME_SEPARATOR.join([alias, ID_SUFFIX]),
        entity_name_column=COLUMN_NAME_SEPARATOR.join(
            [alias, ENTITY_NAME_COLUMN_SUFFIX]),
        sort_column=SORT_COLUMN,
    )


@st.cache
def preload_data(entities_to_load: list[str],
                 data_path: Optional[str] = DATA_PATH) -> EntityDataLoader:
    entity_tables = [
        TableInfo(**fill_table_info_from_alias(entity, data_path))
        for entity in entities_to_load
    ]
    entity_data_loader = EntityDataLoader(entity_tables)
    entity_data_loader.load_data()
    return entity_data_loader
