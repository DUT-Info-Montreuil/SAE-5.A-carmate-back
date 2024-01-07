import psycopg2
import os

from database.exceptions import InternalServer


def establishing_connection():
    if any([not os.getenv("POSTGRES_DB"), not os.getenv("POSTGRES_USER"), not os.getenv("POSTGRES_PWD"), not os.getenv("POSTGRES_HOST"), not os.getenv("POSTGRES_PORT")]):
        raise Exception("Environment variable about POSTGRES must be set !")

    try:
        return psycopg2.connect(
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PWD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
    except Exception as e:
        raise InternalServer(str(e))


from . import schemas
from . import exceptions
from . import interfaces

from .tables_name import *

from . import repositories
