from .connect import database


async def add_user(user_id, f_name, l_name, grad=None, interest: set = None):
	with database() as (cur, conn):
		sql = "INSERT INTO users (id, first_name, last_name, grad, is_admin, interest) VALUES (%s, %s, %s, %s, %s, %s)"
		cur.execute(sql, [user_id, f_name, l_name, grad, 0, list(interest)])
		conn.commit()


async def get_admin_access(user_id):
	with database() as (cur, conn):
		sql = "UPDATE users SET is_admin = 1 WHERE id = %s"
		cur.execute(sql, [user_id])
		conn.commit()
