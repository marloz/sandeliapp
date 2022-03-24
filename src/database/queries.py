from abc import ABC, abstractmethod
from dataclasses import field
from datetime import datetime
from typing import List

from pydantic.dataclasses import dataclass
from src.config import DATE_FORMAT


@dataclass
class LoaderQuery(ABC):

    table_name: str
    id_column: str
    timestamp_column: str = field(default="timestamp", init=False)
    status_column: str = field(default="status", init=False)

    @abstractmethod
    def get_query(self) -> str:
        ...

    def _latest_row_cte(self):
        return f"""
            WITH cte AS (
                SELECT
                    tbl.*,
                    ROW_NUMBER() OVER(
                        PARTITION BY {self.id_column}
                        ORDER BY {self.timestamp_column} DESC
                    ) as row_num
                FROM
                    {self.table_name} as tbl
            )
        """


@dataclass
class LatestRowQuery(LoaderQuery):
    def get_query(self) -> str:
        return f"""
            {self._latest_row_cte()}

            SELECT
                *
            FROM
                cte
            WHERE
                row_num = 1
            AND
                {self.status_column} != 'D'
        """


@dataclass
class GroupedSumQuery(LoaderQuery):

    input_table: str
    groupby_columns: List[str]
    column_to_sum: str

    def get_query(self) -> str:
        groupby_columns = ",".join(self.groupby_columns)
        sum_column = f"sum_{self.column_to_sum}"
        latest_row_query = LatestRowQuery(
            table_name=self.input_table, id_column=self.id_column,
        ).get_query()
        return f"""
            SELECT
                {groupby_columns},
                SUM({self.column_to_sum}) as {sum_column}
            FROM ({latest_row_query}) as tbl
            GROUP BY {groupby_columns}
            ORDER BY {sum_column} DESC
    """


@dataclass
class ValidDateQuery(LoaderQuery):

    start_date_column: str
    end_date_column: str
    filter_date: str = field(default=datetime.now().date().strftime(DATE_FORMAT), init=False)

    def get_query(self) -> str:
        latest_row_query = LatestRowQuery(
            table_name=self.table_name, id_column=self.id_column,
        ).get_query()
        return f"""
            SELECT
                *
            FROM ({latest_row_query}) as tbl
            WHERE
                {self.start_date_column} <= '{self.filter_date}'
            AND {self.end_date_column} >= '{self.filter_date}'
    """
