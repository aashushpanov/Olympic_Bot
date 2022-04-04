from pandas import DataFrame

from .connect import database


async def add_user(user_id, f_name, l_name, grad=None, interest: set = None):
    with database() as (cur, conn):
        sql = "INSERT INTO users (id, first_name, last_name, grad, is_admin, interest) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, grad, 0, list(interest)])
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
            sql = "INSERT INTO olympiads (code, ol_name, subject_code, grade)" \
                  " VALUES (%s, %s, %s, %s)"
            cur.execute(sql, [olympiad['code'], olympiad['name'], olympiad['subject_code'], olympiad['grade']])
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
            sql = "UPDATE olympiads SET stage = %s, start_date = %s, finish_date = %s, active = %s WHERE code = %s"
            cur.execute(sql, [date['stage'], date['start_date'], date['finish_date'], date['active'], date['code']])
        conn.commit()
    res = True
    return res
