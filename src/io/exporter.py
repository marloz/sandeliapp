from typing import Any, Dict
from pydantic.json import pydantic_encoder
import json
import pandas as pd
from datetime import datetime

from src.config import SEP, TIMESTAMP_FORMAT
from src.entities import Entity
from src.logger import Logger

log = Logger()


class Exporter:

    def __init__(self, entity: Entity) -> None:
        self.entity = entity
        self._timestamp = datetime.now()

    def export(self, output_path: str) -> None:
        log(f'Exporting {str(self.entity)} to {output_path}')
        (self._to_df()
         .pipe(self._add_timestamp)
         .to_csv(output_path, sep=SEP, mode='a', index=False))

    def _to_df(self) -> pd.DataFrame:
        return pd.json_normalize([self._serialize()], sep="_")

    def _serialize(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.entity, indent=2, default=pydantic_encoder))

    def _add_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(timestamp=self._timestamp.strftime(TIMESTAMP_FORMAT))
