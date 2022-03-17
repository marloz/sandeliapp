import os
from traceback import print_exception

import sqlalchemy
from dotenv import load_dotenv

# Available as env variable in connected Heroko app conected Postgres database
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")


class SqlExecutor:
    def __init__(self, database: str = DATABASE_URL):
        self.database = database
        self.connection: sqlalchemy.engine.base.Engine

    def __enter__(self):
        engine = sqlalchemy.create_engine(self.database)
        self.connection = engine.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type:
            print_exception(exception_type, exception_value, traceback)
        self.connection.close()
