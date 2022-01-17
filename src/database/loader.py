from collections import defaultdict
from .executor import SqlExecutor
from src.database import queries
from .tables import BaseTable

import streamlit as st
import pandas as pd
from typing import List, Dict


class Loader:

    def __init__(self):
        self.executor: SqlExecutor = SqlExecutor()
        self.table_info: Dict[str, BaseTable] = defaultdict()
        self.data: Dict[str, pd.DataFrame] = defaultdict()

    def load_table_from_query(self, query: queries.LoaderQuery) -> pd.DataFrame:
        with self.executor as executor:
            return pd.read_sql(query.get_query(), con=executor.connection)

    def load_table_from_info(self, table: BaseTable) -> pd.DataFrame:
        query = getattr(queries, table.query)(**table.argument_dict())
        return self.load_table_from_query(query)

    def load_data_dict(self, tables: List[BaseTable]) -> None:
        for table in tables:
            self.table_info[table.name()] = table
            self.data[table.name()] = self.load_table_from_info(table)

    def update(self, table: BaseTable) -> None:
        self.table_info[table.name()] = table
        self.data[table.name()] = self.load_table_from_info(table)


@st.cache(allow_output_mutation=True)
def preload_data(tables: List[BaseTable]) -> Loader:
    loader = Loader()
    loader.load_data_dict(tables=tables)
    return loader
