from pydantic.dataclasses import dataclass
from datetime import datetime, date


@dataclass
class Entity:
    ...


@dataclass
class Manager(Entity):
    manager_id: str
    manager_name: str
    location: str


@dataclass
class Customer(Entity):
    customer_id: str
    customer_name: str


@dataclass
class Product(Entity):
    product_id: str
    product_name: str
    unit_price: float
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
