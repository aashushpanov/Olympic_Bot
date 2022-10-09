import os

import pandas as pd
import datetime as dt

from data.aliases import status_codes
from utils.db.get import get_olympiads, get_subjects, get_users, get_all_olympiads_status, get_answers, \
    get_class_managers, get_admins, get_cm_keys, get_all_cm_keys


file_dir = os.path.join(os.getcwd(), 'data', 'files', 'to_send')


def make_users_file(user_id=None):
    file_path = os.path.join(os.getcwd(), file_dir, 'users.xlsx')
    users = get_users(user_id)
    columns = ['Фамилия', 'Имя', 'Класс', 'Дата регистрации']
    users['grade_label'] = users['grade'].astype(str) + users['literal']
    users_file = users[['l_name', 'f_name', 'grade_label', 'reg_date']]
    # users_file['reg_date'] = users_file['reg_date'].apply(lambda x: dt.datetime.fromordinal(x).date())
    users_file.columns = columns
    users_file.to_excel(file_path, index=False)
    return file_path, users_file


def make_class_managers_file():
    file_path = os.path.join(os.getcwd(), file_dir, 'class_managers.xlsx')
    class_managers = get_class_managers()
    columns = ['Фамилия', 'Имя', 'Классы', 'Дата регистрации']
    class_managers_file = pd.DataFrame(columns=columns)
    for _, row in class_managers.iterrows():
        grade_list = row['grades'].replace(' ', '')
        class_manager = pd.DataFrame([[row['l_name'], row['f_name'], ', '.join(grade_list), row['reg_date']]], columns=columns)
        class_managers_file = pd.concat([class_managers_file, class_manager], axis=0)
    class_managers_file.to_excel(file_path, index=False)
    return file_path, class_managers_file


def make_olympiads_with_dates_file():
    file_path = os.path.join(os.getcwd(), file_dir, 'all_olympiads.xlsx')
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('id'), on='subject_id', rsuffix='_subject')
    olympiads_groups = olympiads.groupby(['name', 'start_date', 'end_date'])
    columns = ['Название', 'Предмет', 'Этап', 'Дата начала', 'Дата окончания', 'мл. класс', 'ст. класс',
               'Активна', 'Ключ', 'Предварительная регистрация', 'Ссылка на сайт олимпиады', 'Ссылка на регистрацию']
    olympiads_file = pd.DataFrame(columns=columns)
    for name, group in olympiads_groups:
        min_grade = group['grade'].min()
        max_grade = group['grade'].max()
        urls = group['urls'].iloc[0]
        site_url = urls.get('site_url')
        reg_url = urls.get('reg_url')
        subject_name = group['name_subject'].iloc[0]
        active = 'Да' if group['is_active'].iloc[0] else 'Нет'
        key_needed = 'Да' if group['key_needed'].iloc[0] else 'Нет'
        pre_registration = 'Да' if group['pre_registration'].iloc[0] else 'Нет'
        stage = group['stage'].iloc[0]
        start_date = name[1].strftime('%d.%m.%y')
        end_date = name[2].strftime('%d.%m.%y')
        olympiad = pd.DataFrame([[name[0], subject_name, stage, start_date, end_date, min_grade, max_grade, active,
                                  key_needed, pre_registration, site_url, reg_url]], columns=columns)
        olympiads_file = pd.concat([olympiads_file, olympiad], axis=0)
        # olympiads_file.to_csv(file_path, index=False, sep=';')
    olympiads_file.to_excel(file_path, index=False)
    return file_path, olympiads_file


def make_olympiads_status_file(user_id=None, teaching=None):
    file_path = os.path.join(os.getcwd(), file_dir, 'status_file.xlsx')
    users = get_users()
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads_status = get_all_olympiads_status(user_id)
    olympiads_status = olympiads_status.join(olympiads.set_index('id'), on='olympiad_id', rsuffix='real')
    olympiads_status = olympiads_status.join(subjects.set_index('id'), on='subject_id', rsuffix='_subject')
    olympiads_status = olympiads_status.join(users.set_index('user_id'), on='user_id', rsuffix='user')
    columns = ['Имя', 'Фамилия', 'Класс', 'Олимпиада', 'Предмет', 'Ключ', 'Статус', 'Дата']
    status_file = pd.DataFrame(columns=columns)
    for _, olympiad_status in olympiads_status.iterrows():
        f_name = olympiad_status['f_name']
        l_name = olympiad_status['l_name']
        literal = olympiad_status['literal'] if olympiad_status['literal'] else ''
        grade = str(olympiad_status['grade']) + str(literal)
        olympiad_name = olympiad_status['name']
        subject = olympiad_status['name_subject']
        date = dt.datetime.fromtimestamp(olympiad_status['action_timestamp']).date()
        if teaching:
            key = "Взят" if olympiad_status['key'] else ""
        else:
            key = olympiad_status['key']
        status = status_codes.get(olympiad_status['status_code'], 'Не определен')
        new_olympiad_status = pd.DataFrame([[f_name, l_name, grade, olympiad_name, subject, key, status, date]],
                                           columns=columns)
        status_file = pd.concat([status_file, new_olympiad_status], axis=0)
    status_file.to_excel(file_path, index=False)
    return file_path, status_file


def make_answers_file():
    file_path = os.path.join(os.getcwd(), file_dir, 'answers_file.xlsx')
    answers = get_answers()
    admins = get_admins()
    answers = answers.join(admins.set_index('admin_id'), on='to_admin')
    columns = ['Номер вопроса', 'Вопрос', 'Дата вопроса', 'Ответ', 'Дата ответа', 'Дал ответ']
    answers_file = pd.DataFrame(columns=columns)
    for _, row in answers.iterrows():
        question_id = row['question_id']
        question = row['question']
        answer = row['answer']
        question_date = row['question_date']
        answer_date = row['answer_date']
        from_admin = '{} {}'.format(row['l_name'], row['f_name'])
        answer_row = pd.DataFrame([[question_id, question, question_date, answer, answer_date, from_admin]],
                                  columns=columns)
        answers_file = pd.concat([answers_file, answer_row], axis=0)
    answers_file.to_excel(file_path, index=False)
    return file_path, answers_file


def make_cm_key_file(cm_id):
    file_path = os.path.join(os.getcwd(), file_dir, 'cm_key_file.xlsx')
    columns = ['Олимпиада', 'Класс', 'Ключ', 'Метка']
    cm_key_file = get_cm_keys(cm_id)
    cm_key_file = cm_key_file.fillna('')
    cm_key_file.columns = columns
    cm_key_file.to_excel(file_path, index=False)
    return file_path, cm_key_file


def make_all_cm_key_file():
    file_path = os.path.join(os.getcwd(), file_dir, 'all_cm_key_file.xlsx')
    columns = ['Олимпиада', 'Класс', 'Ключ', 'Метка', 'ФИО']
    cm_key_file = get_all_cm_keys()
    cm_key_file['fio'] = cm_key_file.apply(lambda row: '{} {}'.format(row['l_name'], row['f_name']), axis=1)
    cm_key_file = cm_key_file.fillna('')
    cm_key_file = cm_key_file.drop(['l_name', 'f_name'], axis=1)
    cm_key_file.columns = columns
    cm_key_file.to_excel(file_path, index=False)
    return file_path, cm_key_file
