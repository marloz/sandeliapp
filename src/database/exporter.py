from src.database.executor import SqlExecutor
from src.database.tables import BaseTable

import pandas as pd
from typing import List


class Exporter:

    def __init__(self):
        self.executor: SqlExecutor = SqlExecutor()

    def append_df_to_database(self, df: pd.DataFrame, table: BaseTable) -> None:
        with self.executor as executor:
            columns_to_select = self.get_table_columns(table, executor)
            df[columns_to_select] \
                .to_sql(name=table.table_name, con=executor.connection,
                        index=False, if_exists='append')

    def get_table_columns(self, table: BaseTable, executor: SqlExecutor) -> List[str]:
        sql = f"""SELECT * FROM {table.table_name} LIMIT 1"""
        return pd.read_sql(sql, con=executor.connection).columns.tolist()
