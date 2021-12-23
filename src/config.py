import os

# Dates
DATE_FORMAT: str = "%Y-%m-%d"  # Default date format
TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S.%f'  # Default timestamp format

# Paths
DATA_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data")

# Order
VAT: float = 0.21  # VAT tax applied in Order
ORDER_TYPES = ['regular',
               'return',
               'credit',
               'stock refill']

# Data loader
SORT_COLUMN = "timestamp"
ID_SUFFIX = "id"
TABLE_FORMAT = "csv"
ENTITY_NAME_COLUMN_SUFFIX = 'name'
COLUMN_NAME_SEPARATOR = '_'

# Other
SEP: str = ";"  # column separator in csv files

# Main
DATASOURCES = ['customer', 'product', 'manager']
