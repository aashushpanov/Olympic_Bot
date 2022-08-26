from .connect import database

import pandas as pd


def get_access(user_id: int) -> object:
    """
    Получает уровень доступа пользователя из базы данных

    :param user_id: Идентификатор пользователя
    :type user_id: int
    :return: Уровень доступа пользователя.
    """
    with database() as (cur, conn, status):
        sql = "SELECT is_admin FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        result = cur.fetchone()
    return result[0] if result else 0


async def is_exist(user_id):
    """
    Он проверяет, существует ли пользователь в базе данных

    :param user_id: Идентификатор пользователя
    :return: 1 если результат иначе 0
    """
    result = 0
    with database() as (cur, conn, status):
        sql = "SELECT f_name FROM users WHERE id = %s AND is_active = 1"
        cur.execute(sql, [user_id])
        result = cur.fetchone()
    return 1 if result else 0


async def is_inactive(user_id):
    """
    Возвращает 1, если пользователь неактивен, 0, если пользователь активен.

    :param user_id: Идентификатор пользователя
    :return: 1 если пользователь активен, 0 если пользователь неактивен
    """
    result = 0
    with database() as (cur, conn, status):
        sql = "SELECT f_name FROM users WHERE id = %s AND is_active = 0"
        cur.execute(sql, [user_id])
        result = cur.fetchone()
    return 1 if result else 0


def get_tracked_olympiads(user_id, with_inactive=False):
    with database() as (cur, conn, status):
        if with_inactive:
            sql = "SELECT olympiad_id, status_code, result_code, stage, key_id, action_timestamp" \
                  " FROM olympiads_status WHERE user_id = %s"
        else:
            sql = "SELECT olympiad_id, status_code, result_code, stage, key_id, action_timestamp" \
                  " FROM olympiads_status WHERE user_id = %s AND is_active = 1"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['olympiad_id', 'status_code', 'result_code',
                                          'stage', 'key_id', 'action_timestamp'])
        data = data.astype({'stage': 'int32'})
    return data


def get_olympiads_by_status(user_id, status_code):
    """
    > Получить olympiad_id, stage и key_id для всех олимпиад, которые имеют status_code из status_code для данного user_id

    :param user_id: идентификатор пользователя
    :param status_code:
    :return: Фрейм данных с olympiad_id, stage и key_id олимпиад, для которых у пользователя есть данный status_code.
    """
    with database() as (cur, conn, status):
        sql = "SELECT olympiad_id, stage, key_id FROM olympiads_status WHERE user_id = %s AND status_code = %s"
        cur.execute(sql, [user_id, status_code])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['olympiad_id', 'stage', 'key_id'])
        data = data.astype({'stage': 'int32'})
    return data


def get_olympiad_status(user_id, olympiad_id, stage):
    """
    Он возвращает серию панд с кодом состояния, этапом и идентификатором ключа статуса олимпиады пользователя.

    :param user_id: Идентификатор пользователя
    :param olympiad_id: Идентификатор олимпиады
    :param stage: этап олимпиады
    :return: Серия с кодом состояния, этапом и key_id пользователя.
    """
    with database() as (cur, conn, status):
        sql = "SELECT status_code, stage, key_id, is_active FROM  olympiads_status WHERE olympiad_id = %s" \
              " AND user_id = %s AND stage = %s"
        cur.execute(sql, [olympiad_id, user_id, stage])
        res = cur.fetchone()
        data = pd.Series(res, index=['status_code', 'stage', 'key_id', 'is_active'])
    return data


def get_key_by_id(key_id):
    """
    Он получает ключ из базы данных

    :param key_id: ID ключа, который вы хотите получить
    :return: Ключ возвращается.
    """
    with database() as (cur, conn, status):
        sql = "SELECT key FROM keys WHERE id = %s"
        cur.execute(sql, [int(key_id)])
        key = cur.fetchone()[0]
    return key


