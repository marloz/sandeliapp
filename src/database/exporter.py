from src.database.executor import SqlExecutor
from src.database.tables import BaseTable

import pandas as pd


class Exporter:

    def __init__(self):
        self.executor: SqlExecutor = SqlExecutor()

    def append_df_to_database(self, df: pd.DataFrame, table: BaseTable) -> None:
        with self.executor as executor:
            df[table.get_table_columns()] \
                .to_sql(name=table.table_name, con=executor.connection,
                        index=False, if_exists='append')
