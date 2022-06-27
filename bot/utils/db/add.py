import pandas as pd
from psycopg2.extras import Json
import datetime as dt

from pandas import DataFrame, Series

from .connect import database
from .get import get_olympiads


def add_user(user_id, f_name, l_name, grade=None, literal=None, interests: set = None, time=16):
    """
    It adds a user to the database

    :param user_id: The user's id
    :param f_name: First name
    :param l_name: Last name
    :param grade: int
    :param literal: the literal of the grade, e.g. 'A'
    :param interests: set = None
    :type interests: set
    :param time: The time of day the user wants to be notified, defaults to 16 (optional)
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        date = dt.date.today()
        sql = "INSERT INTO users (id, f_name, l_name, is_admin, notification_time, is_active, reg_date," \
              " last_active_date) VALUES (%s, %s, %s, 0, %s, 1, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, time, date, date])
        sql = "SELECT id FROM grades WHERE grade_num = %s AND grade_literal = %s"
        cur.execute(sql, [grade, literal])
        res = cur.fetchone()
        grade_id = None if not res else res[0]
        if not grade_id:
            sql = "INSERT INTO grades (grade_num, grade_literal) VALUES (%s, %s) RETURNING id"
            cur.execute(sql, [grade, literal])
            grade_id = cur.fetchone()[0]
        sql = "INSERT INTO user_refer_grade (grade_id, user_id) VALUES (%s, %s)"
        cur.execute(sql, [grade_id, user_id])
        for interest in interests:
            sql = "INSERT INTO interests (user_id, subject_id) VALUES (%s, %s)"
            cur.execute(sql, [user_id, interest])
        conn.commit()
    return status.status


def change_name(user_id, f_name, l_name):
    """
    "Change the first and last name of a user in the database."

    The function takes three arguments: user_id, f_name, and l_name. The first line of the function is a with statement.
    This is a Python construct that allows you to write code that will automatically clean up after itself. In this case,
    the with statement will automatically close the database connection when the function is done

    :param user_id: The user's id
    :param f_name: The new first name of the user
    :param l_name: last name
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET first_name = %s, last_name = %s WHERE id = %s"
        cur.execute(sql, [f_name, l_name, user_id])
        conn.commit()
    return status.status


def add_interests(user_id, interests):
    """
    It takes a user_id and a list of interests, and adds each interest to the database

    :param user_id: The user's id
    :param interests: a list of subject_ids
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "DELETE FROM interests WHERE user_id = %s"
        cur.execute(sql, [user_id])
        for interest in interests:
            sql = "INSERT INTO interests (user_id, subject_id) VALUES (%s, %s)"
            cur.execute(sql, [user_id, interest])
        conn.commit()
    return status.status


def add_notify_time(time, user_id):
    """
    It updates the notify_time column in the users table with the time and user_id passed in

    :param time: The time you want to set the notification for
    :param user_id: The user's ID
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET notify_time = %s WHERE id = %s"
        cur.execute(sql, [time, user_id])
        conn.commit()
    return status.status


def add_admin(user_id, f_name, l_name, time, email):
    """
    It deletes a user from the database and then adds them back as an admin

    :param user_id: The user's ID
    :param f_name: First name of the user
    :param l_name: last name
    :param time: time of day to send notifications
    :param email: The email address of the user
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        date = dt.date.today()
        sql = "DELETE FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        sql = "INSERT INTO users (id, f_name, l_name, is_admin, notification_time, email, is_active, reg_date," \
              " last_active_date) VALUES (%s, %s, %s, 3, %s, %s, 1, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, time, email, date, date])
        conn.commit()
    return status.status


def admin_migrate(user_ids):
    """
    It takes a list of user ids and makes them admins

    :param user_ids: a list of user ids to migrate
    :return: The status of the database.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET is_admin = 3 WHERE id = ANY(%s)"
        cur.execute(sql, [user_ids])
        sql = "DELETE FROM interests WHERE user_id = ANY(%s)"
        cur.execute(sql, [user_ids])
        sql = "DELETE FROM user_refer_grade WHERE user_id = ANY(%s)"
        cur.execute(sql, [user_ids])
        conn.commit()
    return status.status


