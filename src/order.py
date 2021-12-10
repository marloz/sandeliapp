from typing import Any, Dict, Optional
from numpy import log
from pydantic.json import pydantic_encoder
import json
import pandas as pd
from ._constants import SEP
from .entities import Order
from .log import log_msg


class OrderProcessor:
    def __init__(self, order: Order, order_date: Optional[str] = None) -> None:
        self.order = order
        self.order_date = order_date if order_date else order.order_date
        self._initialize_discounts()
        log_msg(self.order)

    def _initialize_discounts(self):
        if len(self.order.discounts) == 0:
            log_msg("Discount not set, initializing to zero")
            self.order.discounts = [0.0 for _ in range(len(self.order.items))]

    def export(self, output_table: str) -> None:
        order_df = self.prepare_for_export()
        log_msg(f"Writing preprared order to {output_table}")
        order_df.to_csv(output_table, sep=SEP, mode="a", index=False)

    def prepare_for_export(self) -> pd.DataFrame:
        log_msg("Concatenating order and item info")
        return pd.concat([self._create_order_info_df(), self._create_item_df()], axis=1)

    def _create_order_info_df(self) -> pd.DataFrame:
        log_msg("Creating order info")
        info_df = pd.json_normalize([self._serialize()], sep="_")
        return info_df.drop(["items", "quantities", "discounts"], axis=1)

    def _serialize(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.order, indent=2, default=pydantic_encoder))

    def _create_item_df(self) -> pd.DataFrame:
        log_msg("Creating item info")
        return (
            pd.concat([pd.DataFrame([item.__dict__]) for item in self.order.items])
            # Result of pydantic dataclass post init
            .drop("__initialised__", axis=1).assign(
                quantity=self.order.quantities, discount=self.order.discounts
            )
        )
