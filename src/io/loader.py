from src.logger import Logger
from pydantic.dataclasses import dataclass
from dataclasses import field
from src.entities import Entity
from src.config import DATE_FORMAT, SEP, DATA_PATH, SORT_COLUMN, TABLE_FORMAT, ID_SUFFIX, \
    ENTITY_NAME_COLUMN_SUFFIX, COLUMN_NAME_SEPARATOR
from typing import List, Dict, Any, Optional
import os
import pandas as pd
import streamlit as st
from typing import Union
from datetime import date

log = Logger()


@dataclass
class TableInfo:
    alias: str
    path: str
    id_column: str
    sort_column: str
    name_column: str
    table_columns: List[str] = field(init=False)

    def __post_init__(self):
        self.table_columns = pd.read_csv(
            self.path, sep=SEP, nrows=0).columns.tolist()


@dataclass
class CountTable(TableInfo):
    groupby: str
    aggregation_dict: Dict[str, str]


class BaseDataLoader:
    def __init__(self, tables: List[TableInfo]) -> None:
        self.table_info_dict = {table.alias: table for table in tables}
        self.data: Dict[str, pd.DataFrame]

    def load_data(self) -> None:
        self.data = {table.alias: (self.load_table(table.path)
                                   .pipe(self.process_table, table_info=table))
                     for table in self.table_info_dict.values()}

    @staticmethod
    def load_table(table_name: str) -> pd.DataFrame:
        log(f"Loading data from: {table_name}")
        return pd.read_csv(table_name, sep=SEP)


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
                                   identifier_type: str = 'id') -> Union[Entity, None]:
        log(f"Fetching single {entity} data using {identifier_type}: {entity_identifier}")
        entity_name = entity.__name__.lower()
        table_info = self.table_info_dict[entity_name]
        required_columns = list(entity.__annotations__.keys())
        identifier_column = (table_info.id_column if identifier_type == 'id'
                             else table_info.name_column)
        entity_df = (self.data[entity_name]
                     .loc[lambda x: x[identifier_column] == entity_identifier, required_columns])
        entity_dict = entity_df.to_dict("records")[0]
        return entity(**entity_dict)


class CountDataLoader(BaseDataLoader):
    def __init__(self, tables: List[CountTable]) -> None:
        super().__init__(tables)

    def process_table(self, df: pd.DataFrame, table_info: CountTable) -> pd.DataFrame:
        log(f'Counting {table_info.groupby} values')
        return df.groupby(table_info.groupby).agg(table_info.aggregation_dict)


def fill_table_info_from_alias(alias: str,
                               data_path: Optional[str] = DATA_PATH,
                               **optional_kwargs) -> Dict[str, Any]:
    table_info = dict(
        alias=alias,
        path=os.path.join(data_path, ".".join([alias, TABLE_FORMAT])),
        id_column=COLUMN_NAME_SEPARATOR.join([alias, ID_SUFFIX]),
        name_column=COLUMN_NAME_SEPARATOR.join(
            [alias, ENTITY_NAME_COLUMN_SUFFIX]),
        sort_column=SORT_COLUMN,
    )
    table_info.update(**optional_kwargs)
    return table_info


@st.cache(allow_output_mutation=True)
def preload_data(datasources: List[str]
                 ) -> EntityDataLoader:
    tables = [TableInfo(**fill_table_info_from_alias(table))
              for table in datasources]
    data_loader = EntityDataLoader(tables)
    data_loader.load_data()
    return data_loader


START_DATE_COLUMN, END_DATE_COLUMN = 'start_date', 'end_date'


@dataclass
class DiscountTable(TableInfo):
    filter_date: date
    start_date_column: str = START_DATE_COLUMN
    end_date_column: str = END_DATE_COLUMN


class DiscountDataLoader(BaseDataLoader):
    def __init__(self, tables: List[DiscountTable]) -> None:
        super().__init__(tables)

    def process_table(self, df: pd.DataFrame, table_info: DiscountTable) -> pd.DataFrame:
        filter_date = table_info.filter_date.strftime(DATE_FORMAT)
        log(f'Loading active discounts on date: {filter_date}')
        return df.loc[lambda x: (x[table_info.start_date_column] <= filter_date)
                      & (x[table_info.end_date_column] >= filter_date)]
