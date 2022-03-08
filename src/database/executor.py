import os
from traceback import print_exception

import psycopg2
from config.paths import DATABASE

# Available as env variable in connected Heroko app conected Postgres database
DATABASE_URL = os.environ.get("DATABASE_URL")


class SqlExecutor:
    def __init__(self, database: str = DATABASE):
        self.database = database
        self.connection: psycopg2.extensions.connection
        self.cursor: psycopg2.extensions.cursor

    def __enter__(self):
        self.connection = psycopg2.connect(self.database)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type:
            print_exception(exception_type, exception_value, traceback)
        self.connection.close()
