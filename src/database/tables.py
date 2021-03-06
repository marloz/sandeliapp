from config.formats import DATE_FORMAT

from abc import ABC
from pydantic.dataclasses import dataclass
from dataclasses import field
from typing import List, Dict, Any
from datetime import datetime, date


NON_ARGUMENT_ATTRS = ['__initialised__', 'query', 'processing']


@dataclass
class BaseTable(ABC):

    table_name: str
    query: str
    processing: str

    def argument_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if k not in NON_ARGUMENT_ATTRS}

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()


@dataclass
class CustomerTable(BaseTable):
    table_name: str = 'customer'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'
    processing: str = 'DefaultProcessing'

    def __post_init__(self):
        self.groupby_columns = ['customer_id']


@dataclass
class ManagerTable(BaseTable):
    table_name: str = 'manager'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'
    processing: str = 'DefaultProcessing'

    def __post_init__(self):
        self.groupby_columns = ['manager_id']


@dataclass
class ProductTable(BaseTable):
    table_name: str = 'product'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'
    processing: str = 'DefaultProcessing'

    def __post_init__(self):
        self.groupby_columns = ['product_id']


@dataclass
class InventoryTable(BaseTable):
    table_name: str = 'orders'
    groupby_columns: List[str] = field(default_factory=list)
    column_to_sum: str = 'quantity'
    query: str = 'GroupedSumQuery'
    processing: str = 'DefaultProcessing'

    def __post_init__(self):
        self.groupby_columns = ['product_name']


@dataclass
class OrdersTable(BaseTable):
    table_name: str = 'orders'
    groupby_columns: List[str] = field(default_factory=list)
    sort_column: str = 'timestamp'
    query: str = 'LatestRowQuery'
    processing: str = 'OrderProcessing'

    def __post_init__(self):
        self.groupby_columns = ['order_id']


@dataclass
class DiscountTable(BaseTable):
    table_name: str = 'discount'
    filter_date: date = datetime.now().date()
    start_date_column: str = 'start_date'
    end_date_column: str = 'end_date'
    date_format: str = DATE_FORMAT
    query: str = 'ValidDateQuery'
    processing: str = 'DefaultProcessing'
