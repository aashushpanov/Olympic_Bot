import pandas as pd
from psycopg2.extras import Json

from pandas import DataFrame, Series

from .connect import database
from .get import get_olympiads


async def add_user(user_id, f_name, l_name, grade=None, literal=None, interest: set = None, time=16):
    with database() as (cur, conn):
        sql = "INSERT INTO users (id, first_name, last_name, grade, literal, is_admin, interest, notify_time)" \
              " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, grade, literal, 0, list(interest), time])
        conn.commit()


def add_interests(user_id, interests):
    with database() as (cur, conn):
        sql = "UPDATE users SET interest = %s WHERE id = %s"
        cur.execute(sql, [interests, user_id])
        conn.commit()


def add_notify_time(time, user_id):
    with database() as (cur, conn):
        sql = "UPDATE users SET notify_time = %s WHERE id = %s"
        cur.execute(sql, [time, user_id])
        conn.commit()


async def set_admin_access(user_id):
    with database() as (cur, conn):
        sql = "UPDATE users SET is_admin = 1 WHERE id = %s"
        cur.execute(sql, [user_id])
        conn.commit()


def add_olympiads(olympiads: DataFrame):
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "INSERT INTO olympiads (code, ol_name, subject_code, grade, active, urls)" \
                  " VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(sql, [olympiad['code'], olympiad['name'], olympiad['subject_code'], olympiad['grade'], 0,
                              Json(olympiad['urls'])])
        conn.commit()


def update_olympiads(olympiads: DataFrame):
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "UPDATE olympiads SET ol_name = %s, subject_code = %s, grade = %s, active = %s, urls = %s WHERE code = %s"
            cur.execute(sql, [olympiad['name'], olympiad['subject_code'], olympiad['grade'], 0,
                              Json(olympiad['urls']), olympiad['code']])
        conn.commit()


def remove_olympiads(olympiads_codes):
    with database() as (cur, conn):
        data = pd.DataFrame(columns=['name', 'subject_code'])
        for olympiad_code in olympiads_codes:
            sql = "DELETE FROM olympiads WHERE code = %s RETURNING ol_name, subject_code, grade"
            cur.execute(sql, [olympiad_code])
            res = cur.fetchall()
            deleting_data = pd.DataFrame(res, columns=['name', 'subject_code', 'grade'])
            data = pd.concat([data, deleting_data], axis=0)
        conn.commit()
    return data


def add_subjects(subjects: DataFrame):
    with database() as (cur, conn):
        for _, subject in subjects.iterrows():
            sql = "INSERT INTO subjects (code, subject_name, section) VALUES (%s, %s, %s)"
            cur.execute(sql, [subject['code'], subject['name'], subject['section']])
        conn.commit()


def update_subjects(subjects: DataFrame):
    with database() as (cur, conn):
        for _, subject in subjects.iterrows():
            sql = "UPDATE subjects SET subject_name = %s, section = %s WHERE code = %s"
            cur.execute(sql, [subject['name'], subject['section'], subject['code']])
        conn.commit()


def remove_subjects(subjects_codes):
    with database() as (cur, conn):
        data = pd.DataFrame(columns=['name'])
        for subject_code in subjects_codes:
            sql = "DELETE FROM subjects WHERE code = %s RETURNING name"
            cur.execute(sql, [subject_code])
            res = cur.fetchall()
            deleting_data = pd.DataFrame(res, columns=['name'])
            data = pd.concat([data, deleting_data], axis=0)
        conn.commit()
    return data


def add_dates(dates: DataFrame):
    with database() as (cur, conn):
        for _, date in dates.iterrows():
            sql = "UPDATE olympiads SET stage = %s, start_date = %s, finish_date = %s, active = %s, key_needed = %s," \
                  " pre_registration = %s WHERE code = %s"
            cur.execute(sql, [date['stage'], date['start_date'], date['finish_date'], date['active'],
                              date['key'], date['pre_registration'], date['code']])
        conn.commit()


