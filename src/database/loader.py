from .executor import SqlExecutor
from src.database import queries
from .tables import BaseTable

import pandas as pd
from typing import List, Dict


class Loader:

    def __init__(self, query: queries.LoaderQuery):
        self.query = query.get_query()
        self.executor: SqlExecutor = SqlExecutor()

    def load_table(self) -> pd.DataFrame:
        with self.executor as executor:
            return pd.read_sql(self.query, con=executor.connection)


def load_table_from_info(table: BaseTable) -> pd.DataFrame:
    query = getattr(queries, table.query)(**table.argument_dict)
    return Loader(query).load_table()


def load_table_dict(tables: List[BaseTable]) -> Dict[str, pd.DataFrame]:
    return {table.table_name: load_table_from_info(table) for table in tables}
