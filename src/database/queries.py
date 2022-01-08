from abc import ABC, abstractmethod
from datetime import date
from pydantic.dataclasses import dataclass
from typing import List

from src.config import DATE_FORMAT


@dataclass
class LoaderQuery(ABC):

    table_name: str

    @abstractmethod
    def get_query(self) -> str:
        ...


@dataclass
class LatestRowQuery(LoaderQuery):

    groupby_columns: List[str]
    sort_column: str

    def get_query(self) -> str:
        return f"""
            WITH cte AS (
                SELECT
                    tbl.*,
                    ROW_NUMBER() OVER(
                        PARTITION BY {','.join(self.groupby_columns)}
                        ORDER BY {self.sort_column} DESC
                    ) as row_num
                FROM
                    {self.table_name} as tbl
            )

            SELECT
                *
            FROM
                cte
            WHERE
                row_num = 1
        """


@dataclass
class GroupedSumQuery(LoaderQuery):

    groupby_columns: List[str]
    column_to_sum: str

    def get_query(self) -> str:
        groupby_columns = ','.join(self.groupby_columns)
        sum_column = f'sum_{self.column_to_sum}'
        return f"""
            SELECT
                {groupby_columns},
                SUM({self.column_to_sum}) as {sum_column}
            FROM {self.table_name}
            GROUP BY {groupby_columns}
            ORDER BY {sum_column} DESC
    """


@dataclass
class ValidDateQuery(LoaderQuery):

    filter_date: date
    start_date_column: str
    end_date_column: str
    date_format: str = DATE_FORMAT

    def __post_init__(self):
        self.filter_date = self.filter_date.strftime(self.date_format)

    def get_query(self) -> str:
        return f"""
            SELECT
                *
            FROM {self.table_name}
            WHERE
                {self.start_date_column} <= '{self.filter_date}'
                AND {self.end_date_column} >= '{self.filter_date}'
    """