def remove_admin_access(user_ids):
    """
    It removes admin access from a list of users

    :param user_ids: A list of user ids to remove admin access from
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "DELETE FROM users WHERE id = ANY(%s)"
        cur.execute(sql, [user_ids])
        conn.commit()
    return status.status


def add_class_manager(user_id, f_name, l_name, grades, literals, quantity, time, email):
    with database() as (cur, conn, status):
        date = dt.date.today()
        sql = "INSERT INTO users (id, f_name, l_name, notification_time, email, is_admin, is_active, reg_date," \
              " last_active_date) VALUES (%s, %s, %s, %s, %s, 2, 1, %s, %s)"
        cur.execute(sql, [user_id, f_name, l_name, time, email, date, date])
        grade_list = [[grades[i], literals[i], quantity[i]] for i in range(len(grades))]
        for grade_num, grade_literal, grade_quantity in grade_list:
            sql = "SELECT id FROM grades WHERE grade_num = %s AND grade_literal = %s"
            cur.execute(sql, [grade_num, grade_literal])
            res = cur.fetchone()
            grade_id = None if not res else res[0]
            if not grade_id:
                sql = "INSERT INTO grades (grade_num, grade_literal, grade_quantity) VALUES (%s, %s, %s) RETURNING id"
                cur.execute(sql, [grade_num, grade_literal, grade_quantity])
                grade_id = cur.fetchone()[0]
            sql = "INSERT INTO user_refer_grade (grade_id, user_id) VALUES (%s, %s)"
            cur.execute(sql, [grade_id, user_id])

        conn.commit()
    return status.status


def update_cm_key_limits():
    with database() as (cur, conn, status):
        sql = "DELETE FROM cm_key_limits WHERE olympiad_id = ANY(SELECT id FROM sch1210.olympiads" \
              " WHERE key_needed = 1 AND is_active = 0)"
        cur.execute(sql)
        sql = "SELECT users.id, grade_num, sum(grade_quantity) from users" \
              " RIGHT JOIN user_refer_grade ON users.id = user_refer_grade.user_id" \
              " LEFT JOIN grades ON grades.id = user_refer_grade.grade_id" \
              " WHERE is_admin = 2 GROUP BY users.id, grade_num"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['user_id', "grade_num", 'grade_quantity'])
        for _, row in data.iterrows():
            sql = "SELECT id FROM olympiads WHERE grade = %s"
            cur.execute(sql, [int(row['grade_num'])])
            res = cur.fetchall()
            if res is None:
                continue
            for olympiad_id in res:
                sql = "INSERT INTO cm_key_limits (user_id, olympiad_id, key_remains)" \
                      " VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
                user_id = int(row['user_id'])
                grade_quantity = int(row['grade_quantity'])
                cur.execute(sql, [user_id, olympiad_id, grade_quantity])
        conn.commit()


def get_keys_to_cm(user_id, olympiad_id, key_quantity):
    """
    Он принимает user_id, olympiad_id и key_quantity и возвращает список ключей и статус

    :param user_id: id пользователя, который запрашивает ключи
    :param olympiad_id: идентификатор олимпиады
    :param key_quantity: список целых чисел, каждое число — это количество ключей, которое пользователь хочет получить для
    определенной олимпиады
    :return: Ключи и статус
    """
    with database() as (cur, conn, status):
        keys = []
        key_ids = []
        for _ in range(key_quantity):
            sql = "SELECT key, id FROM keys WHERE olympiad_id = %s AND id =" \
                  " (SELECT MAX(id) FROM keys WHERE olympiad_id = %s AND is_taken = 0)"
            cur.execute(sql, [olympiad_id, olympiad_id])
            res = cur.fetchone()
            key = res[0]
            key_id = res[1]
            keys.append(key)
            key_ids.append(key_id)
            sql = "UPDATE keys SET is_taken = 1 WHERE id = %s"
            cur.execute(sql, [key_id])
            sql = "UPDATE olympiads SET keys_count = keys_count - 1 WHERE id = %s"
            cur.execute(sql, [olympiad_id])
            sql = "INSERT INTO cm_keys (user_id, key_id) VALUES (%s, %s)"
            cur.execute(sql, [user_id, key_id])
        sql = "UPDATE cm_key_limits SET key_remains = key_remains - %s WHERE olympiad_id = %s"
        cur.execute(sql, [key_quantity, olympiad_id])
        conn.commit()
    return keys, key_ids, status.status


def add_key_label(user_id, key_id, label):
    with database() as (cur, conn, status):
        sql = "UPDATE cm_keys SET label = %s WHERE user_id = %s AND key_id = %s"
        cur.execute(sql, [label, user_id, key_id])
        conn.commit()
    return status.status


def add_teaching(user_id, subjects: dict):
    """
    Он принимает user_id и словарь предметов и добавляет данные обучения в базу данных.

    :param user_id: идентификатор пользователя, которому вы хотите добавить обучение
    :param subjects: словарь subject_id: {'grades': [], 'literals': []}
    :type subjects: dict
    :return: Статус подключения к базе данных.
    """
    with database() as (cur, conn, status):
        for subject_id in subjects.keys():
            subject_data = subjects[subject_id]
            grade_list = [[subject_data['grades'][i], subject_data['literals'][i]]
                          for i in range(len(subject_data['grades']))]
            for grade_num, grade_literal in grade_list:
                sql = "SELECT id FROM grades WHERE grade_num = %s AND grade_literal = %s"
                cur.execute(sql, [grade_num, grade_literal])
                res = cur.fetchone()
                grade_id = None if not res else res[0]
                if not grade_id:
                    sql = "INSERT INTO grades (grade_num, grade_literal) VALUES (%s, %s) RETURNING id"
                    cur.execute(sql, [grade_num, grade_literal])
                    grade_id = cur.fetchone()[0]
                sql = "INSERT INTO teaching (user_id, subject_id, grade_id) VALUES (%s, %s, %s)"
                cur.execute(sql, [user_id, subject_id, grade_id])
        conn.commit()
    return status.status


def class_manager_migrate(user_id):
    """
    It takes a user id and makes that user a class manager

    :param user_id: The user's ID
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET is_admin = 2 WHERE id = %s"
        cur.execute(sql, [user_id])
        conn.commit()
    return status.status


