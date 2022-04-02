from .connect import database


async def get_access(user_id):
    with database() as (cur, conn):
        sql = "SELECT is_admin FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        result = cur.fetchone()
        return result[0] if result else 0


async def is_exist(user_id):
    with database() as (cur, conn):
        sql = "SELECT first_name FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        result = cur.fetchone()
        return 1 if result else 0


async def get_olympiad_status(user_id, status):
    with database() as (cur, conn):
        sql = "SELECT olympiad_code FROM olympiad_status WHERE user_id = %s AND status = %s"
        cur.execute(sql, [user_id, status])
        result = cur.fetchall()
        return result


async def get_users():
    with database() as (cur, conn):
        sql = "SELECT (id, first_name, last_name)  FROM users"
        cur.execute(sql)
        result = cur.fetchall()
        return result
