import os
from typing import Dict, Any

DATE_FORMAT: str = "%Y-%m-%d"  # Default date format
TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S.%f'  # Default timestamp format
VAT: float = 0.21  # VAT tax applied in Order
SEP: str = ";"  # column separator in csv files

# Paths
DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
