from typing import List, Any, Dict
from datetime import datetime
from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder
import json
from uuid import uuid1
import pandas as pd
from ._constants import DATE_FORMAT, VAT, SEP


@dataclass
class BaseInfo:
    id: int
    name: str


@dataclass
class Manager(BaseInfo):
    location: str


@dataclass
class Customer(BaseInfo):
    ...


@dataclass
class Product(BaseInfo):
    price: float
    category: str
    manufacturer: str


@dataclass
class Order:
    manager: Manager
    customer: Customer
    type: str
    items: List[Product]
    quantities: List[int]
    discounts: List[float] = Field(default_factory=list)
    date: str = ""
    timestamp: datetime = datetime.now()
    id: str = str(uuid1())
    vat: float = VAT

    def __post_init_post_parse__(self):
        self.discounts = (
            self.discounts if self.discounts else [0.0 for _ in range(len(self.items))]
        )
        self.date = self.date if self.date else self.timestamp.strftime(DATE_FORMAT)

    def export(self, order_df: pd.DataFrame, output_table: str) -> None:
        order_df.to_csv(output_table, sep=SEP, mode="append", index=False)

    def prepare_for_export(self, product_column_map: Dict[str, str]) -> pd.DataFrame:
        order_info_df = self._create_order_info_df()
        item_df = self._create_item_df(product_column_map)
        return pd.concat([order_info_df, item_df], axis=1)

    def _create_item_df(self, product_column_map: Dict[str, str]) -> pd.DataFrame:
        return (
            pd.concat([pd.DataFrame([item.__dict__]) for item in self.items])
            .assign(quantity=self.quantities, discount=self.discounts)
            .rename(columns=product_column_map)
            # Added automatically as result of __post_init__ by pydantic
            .drop("__initialised__", axis=1)
        )

    def _create_order_info_df(self) -> pd.DataFrame:
        order_dict = self._serialize()
        info_df = pd.json_normalize([order_dict], sep="_")
        return info_df.drop(["items", "quantities", "discounts"], axis=1)

    def _serialize(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self, indent=2, default=pydantic_encoder))