def add_olympiads_to_track(olympiads: DataFrame, user_id):
    current_olympiads = get_olympiads()
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "INSERT INTO olympiad_status (user_id, olympiad_code, status, stage, taken_key)" \
                  "VALUES (%s, %s, %s, %s, %s)"
            status = 'idle' if current_olympiads[current_olympiads['code'] == olympiad['code']]['pre_registration'].item() else 'reg'
            cur.execute(sql, [user_id, olympiad['code'], status, olympiad['stage'], ''])
        conn.commit()


def set_registration(olympiad_code, user_id, stage):
    with database() as (cur, conn):
        sql = "UPDATE olympiad_status SET status = %s WHERE olympiad_code = %s AND user_id = %s AND stage = %s"
        cur.execute(sql, ['reg', olympiad_code, user_id, stage])
        conn.commit()


def set_execution(olympiad_code, user_id, stage):
    with database() as (cur, conn):
        sql = "UPDATE olympiad_status SET status = %s WHERE olympiad_code = %s AND user_id = %s AND stage = %s"
        cur.execute(sql, ['done', olympiad_code, user_id, stage])
        conn.commit()


def set_missed(olympiads: DataFrame):
    with database() as (cur, conn):
        for _, olympiad in olympiads.iterrows():
            sql = "UPDATE olympiad_status SET status = %s WHERE olympiad_code = %s AND stage = %s"
            cur.execute(sql, ['missed', olympiad['code'], olympiad['stage']])
        conn.commit()


def set_inactive(inactive_olympiads):
    with database() as (cur, conn):
        for _, olympiad in inactive_olympiads.iterrows():
            sql = "UPDATE olympiads SET active = %s WHERE code = %s"
            cur.execute(sql, [0, olympiad['code']])
        conn.commit()


def set_file_ids(file_type, file_id='', file_unique_id='', url=''):
    with database() as (cur, conn):
        sql = "UPDATE files_ids SET file_id = %s, file_unique_id = %s, changed = 0, url = %s WHERE file_type = %s"
        cur.execute(sql, [file_id, file_unique_id, url, file_type])
        conn.commit()


def change_files(file_types):
    with database() as (cur, conn):
        for file_type in file_types:
            sql = "UPDATE files_ids SET changed = 1 WHERE file_type = %s"
            cur.execute(sql, [file_type])
        conn.commit()


def set_keys(keys: DataFrame, keys_count: dict):
    with database() as (cur, conn):
        for _, key in keys.iterrows():
            sql = "INSERT INTO keys (olympiad_code, no, key) VALUES (%s, %s, %s)"
            cur.execute(sql, [key['olympiad_code'], key['no'], key['key']])
        for olympiad, keys_count in keys_count.items():
            sql = "UPDATE olympiads SET keys_count = %s WHERE code = %s"
            cur.execute(sql, [keys_count, olympiad])
        conn.commit()


def add_notifications(notifications: DataFrame):
    with database() as (cur, conn):
        for _, row in notifications.iterrows():
            sql = "INSERT INTO notifications (user_id, olympiad_code, message, type) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, [row['user_id'], row['olympiad_code'], row['message'], row['type']])
        conn.commit()


def add_question(question: Series):
    with database() as (cur, conn):
        sql = "INSERT INTO questions (from_user, message, answer) VALUES (%s, %s, '') RETURNING no"
        cur.execute(sql, [question['user_id'], question['message']])
        res = cur.fetchone()
        conn.commit()
    return res[0]


def set_message_id_to_questions(questions: DataFrame):
    with database() as (cur, conn):
        for _, question in questions.iterrows():
            sql = "UPDATE questions SET message_id = %s WHERE no = %s"
            cur.execute(sql, [question['message_id'], question['no']])
        conn.commit()


def add_question_answer(question_no, answer, admin):
    with database() as (cur, conn):
        sql = "UPDATE questions SET answer = %s, to_admin = %s WHERE no = %s"
        cur.execute(sql, [answer, admin, question_no])
        conn.commit()
