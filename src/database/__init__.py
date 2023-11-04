import psycopg2

from api import log
from database.exceptions import InternalServer


def establishing_connection():
    try:
        return psycopg2.connect(
            database="postgres",
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
    except Exception as e:
        log(e)
        raise InternalServer(e)
