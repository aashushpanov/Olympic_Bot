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
        sql = "SELECT olympiad_code, stage, taken_key FROM olympiad_status WHERE user_id = %s AND status = %s"
        cur.execute(sql, [user_id, status])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['olympiad_code', 'stage', 'taken_key'])
    return data


def get_olympiad_status(user_id, code, stage):
    with database() as (cur, conn):
        sql = "SELECT status, stage, taken_key FROM  olympiad_status WHERE olympiad_code = %s AND user_id = %s AND stage = %s"
        cur.execute(sql, [code, user_id, stage])
        res = cur.fetchone()
        data = pd.Series(res, index=['status', 'stage', 'taken_key'])
    return data


def get_all_olympiads_status():
    with database() as (cur, conn):
        sql = "SELECT user_id,olympiad_code, status, stage, taken_key FROM olympiad_status"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['user_id', 'olympiad_code', 'status', 'stage', 'taken_key'])
        return data


def get_user(user_id):
    with database() as (cur, conn):
        sql = "SELECT first_name, last_name, grade, literal, interest, notify_time FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['first_name', 'last_name', 'grade', 'literal', 'interest', 'notify_time'])
    return data


def get_users():
    with database() as (cur, conn):
        sql = "SELECT id, first_name, last_name, grade, literal, interest  FROM users"
        cur.execute(sql)
        result = cur.fetchall()
        data = pd.DataFrame(result, columns=['user_id', 'first_name', 'last_name', 'grade', 'literal', 'interest'])
    return data


def get_admins():
    with database() as (cur, conn):
        sql = "SELECT id, first_name, last_name FROM users WHERE is_admin = 2"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['admin_id', 'first_name', 'last_name'])
    return data


def get_class_managers():
    with database() as (cur, conn):
        sql = "SELECT id, first_name, last_name, grade, literal FROM users WHERE is_admin = 1"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['admin_id', 'first_name', 'last_name', 'grade', 'literal'])
    return data


def get_users_by_notification_time(time):
    with database() as (cur, conn):
        sql = "SELECT id FROM users WHERE notify_time < %s"
        cur.execute(sql, [time])
        res = [x[0] for x in cur.fetchall()]
    return res


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
              " pre_registration, urls, keys_count FROM olympiads"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['code', 'name', 'subject_code', 'stage', 'start_date', 'finish_date',
                                          'active', 'grade', 'key_needed', 'pre_registration', 'urls', 'keys_count'])
    return data


def get_olympiad(code):
    with database() as (cur, conn):
        sql = "SELECT ol_name, subject_code, stage, start_date, finish_date, active, grade, key_needed," \
              " pre_registration, urls, keys_count FROM olympiads WHERE code = %s"
        cur.execute(sql, [code])
        res = cur.fetchone()
        data = pd.Series(res, index=['name', 'subject_code', 'stage', 'start_date', 'finish_date', 'active',
                                          'grade', 'key_needed', 'pre_registration', 'urls', 'keys_count'])
    return data


def get_file(file_type):
    with database() as (cur, conn):
        sql = "SELECT file_id, file_unique_id, changed, url FROM files_ids WHERE file_type = %s"
        cur.execute(sql, [file_type])
        res = cur.fetchone()
        data = pd.Series(res, index=['file_id', 'file_unique_id', 'changed', 'url'])
    return data


def get_key_from_db(user_id, olympiad_code, stage):
    with database() as (cur, conn):
        sql = "SELECT key, no FROM keys WHERE olympiad_code = %s AND no =" \
              " (SELECT MAX(no) FROM keys WHERE olympiad_code = %s AND is_taken = 0)"
        cur.execute(sql, [olympiad_code, olympiad_code])
        res = cur.fetchone()
        key = res[0]
        key_no = res[1]
        sql = "UPDATE olympiad_status SET taken_key = %s WHERE user_id = %s AND stage = %s AND olympiad_code = %s"
        cur.execute(sql, [key, user_id, stage, olympiad_code])
        sql = "UPDATE olympiads SET keys_count = %s WHERE code = %s"
        cur.execute(sql, [key_no, olympiad_code])
        sql = "UPDATE keys SET is_taken = 1 WHERE olympiad_code = %s AND no = %s"
        cur.execute(sql, [olympiad_code, key_no])
        conn.commit()
    return key


def get_notifications(users_id):
    with database() as (cur, conn):
        sql = "DELETE FROM notifications WHERE user_id = ANY(%s) RETURNING user_id, olympiad_code, message, type "
        cur.execute(sql, [users_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['user_id', 'olympiad_code', 'message', 'type'])
        conn.commit()
    return data


def get_questions_counts():
    with database() as (cur, conn):
        sql = "SELECT count(no) FROM questions WHERE answer  = ''"
        cur.execute(sql)
        res = cur.fetchall()
    return res[0][0]


def get_new_questions():
    with database() as (cur, conn):
        sql = "SELECT no, from_user, message, message_id FROM questions WHERE answer = '' "
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['no', 'user_id', 'message', 'message_id'])
    return data


def get_question(no):
    with database() as (cur, conn):
        sql = "SELECT from_user, message, message_id, answer, to_admin FROM questions WHERE no = %s "
        cur.execute(sql, [no])
        res = cur.fetchone()
        data = pd.Series(res, index=['from_user', 'message', 'message_id', 'answer', 'to_admin'])
    return data


def get_answers():
    with database() as (cur, conn):
        sql = "SELECT no, from_user, message, message_id, answer, to_admin FROM questions"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['no', 'from_user', 'message', 'message_id', 'answer', 'to_admin'])
    return data