def add_email(user_id, email):
    """
    It updates the email address of a user in the database

    :param user_id: The user's id
    :param email: The email address to add to the user
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET email = %s WHERE id = %s"
        cur.execute(sql, [email, user_id])
        conn.commit()
    return status.status


def set_user_file_format(user_id, flag):
    """
    It updates the user's file format preference in the database

    :param user_id: The user's ID
    :param flag: True or False
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE users SET to_google_sheets = %s WHERE id = %s"
        cur.execute(sql, [flag, user_id])
        conn.commit()
    return status.status


def add_olympiads(olympiads: DataFrame):
    """
    It takes a dataframe of olympiads and adds them to the database

    :param olympiads: DataFrame
    :type olympiads: DataFrame
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        for _, olympiad in olympiads.iterrows():
            sql = "INSERT INTO olympiads (name, code, subject_id, grade, is_active, urls, key_needed, pre_registration)" \
                  " VALUES (%s, %s, %s, %s, 0, %s, 0, 0)"
            cur.execute(sql, [olympiad['name'], olympiad['code'], olympiad['subject_id'], olympiad['grade'],
                              Json(olympiad['urls'])])
        conn.commit()
    return status.status


def update_olympiads(olympiads: DataFrame):
    """
    It updates the olympiads table in the database with the data in the olympiads dataframe

    :param olympiads: DataFrame
    :type olympiads: DataFrame
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        for _, olympiad in olympiads.iterrows():
            sql = "UPDATE olympiads SET name = %s, subject_id = %s, grade = %s, is_active = %s, urls = %s WHERE id = %s"
            cur.execute(sql, [olympiad['name'], olympiad['subject_id'], olympiad['grade'], 0,
                              Json(olympiad['urls']), olympiad['id']])
        conn.commit()
    return status.status


