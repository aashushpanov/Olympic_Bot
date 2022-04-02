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


async def add_olympiads(olympiads: DataFrame = None, subjects: DataFrame = None):
    with database() as (cur, conn):
        if olympiads is not None:
            sql = "SELECT code FROM olympiads"
        else:
            sql = "SELECT code FROM subjects"
        cur.execute(sql)
        res = cur.fetchall()
        added = []
        for code in res:
            added.append(code[0])
        add = []
        existing = []
        subjects_not_existing = []
        if olympiads is not None:
            for _, olympiad in olympiads.iterrows():
                if olympiad['Код'] not in added:
                    sql = "SELECT code FROM subjects WHERE subject_name = %s"
                    cur.execute(sql, [olympiad['Предмет']])
                    subject_code = cur.fetchone()
                    if subject_code:
                        subject_code = subject_code[0]
                    else:
                        subjects_not_existing.append(olympiad['Предмет'])
                        continue
                    sql = "INSERT INTO olympiads (code, ol_name, subject_code, grades, stage)" \
                          " VALUES (%s, %s, %s, %s, %s)"
                    cur.execute(sql, [olympiad['Код'], olympiad['Название'], subject_code,
                                      str([olympiad['мл. класс'], olympiad['ст. класс']]), 1])
                    add.append(olympiad['Код'])
                else:
                    existing.append(olympiad['Код'])
        else:
            for _, subject in subjects.iterrows():
                if subject['Код предмета'] not in added:
                    sql = "INSERT INTO subjects (code, subject_name, section) VALUES (%s, %s, %s)"
                    cur.execute(sql, [subject['Код предмета'], subject['Предмет'], subject['Раздел']])
                    add.append(subject['Код предмета'])
                else:
                    existing.append(subject['Код предмета'])
        conn.commit()
        return add, existing, subjects_not_existing
