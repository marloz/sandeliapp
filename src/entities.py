from pydantic.dataclasses import dataclass
from datetime import date


@dataclass
class Entity:
    ...


@dataclass
class Manager(Entity):
    manager_id: str
    manager_name: str
    manager_location: str


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
