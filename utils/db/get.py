from .connect import database


async def get_access(user_id):
	with database() as (cur, conn):
		sql = "SELECT is_admin FROM users WHERE id = %s"
		cur.execute(sql, [user_id])
		result = cur.fetchone()
		return result[0]


async def is_exist(user_id):
	with database() as (cur, conn):
		sql = "SELECT first_name FROM users WHERE id = %s"
		cur.execute(sql, [user_id])
		result = cur.fetchone()
		return 1 if result else 0