def get_all_olympiads_status(user_id=None, teaching=False):
    columns = ['olympiad_id', 'user_id', 'stage', 'key', 'result_code', 'status_code', 'action_timestamp']
    with database() as (cur, conn, status):
        if user_id is None:
            sql = "SELECT olympiads_status.olympiad_id, user_id, stage, k.key, result_code, status_code, action_timestamp" \
                  " FROM olympiads_status LEFT JOIN keys k on k.id = olympiads_status.key_id"
            cur.execute(sql)
        else:
            if teaching:
                sql = "SELECT olympiads_status.olympiad_id, user_id, stage, k.key, result_code, status_code, action_timestamp" \
                      " FROM olympiads_status LEFT JOIN keys k on k.id = olympiads_status.key_id" \
                      " WHERE user_id = ANY(SELECT user_id FROM user_refer_grade" \
                      " WHERE grade_id = ANY(SELECT grade_id FROM teaching WHERE user_id = %s)) AND" \
                      " olympiad_id = ANY(SELECT olympiad_id FROM olympiads WHERE" \
                      " subject_id = ANY(SELECT subject_id FROM teaching WHERE user_id = %s))"
            else:
                sql = "SELECT olympiads_status.olympiad_id, user_id, stage, k.key, result_code, status_code, action_timestamp" \
                      " FROM olympiads_status LEFT JOIN keys k on k.id = olympiads_status.key_id" \
                      " WHERE user_id = ANY(SELECT user_id FROM user_refer_grade" \
                      " WHERE grade_id = ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s))" \
                      " AND user_id = ANY(SELECT user_id FROM users WHERE is_admin = 0) "
            cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=columns)
        data = data.astype({'stage': 'int32'})
    return data


def get_user(user_id):
    """
    Он получает данные пользователя из базы данных и возвращает их в виде серии панд.

    :param user_id: Идентификатор пользователя
    :return: Серия панд с информацией о пользователе.
    """
    with database() as (cur, conn, status):
        sql = "SELECT f_name, l_name, notification_time, email, is_active, reg_date, last_active_date," \
              " to_google_sheets, grades.grade_num, grades.grade_literal" \
              " FROM users LEFT JOIN user_refer_grade on users.id = user_refer_grade.user_id" \
              " LEFT JOIN grades on grades.id = user_refer_grade.grade_id WHERE users.id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['f_name', 'l_name', 'notify_time', 'email', 'is_active', 'reg_date',
                                     'last_active_date', 'to_google_sheets', 'grade', 'literal'],
                         dtype='object')
        sql = "SELECT subject_id FROM interests WHERE user_id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data['interest'] = res[0] if res else []
    return data


def get_users(user_id=None):
    """
    Он возвращает кадр данных всех пользователей в базе данных,
    кроме админов

    :param user_id: Идентификатор пользователя, который запрашивает данные
    :return: Фрейм данных с информацией о пользователях
    """
    columns = ['user_id', 'f_name', 'l_name', 'reg_date', 'is_active', 'last_active_date',
               'grade', 'literal', 'interest']
    with database() as (cur, conn, status):
        if user_id is None:
            sql = "SELECT users.id, f_name, l_name, reg_date, is_active, last_active_date, max(grade_num), max(grade_literal)," \
                  " array_agg(interests.subject_id) as interest" \
                  " FROM users LEFT JOIN user_refer_grade on users.id = user_refer_grade.user_id" \
                  " LEFT JOIN grades on grades.id = user_refer_grade.grade_id" \
                  " RIGHT JOIN interests on users.id = interests.user_id WHERE is_admin = 0 group by users.id"
            cur.execute(sql)
            res = cur.fetchall()
        else:
            sql = "SELECT users.id, f_name, l_name, reg_date, is_active, last_active_date, max(grade_num), max(grade_literal)," \
                  " array_agg(interests.subject_id) as interest" \
                  " FROM users LEFT JOIN user_refer_grade on users.id = user_refer_grade.user_id" \
                  " LEFT JOIN grades on grades.id = user_refer_grade.grade_id" \
                  " FULL JOIN interests on users.id = interests.user_id" \
                  " WHERE users.id = ANY(SELECT user_id FROM user_refer_grade" \
                  " WHERE grade_id = ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s))" \
                  " AND users.id = ANY(SELECT id FROM users WHERE is_admin = 0) group by users.id"
            cur.execute(sql, [user_id])
            res = cur.fetchall()
        data = pd.DataFrame(res, columns=columns)
    return data


