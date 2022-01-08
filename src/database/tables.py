from config.formats import DATE_FORMAT

from abc import ABC
from pydantic.dataclasses import dataclass
from dataclasses import field
from typing import List
from datetime import datetime, date

NON_ARGUMENT_ATTRS = ['__initialised__', 'query']


@dataclass
class BaseTable(ABC):

    table_name: str
    query: str

    @property
    def argument_dict(self):
        return {k: v for k, v in self.__dict__.items() if k not in NON_ARGUMENT_ATTRS}


@dataclass
class Customer(BaseTable):
    table_name: str = 'customer'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'

    def __post_init__(self):
        self.groupby_columns = ['customer_id']


@dataclass
class Manager(BaseTable):
    table_name: str = 'manager'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'

    def __post_init__(self):
        self.groupby_columns = ['manager_id']


@dataclass
class Product(BaseTable):
    table_name: str = 'product'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'

    def __post_init__(self):
        self.groupby_columns = ['product_id']


@dataclass
class Orders(BaseTable):
    table_name: str = 'orders'
    groupby_columns: List[str] = field(default_factory=list)
    column_to_sum: str = 'quantity'
    query: str = 'GroupedSumQuery'

    def __post_init__(self):
        self.groupby_columns = ['product_name']


@dataclass
class Discount(BaseTable):
    table_name: str = 'discount'
    filter_date: date = datetime.now().date()
    start_date_column: str = 'start_date'
    end_date_column: str = 'end_date'
    date_format: str = DATE_FORMAT
    query: str = 'ValidDateQuery'


tables = [Manager(), Customer(), Product(), Orders(), Discount()]
