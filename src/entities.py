from pydantic.dataclasses import dataclass


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
    price: float
    product_category: str
    manufacturer: str