def remove_olympiads(olympiads_ids):
    """
    It deletes the olympiads with the given ids and returns the deleted olympiads' names, subject codes and grades

    :param olympiads_ids: list of olympiads ids to be deleted
    :return: A dataframe with the name, subject_code, and grade of the olympiads that were deleted.
    """
    with database() as (cur, conn, status):
        sql = "DELETE FROM olympiads WHERE id = ANY(%s) RETURNING name, subject_id, grade"
        cur.execute(sql, [olympiads_ids])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['name', 'subject_code', 'grade'])
        conn.commit()
    return data, status.status


def add_subjects(subjects: DataFrame):
    """
    It takes a dataframe of subjects, and adds them to the database

    :param subjects: DataFrame
    :type subjects: DataFrame
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        for _, subject in subjects.iterrows():
            sql = "INSERT INTO subjects (code, name, section) VALUES (%s, %s, %s)"
            cur.execute(sql, [subject['code'], subject['name'], subject['section']])
        conn.commit()
    return status.status


def update_subjects(subjects: DataFrame):
    """
    It updates the subjects table with the given data

    :param subjects: DataFrame
    :type subjects: DataFrame
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        for _, subject in subjects.iterrows():
            sql = "UPDATE subjects SET name = %s, section = %s WHERE code = %s"
            cur.execute(sql, [subject['name'], subject['section'], subject['code']])
        conn.commit()
    return status.status


def remove_subjects(subjects_codes):
    """
    It deletes subjects from the database and returns the names of the deleted subjects

    :param subjects_codes: list of subjects codes to be removed
    :return: A dataframe with the names of the subjects that were removed.
    """
    with database() as (cur, conn, status):
        sql = "DELETE FROM subjects WHERE code = ANY(%s) RETURNING name"
        cur.execute(sql, [subjects_codes])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['name'])
        conn.commit()
    return data, status.status


def add_dates(dates: DataFrame):
    """
    It takes a dataframe of dates and updates the database with the
    dates

    :param dates: DataFrame
    :type dates: DataFrame
    :return: status.status
    """
    with database() as (cur, conn, status):
        for _, date in dates.iterrows():
            sql = "UPDATE olympiads SET stage = %s, start_date = %s, end_date = %s, is_active = %s, key_needed = %s," \
                  " pre_registration = %s WHERE id = %s"
            cur.execute(sql, [date['stage'], date['start_date'], date['end_date'], date['is_active'],
                              date['key'], date['pre_registration'], date['id']])
        conn.commit()
    return status.status


def add_olympiads_to_track(olympiads: DataFrame, user_id):
    """
    It adds olympiads to the track of a user

    :param olympiads: DataFrame
    :type olympiads: DataFrame
    :param user_id: the user's id
    :return: status.status
    """
    current_olympiads = get_olympiads()
    with database() as (cur, conn, status):
        for _, olympiad in olympiads.iterrows():
            timestamp = dt.datetime.timestamp(dt.datetime.now())
            sql = "SELECT id FROM  olympiads_status WHERE id = %s AND is_active = 0"
            cur.execute(sql, [olympiad['id']])
            if cur.fetchone():
                sql = "UPDATE olympiads_status SET is_active = 1 WHERE id = %s"
                cur.execute(sql, [olympiad['id']])
            else:
                sql = "INSERT INTO olympiads_status (user_id, olympiad_id, status_code, stage, action_timestamp)" \
                      "VALUES (%s, %s, %s, %s, %s)"
                status_code = 0 if current_olympiads[current_olympiads['id'] == olympiad['id']]['pre_registration'].item()\
                    else 1
                cur.execute(sql, [user_id, olympiad['id'], status_code, olympiad['stage'], timestamp])
        conn.commit()
    return status.status


