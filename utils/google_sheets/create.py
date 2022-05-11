import pandas as pd
import pygsheets

from utils.db.add import add_google_doc_row, add_google_doc_url, set_updated_google_doc
from utils.db.get import get_user_files, get_admin, get_changed_files, get_admins
from utils.files.data_files import make_users_file, make_olympiads_status_file, make_olympiads_with_dates_file, \
    make_class_managers_file, make_answers_file
from utils.files.templates import make_subjects_file

file_alias = {'users_file': 'Список учеников', 'status_file': 'Статус прохождения олимпиад',
              'subjects_file': 'Список предметов', 'olympiads_file': 'Список олимпиад',
              'class_managers_file': 'Список классных руководителей', 'answers_file': 'Список вопросов'}


def create_file(user_id, file_types: list):
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    for file_type in file_types:
        no = add_google_doc_row(user_id, file_type)
        name = file_alias.get(file_type, 'Файл')
        title = '{} #{}'.format(name, no)
        spread_sheet = client.create(title)
        add_google_doc_url(no, spread_sheet.url)
        user = get_admin(user_id)
        if user['email']:
            spread_sheet.share(user['email'])
        work_sheet = spread_sheet.sheet1
        file_format(work_sheet, file_type)


def user_files_update(user_id):
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    files = get_user_files(user_id)
    user = get_admin(user_id)
    for _, file in files.iterrows():
        update_file(client, file, user_id, user['grades'], user['literals'])


def update_all_files():
    changed_files = get_changed_files()
    admins = get_admins()
    changed_files = changed_files.join(admins.set_index('id'), on='user_id')
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    for file in changed_files.iterrows():
        update_file(client, file, file['user_id'], file['grades'], file['literals'])


def update_file(client, user_file, user_id, grades=None, literals=None):
    name = file_alias.get(user_file['file_type'], 'Файл')
    match user_file['file_type']:
        case 'users_file':
            _, data = make_users_file(grades, literals)
        case 'status_file':
            _, data = make_olympiads_status_file(grades, literals)
        case 'olympiads_file':
            _, data = make_olympiads_with_dates_file()
        case 'class_managers_file':
            _, data = make_class_managers_file()
        case 'answers_file':
            _, data = make_answers_file()
        case 'subjects_file':
            _, data = make_subjects_file()
        case _:
            data = pd.DataFrame()
    title = '{} #{}'.format(name, user_file['no'])
    try:
        spread_sheet = client.open(title)
    except pygsheets.exceptions.SpreadsheetNotFound:
        spread_sheet = client.create(title)
    work_sheet = spread_sheet.sheet1
    work_sheet.clear()
    work_sheet.set_dataframe(data, (1, 1))
    file_format(work_sheet, user_file['file_type'])
    set_updated_google_doc(user_id, user_file['file_type'])


def file_format(work_sheet, file_type):
    cell = pygsheets.cell.Cell('A1')
    cell.set_text_format('fontFamily', 'Montserrat')
    pygsheets.datarange.DataRange('A1', 'E1000', worksheet=work_sheet).apply_format(cell)
    cell.set_text_format('bold', True)
    cell.text_format['fontSize'] = 12
    cell.color = (0.8, 0.7, 0.3, 1)
    work_sheet.frozen_rows = 1
    work_sheet.adjust_column_width(start=1, end=12)
    match file_type:
        case 'users_file':
            pygsheets.datarange.DataRange('A1', 'C1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=3, pixel_size=60)
        case 'status_file':
            pygsheets.datarange.DataRange('A1', 'G1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=2, pixel_size=120)
            work_sheet.adjust_column_width(start=3, pixel_size=100)
            work_sheet.adjust_column_width(start=4, pixel_size=230)
            work_sheet.adjust_column_width(start=6, pixel_size=250)
            work_sheet.adjust_column_width(start=7, pixel_size=120)
        case 'olympiads_file':
            pygsheets.datarange.DataRange('A1', 'L1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=1, pixel_size=230)
            work_sheet.adjust_column_width(start=4, end=5, pixel_size=150)
        case 'class_managers_file':
            pygsheets.datarange.DataRange('A1', 'C1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=1, pixel_size=130)
            work_sheet.adjust_column_width(start=2, end=3, pixel_size=230)

        case 'answers_file':
            pygsheets.datarange.DataRange('A1', 'D1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=1, pixel_size=120)
        case 'subjects_file':
            pygsheets.datarange.DataRange('A1', 'C1', worksheet=work_sheet).apply_format(cell)


def bind_email(user_id):
    admin = get_admin(user_id)
    email = admin['email']
    files = get_user_files(user_id)
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    for _, file in files.iterrows():
        file_type = file['file_type']
        no = file['no']
        name = file_alias.get(file_type, 'Файл')
        title = '{} #{}'.format(name, no)
        spread_sheet = client.open(title)
        to_remove_permissions = []
        for user in spread_sheet.permissions:
            if user['role'] != 'owner':
                to_remove_permissions.append(user['emailAddress'])
        if to_remove_permissions:
            spread_sheet.remove_permission(to_remove_permissions)
        spread_sheet.share(email)
