
import psycopg2
import psycopg2.pool
import contextlib


pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=20,
    host="localhost",
    user="testrole",
    password="hogehoge",
    dbname="bbsdb")


@contextlib.contextmanager
def get_connection():
    try:
        con = pool.getconn()
        yield con
    finally:
        pool.putconn(con)
