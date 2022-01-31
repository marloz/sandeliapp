from abc import ABC
from typing import Dict
from pydantic.dataclasses import dataclass
from datetime import date
from enum import Enum


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


class AccessLevel(Enum):
    admin = 'admin'
    manager = 'manager'
    user = 'user'


class ManagerLocation(Enum):
    vilnius = 'Vilnius'
    riga = 'Riga'


@dataclass
class Manager(Entity):
    manager_id: str
    manager_name: str
    manager_location: ManagerLocation
    access: AccessLevel


class CustomerType(Enum):
    default = 'default'
    wholesale = 'whole sale'
    retail = 'retail'


class PriceFactor(Enum):
    default = 1.
    wholesale = 1.2
    retail = 1.4


class PaymetTerms(Enum):
    days_30 = 30
    days_60 = 60
    days_90 = 90
    days_120 = 120


@dataclass
class Customer(Entity):
    customer_id: str
    customer_name: str
    customer_type: CustomerType
    pricing_factor: PriceFactor
    payment_terms: PaymetTerms
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


class OrderType(Enum):
    sale = 'sale'
    consignment = 'consignment'
    consignment_sale = 'consignment sale'
    order_return = 'return'
    credit = 'credit'
    refill = 'stock refill'


@dataclass
class Orders(Entity):
    manager: Manager
    customer: Customer
    product: Product
    order_date: date
    order_type: OrderType
    quantity: int
    discount: float


class DiscountLevel(Enum):
    product_name = 'product_name'
    product_category = 'product_category'
    manufacturer = 'manufacturer'


@dataclass
class Discount(Entity):
    discount_id: str
    discount_level: DiscountLevel
    discount_identifier: str
    start_date: date
    end_date: date
    discount_percent: float
