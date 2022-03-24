from abc import ABC
from dataclasses import dataclass

from src.database.queries import GroupedSumQuery, LatestRowQuery, LoaderQuery, ValidDateQuery
from src.processing import DefaultProcessing, OrderProcessing, ProcessingStrategy

NON_ARGUMENT_ATTRS = ["__initialised__", "query", "processing"]


@dataclass
class BaseTable(ABC):

    query: LoaderQuery
    processing: ProcessingStrategy


@dataclass
class CustomerTable(BaseTable):
    query: LoaderQuery = LatestRowQuery(table_name="customer", id_column="customer_id")
    processing: ProcessingStrategy = DefaultProcessing()


@dataclass
class ManagerTable(BaseTable):
    query: LoaderQuery = LatestRowQuery(table_name="manager", id_column="manager_id")
    processing: ProcessingStrategy = DefaultProcessing()


@dataclass
class ProductTable(BaseTable):
    query: LoaderQuery = LatestRowQuery(table_name="product", id_column="product_id")
    processing: ProcessingStrategy = DefaultProcessing()


@dataclass
class InventoryTable(BaseTable):
    query: LoaderQuery = GroupedSumQuery(
        table_name="inventory",
        id_column="order_id",
        input_table="orders",
        groupby_columns=["product_name"],
        column_to_sum="quantity",
    )
    processing: ProcessingStrategy = DefaultProcessing()


@dataclass
class OrdersTable(BaseTable):
    query: LoaderQuery = LatestRowQuery(table_name="orders", id_column="order_id")
    processing: ProcessingStrategy = OrderProcessing()


@dataclass
class DiscountTable(BaseTable):
    query: LoaderQuery = ValidDateQuery(
        table_name="discount",
        id_column="discount_id",
        start_date_column="start_date",
        end_date_column="end_date",
    )
    processing: ProcessingStrategy = DefaultProcessing()
