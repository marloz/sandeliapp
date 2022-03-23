import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import pandas as pd
from pydantic.json import pydantic_encoder

from config.formats import DATE_FORMAT, TIMESTAMP_FORMAT
from src.apps.utils import generate_id
from src.entities import Entity

NEGATIVE_QUANTITY_TYPES = ["stock refill", "return"]
VAT = 1.21


class RowStatus(Enum):
    INSERT = "I"
    UPDATE = "U"
    DELETE = "D"


class ProcessingStrategy(ABC):
    @abstractmethod
    def process(self, entity_list: List[Entity], row_status: RowStatus) -> pd.DataFrame:
        ...

    @classmethod
    def _preprocess(cls, entity_list: List[Entity], row_status: RowStatus) -> pd.DataFrame:
        return pd.concat(
            [cls._preprocess_single_entity(entity, row_status) for entity in entity_list]
        )

    @classmethod
    def _preprocess_single_entity(cls, entity: Entity, row_status: RowStatus) -> pd.DataFrame:
        entity_dict = cls._serialize_entity(entity)
        return (
            cls._entity_dict_to_df(entity_dict)
            .pipe(cls._add_timestamp)
            .pipe(cls._add_row_status, row_status=row_status)
        )

    @staticmethod
    def _serialize_entity(entity: Entity) -> Dict[str, Any]:
        return json.loads(json.dumps(entity, indent=2, default=pydantic_encoder))

    @staticmethod
    def _entity_dict_to_df(entity_dict: Dict[str, Any]) -> pd.DataFrame:
        nested_column_separator = "__"
        pattern_to_replace = f"{nested_column_separator}.*{nested_column_separator}"

        def replace_nested_suffix(x):
            return re.sub(pattern_to_replace, "", x)

        return pd.json_normalize([entity_dict], sep=nested_column_separator).rename(
            columns=lambda x: replace_nested_suffix(x)
        )

    @staticmethod
    def _add_timestamp(df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(timestamp=datetime.now().strftime(TIMESTAMP_FORMAT))

    @staticmethod
    def _add_row_status(df: pd.DataFrame, row_status: RowStatus) -> pd.DataFrame:
        return df.assign(status=row_status.value)


class DefaultProcessing(ProcessingStrategy):
    def process(self, entity_list: List[Entity], row_status: RowStatus) -> pd.DataFrame:
        return self._preprocess(entity_list=entity_list, row_status=row_status)


class OrderProcessing(ProcessingStrategy):
    def process(self, entity_list: List[Entity], row_status: RowStatus) -> pd.DataFrame:
        return (
            self._preprocess(entity_list=entity_list, row_status=row_status)
            .pipe(self.add_order_amounts)
            .pipe(self.calculate_payment_due)
            .reset_index(drop=True)
        )

    @staticmethod
    def add_order_amounts(order_df: pd.DataFrame) -> pd.DataFrame:
        if order_df["order_type"].unique()[0] in NEGATIVE_QUANTITY_TYPES:
            order_df["quantity"] = order_df["quantity"] * -1
        return order_df.assign(
            price=lambda x: x["cost"].mul(x["pricing_factor"]),
            discount_amount=lambda x: x["price"].mul(x["discount"]).div(100),
            price_with_vat=lambda x: x["price"] * VAT,
            price_with_discount=lambda x: x["price"].sub(x["discount_amount"]),
            price_with_discount_vat=lambda x: x["price_with_discount"] * VAT,
            sum=lambda x: x["price_with_discount"] * x["quantity"],
            sum_vat=lambda x: x["price_with_discount_vat"] * x["quantity"],
        )

    @staticmethod
    def calculate_payment_due(order_df: pd.DataFrame) -> pd.DataFrame:
        return order_df.assign(
            payment_due=lambda x: (
                pd.to_datetime(x["order_date"]) + pd.to_timedelta(x["payment_terms"], unit="D")
            ).dt.strftime(DATE_FORMAT)
        )
