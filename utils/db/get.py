from .connect import database

import pandas as pd


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


def get_subjects():
    with database() as (cur, conn):
        sql = "SELECT code, subject_name, section FROM subjects"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['code', 'subject_name', 'section'])
        return data


def get_olympiads():
    with database() as (cur, conn):
        sql = "SELECT code, ol_name, subject_code, stage, start_date, finish_date, active, grade FROM olympiads"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['code', 'name', 'subject_code',
                                          'stage', 'start_date', 'finish_date', 'active', 'grade'])
        return data