def set_registration(olympiad_id, user_id, stage):
    """
    It sets the status of the registration of a user to a particular olympiad to 1

    :param olympiad_id: the id of the olympiad
    :param user_id: the user's id
    :param stage: 1 - registration, 2 - qualification, 3 - final
    :return: status.status
    """
    with database() as (cur, conn, status):
        timestamp = dt.datetime.timestamp(dt.datetime.now())
        sql = "UPDATE olympiads_status SET status_code = %s, action_timestamp = %s" \
              " WHERE olympiad_id = %s AND user_id = %s AND stage = %s"
        cur.execute(sql, [1, timestamp, olympiad_id, user_id, stage])
        conn.commit()
    return status.status


def set_execution(olympiad_id, user_id, stage):
    """
    It sets the status of the execution of the olympiad to "executing"

    :param olympiad_id: the id of the olympiad
    :param user_id: the user's id
    :param stage: 1 - registration, 2 - execution, 3 - results
    :return: status.status
    """
    with database() as (cur, conn, status):
        timestamp = dt.datetime.timestamp(dt.datetime.now())
        sql = "UPDATE olympiads_status SET status_code = %s, action_timestamp = %s" \
              " WHERE olympiad_id = %s AND user_id = %s AND stage = %s"
        cur.execute(sql, [2, timestamp, olympiad_id, user_id, stage])
        conn.commit()
    return status.status


def set_missed(olympiads: DataFrame):
    """
    It sets the status of all olympiads in the given dataframe to -1

    :param olympiads: DataFrame
    :type olympiads: DataFrame
    :return: status.status
    """
    with database() as (cur, conn, status):
        for _, olympiad in olympiads.iterrows():
            sql = "UPDATE olympiads_status SET status_code = %s WHERE olympiad_id = %s AND stage = %s"
            cur.execute(sql, [-1, olympiad['id'], olympiad['stage']])
        conn.commit()
    return status.status


