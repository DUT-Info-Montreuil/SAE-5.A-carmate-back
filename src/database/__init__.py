import psycopg2


def etablishing_connection():
    return psycopg2.connect(
        database="sae",
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432'
    )
