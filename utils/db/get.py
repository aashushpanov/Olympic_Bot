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


def get_tracked_olympiads(user_id):
    with database() as (cur, conn):
        sql = "SELECT olympiad_code, status, stage, taken_key FROM olympiad_status WHERE user_id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['olympiad_code', 'status', 'stage', 'taken_key'])
        return data


def get_olympiads_by_status(user_id, status):
    with database() as (cur, conn):
        sql = "SELECT olympiad_code, stage, taken_key, done FROM olympiad_status WHERE user_id = %s AND status = %s"
        cur.execute(sql, [user_id, status])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['olympiad_code', 'stage', 'taken_key', 'done'])
        return data


def get_olympiad_status(user_id, code):
    with database() as (cur, conn):
        sql = "SELECT status, stage, taken_key, done FROM  olympiad_status WHERE olympiad_code = %s AND user_id = %s"
        cur.execute(sql, [code, user_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['status', 'stage', 'taken_key', 'done'])
        return data


def get_user(user_id):
    with database() as (cur, conn):
        sql = "SELECT first_name, last_name, grade, interest FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['first_name', 'last_name', 'grade', 'interest'])
        return data


def get_users():
    with database() as (cur, conn):
        sql = "SELECT id, first_name, last_name, grade, interest  FROM users"
        cur.execute(sql)
        result = cur.fetchall()
        data = pd.DataFrame(result, columns=['user_id', 'first_name', 'last_name', 'grade', 'interest'])
        return data


def get_subjects():
    with database() as (cur, conn):
        sql = "SELECT code, subject_name, section FROM subjects"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['code', 'subject_name', 'section'])
        return data


def get_olympiads():
    with database() as (cur, conn):
        sql = "SELECT code, ol_name, subject_code, stage, start_date, finish_date, active, grade, key_needed," \
              " pre_registration FROM olympiads"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['code', 'name', 'subject_code', 'stage', 'start_date', 'finish_date',
                                          'active', 'grade', 'key_needed', 'pre_registration'])
        return data


def get_olympiad(code):
    with database() as (cur, conn):
        sql = "SELECT ol_name, subject_code, stage, start_date, finish_date, active, grade, key_needed," \
              " pre_registration, urls FROM olympiads WHERE code = %s"
        cur.execute(sql, [code])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['name', 'subject_code', 'stage', 'start_date',
                                          'finish_date', 'active', 'grade', 'key_needed', 'pre_registration', 'urls'])
        return data