def get_admins():
    """
    Он подключается к базе данных, выполняет запрос и возвращает результаты в виде кадра данных pandas.
    :return: Фрейм данных с admin_id, именем и фамилией всех администраторов.
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, f_name, l_name FROM users WHERE is_admin = 3"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['admin_id', 'f_name', 'l_name'])
    return data


def get_class_managers():
    """
    Он возвращает кадр данных всех руководителей классов в базе данных с их именами и фамилиями, а также классами, которыми
    они управляют.
    :return: Фрейм данных с admin_id, именем, фамилией и классами всех руководителей классов.
    """
    with database() as (cur, conn, status):
        sql = "SELECT users.id, f_name, l_name, string_agg(grades.grade_num || ' ' || grades.grade_literal, ',')" \
              " FROM users RIGHT JOIN user_refer_grade on users.id = user_refer_grade.user_id" \
              " LEFT JOIN grades on user_refer_grade.grade_id = grades.id WHERE is_admin = 2 group by users.id"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['admin_id', 'f_name', 'l_name', 'grades'])
    return data


def get_class_manager_by_grade(grade, literal):
    """
    Возвращает имя, фамилию и идентификатор классного руководителя данного класса.

    :param grade: номер класса
    :param literal: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
    :return: Серия admin_id, f_name и l_name классного руководителя данного класса.
    """
    with database() as (cur, conn, status):
        sql = "SELECT users.id, f_name, l_name FROM users" \
              " WHERE id = ANY(SELECT user_id FROM user_refer_grade" \
              " LEFT JOIN grades on user_refer_grade.grade_id = grades.id" \
              " WHERE grade_num = %s AND grade_literal = %s) AND is_admin = 2"
        cur.execute(sql, [grade, literal])
        res = cur.fetchone()
    if res is None:
        data = pd.Series([], dtype='object')
    else:
        data = pd.Series(res, index=['admin_id', 'f_name', 'l_name'])
    return data


def get_class_managers_grades(cm_id):
    """
    Эта функция возвращает кадр данных всех оценок, за которые отвечает классный руководитель.

    :param cm_id: id руководителя класса
    :return: Фрейм данных сgrade_id,grade_num иgrade_literal оценок, с которыми связан менеджер классов.
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, grade_num, grade_literal FROM grades WHERE id = ANY(SELECT grade_id FROM user_refer_grade WHERE user_id = %s)"
        cur.execute(sql, [cm_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['grade_id', 'grade_num', 'grade_literal'])
    return data


def get_cm_keys_limit(cm_id, olympiad_name, grade_num):
    with database() as (cur, conn, status):
        sql = "SELECT id FROM olympiads WHERE name = %s AND grade = %s"
        cur.execute(sql, [olympiad_name, grade_num])
        olympiad_id = cur.fetchone()[0]
        sql = "SELECT key_remains FROM cm_key_limits WHERE user_id = %s AND olympiad_id = %s"
        cur.execute(sql, [cm_id, olympiad_id])
        res_1 = cur.fetchone()
        sql = "SELECT keys_count FROM olympiads WHERE id = %s"
        cur.execute(sql, [olympiad_id])
        res_2 = cur.fetchone()
        if res_1 and res_2:
            res = min(res_1[0], res_2[0])
        else:
            res = 0
    return res, olympiad_id


def get_cm_keys(cm_id):
    with database() as (cur, conn, status):
        sql = "SELECT name, grade, key, label FROM cm_keys LEFT JOIN keys ON keys.id = cm_keys.key_id" \
              " LEFT JOIN olympiads ON keys.olympiad_id = olympiads.id WHERE user_id = %s"
        cur.execute(sql, [cm_id])
        res = cur.fetchall()
        columns = ['olympiad_name', 'grade', 'key', 'label']
        if res:
            data = pd.DataFrame(res, columns=columns)
        else:
            data = pd.DataFrame(columns=columns)
    return data


def get_all_cm_keys():
    with database() as (cur, conn, status):
        sql = "SELECT f_name, l_name, name, grade, key, label FROM cm_keys LEFT JOIN keys ON keys.id = cm_keys.key_id" \
              " LEFT JOIN olympiads ON keys.olympiad_id = olympiads.id LEFT JOIN users ON users.id = cm_keys.user_id "
        cur.execute(sql)
        res = cur.fetchall()
        if res:
            data = pd.DataFrame(res, columns=['f_name', 'l_name', 'olympiad_name', 'grade', 'key', 'label'])
        else:
            data = pd.DataFrame()
    return data


def get_admin(user_id):
    """
    > Эта функция принимает user_id и возвращает серию pandas с именем пользователя, фамилией, адресом электронной почты и
    тем, хотят ли они отправлять свои данные в Google Таблицы.

    :param user_id: идентификатор пользователя
    :return: Серия pandas с именем, фамилией, адресом электронной почты и значением to_google_sheets пользователя с заданным
    user_id.
    """
    with database() as (cur, conn, status):
        sql = "SELECT f_name, l_name, email, to_google_sheets FROM users WHERE id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['f_name', 'l_name', 'email', 'to_google_sheets'])
    return data


def get_users_by_notification_time(time):
    """
    «Получить всех пользователей, у которых время уведомления меньше или равно заданному времени».

    Функция немного сложнее, но суть в этом.

    :param time: Время для проверки
    :return: Список идентификаторов пользователей
    """
    with database() as (cur, conn, status):
        sql = "SELECT id FROM users WHERE notification_time <= %s"
        cur.execute(sql, [time])
        res = [x[0] for x in cur.fetchall()]
    return res


def get_subjects():
    """
    Он подключается к базе данных, выполняет запрос и возвращает результаты в виде кадра данных pandas.
    :return: Фрейм данных с идентификатором столбца, кодом, именем и разделом.
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, code, name, section FROM subjects"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['id', 'code', 'name', 'section'])
    return data


def get_subject(subject_id):
    with database() as (cur, conn, status):
        sql = "SELECT id, code, name, section FROM subjects WHERE id = %s"
        cur.execute(sql, [subject_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['id', 'code', 'name', 'section'])
    return data


def get_olympiads():
    """
    Он получает все олимпиады из базы данных и возвращает их в виде кадра данных pandas.
    :return: Датафрейм со всеми олимпиадами в базе данных.
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, name, code, subject_id, stage, start_date, end_date, is_active, grade, key_needed," \
              " pre_registration, urls, keys_count FROM olympiads"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['id', 'name', 'code', 'subject_id', 'stage', 'start_date', 'end_date',
                                          'is_active', 'grade', 'key_needed', 'pre_registration', 'urls', 'keys_count'])
        data['stage'] = data['stage'].fillna(-1)
        data['keys_count'] = data['keys_count'].fillna(0)
        data[['key_needed', 'pre_registration']] = data[['key_needed', 'pre_registration']].fillna(0)
        data = data.astype({'stage': 'int32', 'grade': 'int32', 'pre_registration': 'int32',
                            'key_needed': 'int32', 'keys_count': 'int32'})
    return data


