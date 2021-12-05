import os

DATE_FORMAT: str = "%Y-%m-%d"  # Default date format
VAT: float = 0.21  # VAT tax applied in Order
SEP: str = ";"  # column separator in csv files

# Paths
DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# Table info
ENTITY_TABLES = {
    "customer": {
        "alias": "customer",
        "name": os.path.join(DATA_PATH, "customer.csv"),
        "id_column": "customer_id",
        "sort_column": "timestamp",
        "column_mapping": {"customer_id": "id", "customer_name": "name",},
    },
    "product": {
        "alias": "product",
        "name": os.path.join(DATA_PATH, "product.csv"),
        "id_column": "product_id",
        "sort_column": "timestamp",
        "column_mapping": {
            "product_id": "id",
            "product_name": "name",
            "price": "price",
            "category": "category",
            "manufacturer": "manufacturer",
        },
    },
}
ORDER_HISTORY_TABLE_INFO = {
    "alias": "order_history",
    "name": os.path.join(DATA_PATH, "order_history.csv"),
    "id_column": "order_id",
    "sort_column": "timestamp",
    "column_mapping": {
        "order_id": "id",
        "order_date": "date",
        "order_type": "type",
        "manager_id": "manager_id",
        "manager_name": "manager_name",
        "manager_location": "manager_location",
        "customer_id": "customer_id",
        "customer_name": "customer_name",
        "product_id": "product_id",
        "product_name": "product_name",
        "product_category": "category",
        "manufacturer": "manufacturer",
        "price": "price",
        "quantity": "quantity",
        "discount": "discount",
        "vat": "vat",
        "timestamp": "timestamp",
    },
}
