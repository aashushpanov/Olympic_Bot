import psycopg2
import contextlib

from data import config


@contextlib.contextmanager
def database():
    conn = psycopg2.connect(
        host=config.HOST,
        database=config.DATABASE,
        user=config.USER,
        passwd=config.PASSWORD
    )
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()



