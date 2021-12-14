from typing import Any, Dict, Optional, List
from pydantic.json import pydantic_encoder
from dataclasses import dataclass
from pydantic import Field
import json
import pandas as pd
from datetime import datetime
from uuid import uuid1

from src.config import SEP, DATE_FORMAT, TIMESTAMP_FORMAT, VAT
from src.entities import Manager, Customer, Product
from src.logger import Logger

log = Logger()


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


class OrderProcessor:
    def __init__(self, order: Order) -> None:
        self.order = order
        log(str(self.order))

    def export(self, output_table: str) -> None:
        order_df = self.prepare_for_export()
        log(f"Writing preprared order to {output_table}")
        order_df.to_csv(output_table, sep=SEP, mode="a", index=False)

    def prepare_for_export(self) -> pd.DataFrame:
        log("Concatenating order and item info")
        return pd.concat([self._create_order_info_df(), self._create_item_df()], axis=1)

    def _create_order_info_df(self) -> pd.DataFrame:
        log("Creating order info")
        info_df = pd.json_normalize([self._serialize()], sep="_")
        return info_df.drop(["items", "quantities", "discounts"], axis=1)

    def _serialize(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.order, indent=2, default=pydantic_encoder))

    def _create_item_df(self) -> pd.DataFrame:
        log("Creating item info")
        return (
            pd.concat([pd.DataFrame([item.__dict__])
                      for item in self.order.items])
            # Result of pydantic dataclass post init
            .drop("__initialised__", axis=1)
            .assign(quantity=self.order.quantities, discount=self.order.discounts)
        )
