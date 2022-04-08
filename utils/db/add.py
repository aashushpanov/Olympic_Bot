from psycopg2.extras import Json

from pandas import DataFrame

from .connect import database


async def add_user(user_id, f_name, l_name, grade=None, interest: set = None):
    with database() as (cur, conn):
        sql = "INSERT INTO users (id, first_name, last_name, grade, is_admin, interest) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, grade, 0, list(interest)])
        conn.commit()


def add_interests(user_id, interests):
    with database() as (cur, conn):
        sql = "UPDATE users SET interest = %s WHERE id = %s"
        cur.execute(sql, [interests, user_id])
        conn.commit()


async def set_admin_access(user_id):
    with database() as (cur, conn):
        sql = "UPDATE users SET is_admin = 1 WHERE id = %s"
        cur.execute(sql, [user_id])
        conn.commit()


def add_olympiads(olympiads: DataFrame):
    res = False
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "INSERT INTO olympiads (code, ol_name, subject_code, grade, active, urls)" \
                  " VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, [olympiad['code'], olympiad['name'], olympiad['subject_code'], olympiad['grade'], 0,
                              Json(olympiad['urls'])])
        conn.commit()
    res = True
    return res


def add_subjects(subjects: DataFrame):
    res = False
    with database() as (cur, conn):
        for _, subject in subjects.iterrows():
            sql = "INSERT INTO subjects (code, subject_name, section) VALUES (%s, %s, %s)"
            cur.execute(sql, [subject['Код предмета'], subject['Предмет'], subject['Раздел']])
        conn.commit()
    res = True
    return res


def add_dates(dates: DataFrame):
    res = False
    with database() as (cur, conn):
        for _, date in dates.iterrows():
            sql = "UPDATE olympiads SET stage = %s, start_date = %s, finish_date = %s, active = %s, key_needed = %s," \
                  " pre_registration = %s WHERE code = %s"
            cur.execute(sql, [date['stage'], date['start_date'], date['finish_date'], date['active'],
                              date['key'], date['pre_registration'], date['code']])
        conn.commit()
    res = True
    return res


def add_olympiads_to_track(olympiads: DataFrame, user_id):
    res = False
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "INSERT INTO olympiad_status (user_id, olympiad_code, status, stage, taken_key, done)" \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, [user_id, olympiad['code'], 'idle', olympiad['stage'], '', 0])
        conn.commit()
    res = True
    return res


def set_inactive(inactive_olympiads):
    with database() as (cur, conn):
        for olympiad in inactive_olympiads.iterrows():
            sql = "UPDATE olympiads SET active = %s WHERE code = %s"
            cur.execute(sql, [0, olympiad['code']])
        conn.commit()
