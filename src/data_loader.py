import pandas as pd
import os
from typing import List, Dict, Any
from ._constants import SEP, DATA_PATH
from .entities import Entity
from abc import abstractmethod
from pydantic.dataclasses import dataclass
from .logger import log_msg


# Columns
SORT_COLUMN = "timestamp"
ID_SUFFIX = "id"
TABLE_FORMAT = "csv"

# Table info
def fill_table_info_from_alias(alias: str) -> Dict[str, Any]:
    return dict(
        alias=alias,
        name=os.path.join(DATA_PATH, ".".join([alias, TABLE_FORMAT])),
        id_column="_".join([alias, ID_SUFFIX]),
        sort_column=SORT_COLUMN,
    )


@dataclass
class TableInfo:
    alias: str
    name: str
    id_column: str
    sort_column: str


class BaseDataLoader:
    def __init__(self, tables: List[TableInfo]) -> None:
        self.table_info_dict = {table.alias: table for table in tables}
        self.data: Dict[str, pd.DataFrame]

    def load_data(self) -> None:
        self.data = {
            table.alias: (
                self.load_table(table.name).pipe(self.process_table, table_info=table)
            )
            for table in self.table_info_dict.values()
        }

    def load_table(self, table_name: str) -> pd.DataFrame:
        log_msg(f"Loading data from: {table_name}")
        return pd.read_csv(table_name, sep=SEP)

    @abstractmethod
    def process_table(self, df: pd.DataFrame, table_info: TableInfo) -> pd.DataFrame:
        log_msg(f"Processing loaded table...")
        pass


class EntityDataLoader(BaseDataLoader):
    def __init__(self, tables: List[TableInfo]) -> None:
        super().__init__(tables)

    def process_table(self, df: pd.DataFrame, table_info: TableInfo) -> pd.DataFrame:
        return self.filter_latest_rows_in_df(
            df, id_column=table_info.id_column, sort_column=table_info.sort_column
        )

    @staticmethod
    def filter_latest_rows_in_df(
        df: pd.DataFrame, id_column: str, sort_column: str,
    ) -> pd.DataFrame:
        log_msg(f"Filtering latest row using {id_column} sorted by {sort_column}")
        return df.loc[
            lambda x: (
                x.groupby(id_column)[sort_column].transform(max) == x[sort_column]
            )
        ]

    def get_single_entity_instance(self, entity: Entity, entity_id: int) -> Entity:
        log_msg(f"Fetching single {entity} data using id: {entity_id}")
        entity_name = entity.__name__.lower()
        entity_df = self.data[entity_name]
        table_info = self.table_info_dict[entity_name]
        required_columns = list(entity.__annotations__.keys())
        entity_df = entity_df.loc[lambda x: x[table_info.id_column] == entity_id]
        entity_dict = entity_df[required_columns].to_dict("records")[0]
        return entity(**entity_dict)

