import MySQLdb
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

class MySQLWrapperClass():
    """Redis client wrapper to have 'with' sougar"""

    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT'))
    user = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD') if os.getenv('DB_PASSWORD') != 'null' else None
    database = os.getenv('DB_DATABASE')
    charset = 'utf8' # utf8mb4_unicode_ci
    # charset = 'utf8mb4'

    db = None

    def __init__(self, *args, **kwargs):
        # fill with default values
        if "host" not in kwargs:
            kwargs["host"] = self.host

        if "port" not in kwargs:
            kwargs["port"] = self.port

        if "user" not in kwargs and self.user is not None:
            kwargs["user"] = self.user

        if "password" not in kwargs and self.password is not None:
            kwargs["password"] = self.password

        if "database" not in kwargs and self.database is not None:
            kwargs["database"] = self.database

        if "charset" not in kwargs:
            kwargs["charset"] = self.charset

        # super().__init__(*args, **kwargs)
        self.db = MySQLdb.connect(*args, **kwargs)


    def __enter__(self):
        return (self.db, self.db.cursor())

    def __exit__(self, type, value, traceback):
        self.db.close()

    # def commit(self):
    #     return self.db.commit()

from sqlalchemy import create_engine
class SQLAlchemyWrapperClass():

    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT'))
    user = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD') if os.getenv('DB_PASSWORD') != 'null' else None
    database = os.getenv('DB_DATABASE')
    charset = 'utf8' # utf8mb4_unicode_ci
    # charset = 'utf8mb4'
    # echo_sql = True if os.getenv('DB_ECHO') in ('True', 'true', 'yes', '1') else False
    echo_sql = False

    def __init__(self, *args, **kwargs):
        if self.password:
            conn_string = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
        else:
            conn_string = f'mysql+pymysql://{self.user}@{self.host}:{self.port}/{self.database}'
        # self.engine = create_engine(conn_string, echo=True)
        self.engine = create_engine(conn_string, echo=self.echo_sql, pool_size=30, max_overflow=0, pool_recycle=3600, pool_timeout=300)
        self.connection = self.engine.connect()

        if "_conn" not in kwargs:
            self._conn = None
        else:
            self._conn = self.connection

    def __enter__(self):
        # return (self.conn, self.db.cursor())
        return self.connection

    def __exit__(self, type, value, traceback):
        if self._conn is None:
            self.connection.close()

        # self.db.close()


class SQLAlchemyBCWrapperClass():

    host = os.getenv('BC_DB_HOST')
    port = int(os.getenv('BC_DB_PORT'))
    user = os.getenv('BC_DB_USERNAME')
    password = os.getenv('BC_DB_PASSWORD') if os.getenv('BC_DB_PASSWORD') != 'null' else None
    database = os.getenv('BC_DB_DATABASE')
    charset = 'utf8' # utf8mb4_unicode_ci
    # charset = 'utf8mb4'
    # echo_sql = True if os.getenv('DB_ECHO') in ('True', 'true', 'yes', '1') else False
    echo_sql = False

    def __init__(self, *args, **kwargs):
        if self.password:
            conn_string = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
        else:
            conn_string = f'mysql+pymysql://{self.user}@{self.host}:{self.port}/{self.database}'
        # self.engine = create_engine(conn_string, echo=True)
        self.engine = create_engine(conn_string, echo=self.echo_sql)
        self.connection = self.engine.connect()

    def __enter__(self):
        # return (self.conn, self.db.cursor())
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()

        # self.db.close()

