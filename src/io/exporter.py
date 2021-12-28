from typing import Any, Dict
from pydantic.json import pydantic_encoder
import json
import pandas as pd
import re
from datetime import datetime
from abc import ABC, abstractmethod

from src.config import SEP, TIMESTAMP_FORMAT
from src.entities import Entity
from src.logger import Logger

log = Logger()


class BaseWriter(ABC):

    @abstractmethod
    def write(self, df: pd.DataFrame, output_path: str):
        ...


class CsvWriter(BaseWriter):

    def write(self, df: pd.DataFrame, output_path: str):
        df.to_csv(output_path, sep=SEP, mode='a', index=False, header=False)


class Exporter:

    def __init__(self, entity: Entity) -> None:
        self.entity = entity
        self._timestamp: datetime = datetime.now()
        self.writer: BaseWriter = CsvWriter()

    def export(self, output_path: str) -> None:
        log(f'Exporting {str(self.entity)} to {output_path}')
        df = self.prepare_for_export()
        self.write(df, output_path)

    def prepare_for_export(self) -> pd.DataFrame:
        return (self._to_df(self._serialize(self.entity))
                .pipe(self._add_timestamp))

    @staticmethod
    def _serialize(entity: Entity) -> Dict[str, Any]:
        return json.loads(json.dumps(entity, indent=2, default=pydantic_encoder))

    @staticmethod
    def _to_df(entity_dict: Dict[str, Any]) -> pd.DataFrame:
        nested_column_separator = '__'
        pattern_to_replace = f'{nested_column_separator}.*{nested_column_separator}'
        def replace_nested_suffix(x): return re.sub(pattern_to_replace, '', x)
        return pd.json_normalize([entity_dict], sep=nested_column_separator) \
            .rename(columns=lambda x: replace_nested_suffix(x))

    def _add_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(timestamp=self._timestamp.strftime(TIMESTAMP_FORMAT))

    def write(self, df: pd.DataFrame, output_path: str) -> None:
        self.writer.write(df, output_path)
