import pandas as pd
from typing import List, Dict
from ._constants import SEP
from abc import abstractmethod
from pydantic.dataclasses import dataclass


@dataclass
class TableInfo:
    alias: str
    name: str
    id_column: str
    sort_column: str
    column_mapping: Dict[str, str]


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
        return pd.read_csv(table_name, sep=SEP)

    @abstractmethod
    def process_table(self, df: pd.DataFrame, table_info: TableInfo) -> pd.DataFrame:
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
        return df.loc[
            lambda x: (
                x.groupby(id_column)[sort_column].transform(max) == x[sort_column]
            )
        ]

    def get_single_entity_info_dict(
        self, table_alias: str, entity_id: int
    ) -> pd.DataFrame:
        entity_df = self.data[table_alias]
        table_info = self.table_info_dict[table_alias]
        return (
            entity_df.loc[lambda x: x[table_info.id_column] == entity_id]
            .rename(columns=table_info.column_mapping)[
                list(table_info.column_mapping.values())
            ]
            .to_dict("records")[0]
        )

