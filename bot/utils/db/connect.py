import psycopg2
import contextlib

from data import config


@contextlib.contextmanager
def database():
    conn = psycopg2.connect(config.URL)
    # conn = psycopg2.connect(
    #     host=config.HOST,
    #     dbname=config.DATABASE,
    #     user=config.USER,
    #     passwd=config.PASSWORD
    # )
    cur = conn.cursor()
    try:
        yield cur, conn
    except Exception as err:
        print(err)
    finally:
        cur.close()
        conn.close()



