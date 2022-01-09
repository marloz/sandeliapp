from abc import ABC
from typing import Dict
from pydantic.dataclasses import dataclass
from datetime import date


@dataclass
class Entity(ABC):

    @classmethod
    def attribute_list(cls) -> list[str]:
        return list(cls.__annotations__.keys())

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def schema(cls) -> Dict[str, type]:
        return dict(cls.__annotations__)


@dataclass
class Foo(Entity):

    some_id: str


@dataclass
class Manager(Entity):
    manager_id: str
    manager_name: str
    manager_location: str
    access: str


@dataclass
class Customer(Entity):
    customer_id: str
    customer_name: str
    customer_type: str
    pricing_factor: float
    address: str
    post_code: str
    customer_location: str
    email: str
    telephone: str
    customer_code: str
    vat_code: str


@dataclass
class Product(Entity):
    product_id: str
    product_name: str
    cost: float
    product_category: str
    manufacturer: str


@dataclass
class OrderRow(Entity):
    manager: Manager
    customer: Customer
    product: Product
    order_date: date
    order_type: str
    quantity: int
    discount: float


@dataclass
class Discount(Entity):
    discount_id: str
    discount_level: str
    discount_identifier: str
    start_date: date
    end_date: date
    discount_percent: float