def get_olympiad(olympiad_id):
    """
    Он получает данные олимпиады из базы данных

    :param olympiad_id: Идентификатор олимпиады
    :return: Ряд данных из таблицы олимпиад.
    """
    with database() as (cur, conn, status):
        sql = "SELECT name, subject_id, stage, start_date, end_date, is_active, grade, key_needed," \
              " pre_registration, urls, keys_count FROM olympiads WHERE id = %s"
        cur.execute(sql, [olympiad_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['name', 'subject_id', 'stage', 'start_date', 'end_date', 'is_active',
                                     'grade', 'key_needed', 'pre_registration', 'urls', 'keys_count'])
    return data


def get_common_file(file_type):
    """
    Он принимает тип файла в качестве аргумента и возвращает серию pandas, содержащую данные файла и независимо от того,
    были ли они изменены.

    :param file_type: Тип файла, который вы хотите получить
    :return: Серия pandas со столбцами file_data и is_changed из таблицы templates_and_examples.
    """
    with database() as (cur, conn, status):
        sql = "SELECT file_data, is_changed FROM templates_and_examples WHERE file_type = %s"
        cur.execute(sql, [file_type])
        res = cur.fetchone()
        data = pd.Series(res, index=['file_data', 'is_changed'])
    return data


def get_key_from_db(user_id, olympiad_id, stage):
    """
    Он получает ключ из базы данных, обновляет базу данных и возвращает ключ

    :param user_id: идентификатор пользователя
    :param olympiad_id: идентификатор олимпиады
    :param stage: 1 - регистрация, 2 - первый этап, 3 - второй этап, 4 - третий этап
    :return: ключ, статус.статус
    """
    key = ""
    with database() as (cur, conn, status):
        sql = "SELECT key, id FROM keys WHERE olympiad_id = %s AND id =" \
              " (SELECT MAX(id) FROM keys WHERE olympiad_id = %s AND is_taken = 0)"
        cur.execute(sql, [olympiad_id, olympiad_id])
        res = cur.fetchone()
        key = res[0]
        key_id = res[1]
        sql = "UPDATE olympiads_status SET key_id = %s WHERE user_id = %s AND stage = %s AND olympiad_id = %s"
        cur.execute(sql, [key_id, user_id, stage, olympiad_id])
        sql = "UPDATE olympiads SET keys_count = keys_count - 1 WHERE id = %s"
        cur.execute(sql, [olympiad_id])
        sql = "UPDATE keys SET is_taken = 1 WHERE olympiad_id = %s AND id = %s"
        cur.execute(sql, [olympiad_id, key_id])
        conn.commit()
    return key, status.status


def get_notifications(users_id):
    """
    Он удаляет все уведомления для списка пользователей и возвращает удаленные уведомления.

    :param users_id: список идентификаторов пользователей
    :return: Фрейм данных с user_id, olympiad_id,notification_messageиnotification_type удаленных уведомлений.
    """
    with database() as (cur, conn, status):
        sql = "DELETE FROM notifications WHERE user_id = ANY(%s)" \
              " RETURNING user_id, olympiad_id, notification_message, notification_type"
        cur.execute(sql, [users_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['user_id', 'olympiad_id', 'notification_message', 'notification_type'])
        conn.commit()
    return data


def get_questions_counts():
    """
    Возвращает количество оставшихся без ответа вопросов в базе данных
    :return: Количество вопросов, на которые нет ответов.
    """
    with database() as (cur, conn, status):
        sql = "SELECT count(id) FROM questions WHERE answer  = ''"
        cur.execute(sql)
        res = cur.fetchone()
    return res[0]


def get_new_questions():
    """
    Он получает все вопросы из базы данных, на которые еще не ответили
    :return: Фрейм данных с идентификатором столбцов, user_id, question, user_message_id, admin_message_id
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, from_user, question, user_message_id, admin_message_id FROM questions WHERE answer = '' "
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['id', 'user_id', 'question', 'user_message_id', 'admin_message_id'])
    return data


def get_question(question_id):
    """
    Он получает вопрос из базы данных

    :param question_id: id вопроса, который вы хотите получить
    :return: Серия pandas с данными из базы данных.
    """
    with database() as (cur, conn, status):
        sql = "SELECT from_user, question, user_message_id, admin_message_id, answer, to_admin," \
              " question_date, answer_date FROM questions WHERE id = %s "
        cur.execute(sql, [question_id])
        res = cur.fetchone()
        data = pd.Series(res, index=['from_user', 'question', 'user_message_id', 'admin_message_id',
                                     'answer', 'to_admin', 'question_date', 'answer_date'])
    return data


def get_answers():
    """
    Он получает все ответы из базы данных
    :return: Датафрейм с ответами на вопросы.
    """
    with database() as (cur, conn, status):
        sql = "SELECT id, from_user, question, user_message_id, admin_message_id, answer, to_admin," \
              " question_date, answer_date FROM questions"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['question_id', 'from_user', 'question', 'user_message_id', 'admin_message_id',
                                          'answer', 'to_admin', 'question_date', 'answer_date'])
    return data


def get_user_google_files(user_id):
    """
    Он принимает user_id в качестве входных данных и возвращает кадр данных pandas со столбцами file_type, url и is_changed
    из таблицы google_sheets.

    :param user_id: Идентификатор пользователя
    :return: Фрейм данных со столбцами file_type, url и is_changed.
    """
    with database() as (cur, conn, status):
        sql = "SELECT file_type, url, is_changed FROM google_docs WHERE user_id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['file_type', 'url', 'is_changed'])
    return data


def get_user_google_file(user_id, file_type):
    """
    Эта функция принимает user_id и file_type и возвращает фрейм данных со столбцами file_type, url и is_changed.

    :param user_id: ID пользователя
    :param file_type: Тип файла, который вы хотите получить
    :return: Фрейм данных со столбцами file_type, url и is_changed.
    """
    with database() as (cur, conn, status):
        sql = "SELECT file_type, url, is_changed FROM google_docs WHERE user_id = %s AND file_type = %s"
        cur.execute(sql, [user_id, file_type])
        res = cur.fetchone()
        data = pd.Series(res, index=['file_type', 'url', 'is_changed'])
    return data


def get_user_excel_files(user_id):
    """
    Он принимает user_id в качестве входных данных и возвращает кадр данных pandas со столбцами file_type, url и is_changed.

    :param user_id: идентификатор пользователя
    :return: Фрейм данных со столбцами file_type, url и is_changed.
    """
    with database() as (cur, conn, status):
        sql = "SELECT file_type, file_id, is_changed FROM excel_docs WHERE user_id = %s"
        cur.execute(sql, [user_id])
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['file_type', 'url', 'is_changed'])
    return data


def get_user_excel_file(user_id, file_type):
    """
    > Эта функция принимает user_id и file_type и возвращает серию pandas со значениями file_type, url и is_changed.

    :param user_id: Идентификатор пользователя
    :param file_type: Тип файла, который вы хотите получить
    :return: Серия pandas со столбцами file_type, url и is_changed из таблицы google_sheets.
    """
    with database() as (cur, conn, status):
        sql = "SELECT file_type, is_changed FROM excel_docs WHERE user_id = %s AND file_type = %s"
        cur.execute(sql, [user_id, file_type])
        res = cur.fetchone()
        data = pd.Series(res, index=['file_type', 'file_id', 'is_changed'])
    return data


def get_changed_google_files():
    """
    Он возвращает кадр данных всех пользователей, которые изменили свои листы Google.
    :return: Фрейм данных с user_id и file_type всех измененных листов Google.
    """
    with database() as (cur, conn, status):
        sql = "SELECT user_id, file_type FROM google_docs WHERE is_changed = 1"
        cur.execute(sql)
        res = cur.fetchall()
        data = pd.DataFrame(res, columns=['user_id', 'file_type'])
    return data
