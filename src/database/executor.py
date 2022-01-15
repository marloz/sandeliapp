from config.paths import DATABASE
import sqlite3
from traceback import print_exception


class SqlExecutor:

    def __init__(self, database: str = DATABASE):
        self.database = database

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.database)
        self.cursor: sqlite3.Cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is not None:
            print_exception(exception_type, exception_value, traceback)
        self.connection.close()
