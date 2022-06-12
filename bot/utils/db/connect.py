import psycopg2
import contextlib

from data import config


# "The Status class has a single attribute, _ok, which is initialized to 1. The error method sets _ok to 0. The status
# property returns the value of _ok."
class Status:
    def __init__(self):
        self._ok = 1

    def error(self):
        self._ok = 0

    @property
    def status(self):
        return self._ok


@contextlib.contextmanager
def database():
    """
    It creates a database connection, creates a cursor, and then yields the cursor and the connection to the caller
    """
    conn = psycopg2.connect(config.URL)
    # conn = psycopg2.connect(
    #     host=config.HOST,
    #     dbname=config.DATABASE,
    #     user=config.USER,
    #     passwd=config.PASSWORD
    # )
    cur = conn.cursor()
    status = Status()
    try:
        yield cur, conn, status
    except Exception as err:
        print(err)
        status.error()
    finally:
        cur.close()
        conn.close()



