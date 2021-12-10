from src.entities import Manager, Customer, Product, Order
from src.data_loader import EntityDataLoader, TableInfo, fill_table_info_from_alias
from src.order import OrderProcessor
from src._constants import DATA_PATH

ORDER_TABLE = DATA_PATH + "order.csv"

# Manager info
MANAGER_ID = 1
MANAGER_NAME = "Mother Theresa"
MANAGER_LOCATION = "Vilnius"

# Manager logs in
manager = Manager(
    manager_id=MANAGER_ID, manager_name=MANAGER_NAME, location=MANAGER_LOCATION
)

# Entire entity data is preloaded
customer_table_info = fill_table_info_from_alias("customer")
product_table_info = fill_table_info_from_alias("product")
entity_tables = [
    TableInfo(**table_info) for table_info in [customer_table_info, product_table_info]
]
entity_data_loader = EntityDataLoader(entity_tables)
entity_data_loader.load_data()

# Manager selects customer and product, info retrieved from entity table
ENTITY_ID = 1
customer = entity_data_loader.get_single_entity_instance(
    entity=Customer, entity_id=ENTITY_ID
)

# Manager selects product
ENTITY_ID = 1
product1 = entity_data_loader.get_single_entity_instance(
    entity=Product, entity_id=ENTITY_ID
)

ENTITY_ID = 3
product2 = entity_data_loader.get_single_entity_instance(
    entity=Product, entity_id=ENTITY_ID
)

# # Manager fills in order info
ORDER_TYPE = "regular"
ITEMS = [product1, product2]
QUANTITIES = [1, 10]
DISCOUNTS = [0.0, 0.1]

order = Order(
    manager=manager,
    customer=customer,
    order_type=ORDER_TYPE,
    items=ITEMS,
    quantities=QUANTITIES,
    discounts=DISCOUNTS,
)

OrderProcessor(order).export(ORDER_TABLE)
