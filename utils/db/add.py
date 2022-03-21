import psycopg2

from connect import database


def add_user(id, f_name, l_name, grad=None):
    with database() as cur:
        sql = "INSERT INTO user (id, first_name, last_name, grad) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (id, f_name, l_name, grad))
