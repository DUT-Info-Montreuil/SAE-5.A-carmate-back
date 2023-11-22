import psycopg2

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
        raise InternalServer(str(e))
