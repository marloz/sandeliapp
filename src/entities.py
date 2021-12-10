from typing import List
from datetime import datetime
from pydantic import Field
from pydantic.dataclasses import dataclass
from uuid import uuid1
from ._constants import DATE_FORMAT, TIMESTAMP_FORMAT

VAT = 0.21


@dataclass
class Entity:
    ...


@dataclass
class Manager(Entity):
    manager_id: int
    manager_name: str
    location: str


@dataclass
class Customer(Entity):
    customer_id: int
    customer_name: str


@dataclass
class Product(Entity):
    product_id: int
    product_name: str
    price: float
    product_category: str
    manufacturer: str


@dataclass
class Order:
    manager: Manager
    customer: Customer
    order_type: str
    items: List[Product]
    quantities: List[int]
    discounts: List[float] = Field(default_factory=list)
    order_date: str = datetime.now().strftime(DATE_FORMAT)
    timestamp: str = datetime.now().strftime(TIMESTAMP_FORMAT)
    order_id: str = str(uuid1())
    vat: float = VAT
