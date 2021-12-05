from src.entities import Manager, Customer, Product, Order
from src.data_loader import EntityDataLoader, TableInfo
from src._constants import ENTITY_TABLES, ORDER_HISTORY_TABLE_INFO
import pandas as pd


# Manager info
MANAGER_ID = 1
MANAGER_NAME = "Mother Theresa"
MANAGER_LOCATION = "Vilnius"

# Manager logs in
manager = Manager(id=MANAGER_ID, name=MANAGER_NAME, location=MANAGER_LOCATION)

# Entire entity data is preloaded
entity_tables = [TableInfo(**table_info) for table_info in ENTITY_TABLES.values()]
entity_data_loader = EntityDataLoader(entity_tables)
entity_data_loader.load_data()

# Manager selects customer and product, info retrieved from entity table
ENTITY_ID = 1
ENTITY = "customer"
customer_info = entity_data_loader.get_single_entity_info_dict(
    table_alias=ENTITY, entity_id=ENTITY_ID
)
customer = Customer(**customer_info)

# Manager selects product
ENTITY_ID = 1
ENTITY = "product"
product_info = entity_data_loader.get_single_entity_info_dict(
    table_alias=ENTITY, entity_id=ENTITY_ID
)
product1 = Product(**product_info)

ENTITY_ID = 3
product_info = entity_data_loader.get_single_entity_info_dict(
    table_alias=ENTITY, entity_id=ENTITY_ID
)
product2 = Product(**product_info)

# Manager fills in order info
ORDER_TYPE = "regular"
ITEMS = [product1, product2]
QUANTITIES = [1, 10]
DISCOUNTS = [0.0, 0.1]

order = Order(
    manager=manager,
    customer=customer,
    type=ORDER_TYPE,
    items=ITEMS,
    quantities=QUANTITIES,
    discounts=DISCOUNTS,
)


def invert_dict(d: dict) -> dict:
    return {v: k for k, v in d.items()}


product_columns = invert_dict(
    entity_data_loader.table_info_dict["product"].column_mapping
)
order_df = order.prepare_for_export(product_columns)

order_history_columns = invert_dict(ORDER_HISTORY_TABLE_INFO["column_mapping"])
order_df = order_df.rename(columns=order_history_columns)[
    list(order_history_columns.values())
]
print(order_df)