def set_inactive(inactive_olympiads):
    """
    It sets the is_active column of the olympiads table to 0 for all olympiads in the inactive_olympiads dataframe, and then
    sets the is_active column of the olympiads_status table to 0 for all olympiads in the inactive_olympiads dataframe

    :param inactive_olympiads: a dataframe with columns id, stage, and is_active
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        for _, olympiad in inactive_olympiads.iterrows():
            sql = "UPDATE olympiads SET is_active = 0 WHERE id = %s RETURNING stage"
            cur.execute(sql, [olympiad['id']])
            stage = cur.fetchone()[0]
            sql = "UPDATE olympiads_status SET is_active = 0 WHERE id = %s AND stage = %s"
            cur.execute(sql, [olympiad['id'], stage])
        conn.commit()
    return status.status


def set_keys(keys: DataFrame, keys_count: dict):
    """
    It takes a dataframe of keys and a dictionary of olympiad_id:keys_count and inserts the keys into the database and
    updates the keys_count for each olympiad

    :param keys: a DataFrame with columns 'olympiad_id' and 'key'
    :type keys: DataFrame
    :param keys_count: a dictionary of olympiad_id: keys_count
    :type keys_count: dict
    :return: status.status
    """
    with database() as (cur, conn, status):
        for _, key in keys.iterrows():
            sql = "INSERT INTO keys (olympiad_id, key) VALUES (%s, %s)"
            cur.execute(sql, [key['olympiad_id'], key['key']])
        for olympiad_id, count in keys_count.items():
            sql = "UPDATE olympiads SET keys_count = %s WHERE id = %s"
            cur.execute(sql, [count, int(olympiad_id)])
        conn.commit()
    return status.status


def add_notifications(notifications: DataFrame):
    """
    It takes a dataframe of notifications and adds them to the database

    :param notifications: DataFrame
    :type notifications: DataFrame
    :return: status.status
    """
    with database() as (cur, conn, status):
        for _, row in notifications.iterrows():
            sql = "INSERT INTO notifications (user_id, olympiad_id, notification_message, notification_type)" \
                  " VALUES (%s, %s, %s, %s)"
            cur.execute(sql, [row['user_id'], row['olympiad_id'], row['message'], row['type']])
        conn.commit()
    return status.status


def clean_notifications():
    """
    It deletes all the rows in the notifications table
    """
    with database() as (cur, conn, status):
        sql = "DELETE from notifications"
        cur.execute(sql)
        conn.commit()


def add_question(question: Series):
    """
    > This function takes a question as a parameter and inserts it into the database

    :param question: Series
    :type question: Series
    :return: The id of the question that was just added to the database.
    """
    with database() as (cur, conn, status):
        date = dt.date.today()
        sql = "INSERT INTO questions (from_user, question, user_message_id, question_date)" \
              " VALUES (%s, %s, %s, %s) RETURNING id"
        cur.execute(sql, [question['user_id'], question['question'], question['user_message_id'], date])
        res = cur.fetchone()
        conn.commit()
    return res[0], status


def add_questions_admin_message_id(questions):
    """
    Он берет фрейм данных вопросов и обновляет столбец admin_message_id в базе данных.

    :param questions: датафрейм вопросов
    :return: Статус подключения к базе данных.
    """
    with database() as (cur, conn, status):
        for _, question in questions.iterrows():
            sql = "UPDATE questions SET admin_message_id = %s WHERE id = %s"
            cur.execute(sql, [question['admin_message_id'], question['id']])
        conn.commit()
    return status.status


def add_question_answer(question_id, answer, admin_id):
    """
    It updates the question with the given id with the given answer, admin_id, admin_message_id, and answer_date

    :param question_id: The id of the question that was answered
    :param answer: The answer to the question
    :param admin_id: The id of the admin who answered the question
    :param admin_message_id: The message id of the message that the admin sent to the user
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        date = dt.date.today()
        sql = "UPDATE questions SET answer = %s, to_admin = %s, answer_date = %s WHERE id = %s"
        cur.execute(sql, [answer, admin_id, date, question_id])
        conn.commit()
    return status.status


def add_google_doc_row(user_id, file_type):
    """
    This function adds a row to the google_docs table

    :param user_id: The user's ID
    :param file_type: The type of file you want to create. This can be one of the following:
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "INSERT INTO google_docs (user_id, file_type) VALUES (%s, %s)"
        cur.execute(sql, [user_id, file_type])
        conn.commit()
    return status.status


def add_google_doc_url(user_id, file_type, url):
    """
    Эта функция обновляет URL-адрес документа Google для пользователя.

    :param user_id: Идентификатор пользователя
    :param file_type:
    :param url: адрес гугл документа
    """
    with database() as (cur, conn, status):
        sql = "UPDATE google_docs SET url = %s WHERE user_id = %s AND file_type = %s"
        cur.execute(sql, [url, user_id, file_type])
        conn.commit()
    return status.status


def set_updated_google_doc(user_id, file_type):
    """
    This function sets the is_changed column of the google_docs table to 0 for the row that matches the user_id and
    file_type passed in

    :param user_id: The user's id
    :param file_type: The type of file you want to update. This can be either "resume" or "cover_letter"
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE google_docs SET is_changed = 0 WHERE user_id = %s AND file_type = %s"
        cur.execute(sql, [user_id, file_type])
        conn.commit()
    return status.status


