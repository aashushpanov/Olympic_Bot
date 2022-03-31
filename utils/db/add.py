from pandas import DataFrame

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


async def add_olympiads(olympiads: DataFrame):
    with database() as (cur, conn):
        sql = "SELECT code FROM olympiads"
        cur.execute(sql)
        res = cur.fetchall()
        added = []
        for code in res:
            added.append(code[0])
        existing = []
        for _, olympiad in olympiads.iterrows():
            if olympiad['Код'] not in added:
                sql = "INSERT INTO olympiads (code, ol_name, subject, subject_code, grades, stage) VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(sql, [olympiad['Код'], olympiad['Название'], olympiad['Предмет'], olympiad['Код предмета'],
                                  str([olympiad['мл. класс'], olympiad['ст. класс']]), 1])
            else:
                existing.append(olympiad['Код'])
        conn.commit()
        return existing
