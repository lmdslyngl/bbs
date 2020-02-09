
import psycopg2
import psycopg2.pool
import contextlib
import conf


pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1, maxconn=conf.db_max_pool_connections,
    host=conf.db_host,
    user=conf.db_user,
    password=conf.db_password,
    dbname=conf.db_name)


@contextlib.contextmanager
def get_connection():
    try:
        con = pool.getconn()
        yield con
    finally:
        pool.putconn(con)