def add_excel_doc_row(user_id, file_type):
    """
    It takes a user_id and a file_type and inserts them into the excel_docs table

    :param user_id: The user's id
    :param file_type: This is the type of file that the user is uploading. It can be either "income" or "expense"
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "INSERT INTO excel_docs (user_id, file_type) VALUES (%s, %s)"
        cur.execute(sql, [user_id, file_type])
        conn.commit()
    return status.status


def set_excel_doc_id(user_id, file_type, file_id=''):
    """
    It updates the `file_id` and `is_changed` columns of the `excel_docs` table for the row that matches the `user_id` and
    `file_type` parameters

    :param user_id: The user's ID
    :param file_type: The type of file you want to set. This can be 'main', 'backup', or 'temp'
    :param file_id: the id of the file in the google drive
    :return: The status of the database connection.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE excel_docs SET file_id = %s, is_changed = 0 WHERE file_type = %s AND user_id = %s"
        cur.execute(sql, [file_id, file_type, user_id])
        conn.commit()
    return status.status


def change_users_files(user_id=None, file_types=None):
    """
    Он изменяет столбец is_changed таблиц excel_docs и google_docs на 1 для всех файлов заданных типов файлов, которые
    связаны с данным user_id или любым пользователем, который связан с той же оценкой, что и данный user_id.

    :param user_id: Идентификатор пользователя, который вносит изменения
    :param file_types: список типов файлов, которые вы хотите изменить
    :return: Статус подключения к базе данных.
    """
    with database() as (cur, conn, status):
        if user_id is not None:
            sql = "UPDATE excel_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND user_id = ANY(" \
                  "SELECT id FROM users WHERE is_admin = 2 AND id = ANY(SELECT user_id FROM user_refer_grade WHERE" \
                  " grade_id =ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s)))"
            cur.execute(sql, [file_types, user_id])

            sql = "UPDATE google_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND user_id = ANY(" \
                  "SELECT id FROM users WHERE is_admin = 2 AND id = ANY(SELECT user_id FROM user_refer_grade WHERE" \
                  " grade_id =ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s)))"
            cur.execute(sql, [file_types, user_id])

        sql = "UPDATE excel_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND" \
              " user_id = ANY(SELECT id FROM users WHERE is_admin = 3)"
        cur.execute(sql, [file_types])
        sql = "UPDATE google_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND" \
              " user_id = ANY(SELECT id FROM users WHERE is_admin = 3)"
        cur.execute(sql, [file_types])
        conn.commit()
    return status.status


def change_teachers_files(user_id, file_types, subject_id):
    with database() as (cur, conn, status):
        sql = "UPDATE google_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND" \
              " user_id = ANY(SELECT user_id FROM teaching" \
              " WHERE grade_id = ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s) AND subject_id = %s)"
        cur.execute(sql, [file_types, user_id, subject_id])
        sql = "UPDATE excel_docs SET is_changed = 1 WHERE file_type = ANY(%s) AND" \
              " user_id = ANY(SELECT user_id FROM teaching" \
              " WHERE grade_id = ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s) AND subject_id = %s)"
        cur.execute(sql, [file_types, user_id, subject_id])
        conn.commit()
    return status.status


def set_common_file_data(file_type, file_data):
    """
    It updates the file data and is_changed value of the file_type specified

    :param file_type: The type of file you want to set. This can be one of the following:
    :param file_data: The file data to be stored in the database
    :return: The status of the database operation.
    """
    with database() as (cur, conn, status):
        sql = "UPDATE templates_and_examples SET file_data = %s, is_changed = 0 WHERE file_type = %s"
        cur.execute(sql, [file_data, file_type])
        conn.commit()
    return status.status


def change_common_files(file_types):
    """
    It changes the is_changed column in the templates_and_examples table to 1 for all rows where the file_type column
    matches the file_type argument

    :param file_types: a list of file types to change
    :return: The status of the database.
    """
    with database() as (cur, conn, status):
        for file_type in file_types:
            sql = "UPDATE templates_and_examples SET is_changed = 1 WHERE file_type = %s"
            cur.execute(sql, [file_type])
        conn.commit()
    return status.status
