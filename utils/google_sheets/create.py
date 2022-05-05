import pandas as pd
import pygsheets

from utils.db.add import add_google_doc_row, add_google_doc_url
from utils.db.get import get_user, get_user_files, get_class_manager
from utils.files.data_files import make_users_file, make_olympiads_status_file


def create_file(user_id, file_type):
    no = add_google_doc_row(user_id, file_type)
    if file_type == 'user_list':
        name = 'Список учеников'
    elif file_type == 'status_file':
        name = 'Статус олимпиад'
    else:
        name = 'Файл'
    title = '{} {}'.format(name, no)
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    spread_sheet = client.create(title)
    add_google_doc_url(no, spread_sheet.url)
    user = get_user(user_id)
    if user['email']:
        spread_sheet.share(user['email'])
    work_sheet = spread_sheet.sheet1
    file_format(work_sheet, file_type)


def update_file(user_id, user_file):
    class_manager = get_class_manager(user_id)
    grades = class_manager['grades']
    literals = class_manager['literals']
    match user_file['file_type']:
        case 'user_list':
            name = 'Список учеников'
            _, data = make_users_file(grades, literals)
        case 'status_file':
            name = 'Статус олимпиад'
            _, data = make_olympiads_status_file(grades, literals)
        case _:
            name = 'Файл'
            data = pd.DataFrame()
    title = '{} {}'.format(name, user_file['no'])
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    spread_sheet = client.open(title)
    work_sheet = spread_sheet.sheet1
    work_sheet.clear()
    work_sheet.set_dataframe(data, (1, 1))


def file_format(work_sheet, file_type):
    cell = pygsheets.cell.Cell('A1')
    cell.set_text_format('fontFamily', 'Montserrat')
    pygsheets.datarange.DataRange('A1', 'E1000', worksheet=work_sheet).apply_format(cell)
    cell.set_text_format('bold', True)
    cell.text_format['fontSize'] = 12
    cell.color = (0.8, 0.7, 0.3, 1)
    match file_type:
        case 'users_file':
            pygsheets.datarange.DataRange('A1', 'D1', worksheet=work_sheet).apply_format(cell)
        case 'status_file':
            pygsheets.datarange.DataRange('A1', 'G1', worksheet=work_sheet).apply_format(cell)


def bind_email(user_id):
    class_manager = get_class_manager(user_id)
    email = class_manager['email']
    files = get_user_files(user_id)
    client = pygsheets.authorize(service_file='././olympicbot1210-c81dc6c184cb.json')
    for _, file in files.iterrows():
        file_type = file['file_type']
        no = add_google_doc_row(user_id, file_type)
        if file_type == 'user_list':
            name = 'Список учеников'
        elif file_type == 'status_file':
            name = 'Статус олимпиад'
        else:
            name = 'Файл'
        title = '{} {}'.format(name, no)
        spread_sheet = client.open(title)
        to_remove_permissions = []
        for user in spread_sheet.permissions:
            if user['role'] != 'owner':
                to_remove_permissions.append(user['emailAddress'])
        spread_sheet.remove_permission(to_remove_permissions)
        spread_sheet.share(email)




