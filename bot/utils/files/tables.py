import pandas as pd
import pygsheets
import os
import asyncio

from googleapiclient.errors import HttpError

from data.aliases import file_alias
from data.config import GOOGLE_SERVICE_FILENAME
from loader import bot
from utils.db.add import add_google_doc_row, add_google_doc_url, set_updated_google_doc, add_excel_doc_row, \
    add_google_doc_rows_from_reserve, add_reserved_files_to_db
from utils.db.get import get_admin, get_changed_google_files, get_user_google_files, get_access
from utils.files.data_files import make_users_file, make_olympiads_status_file, make_olympiads_with_dates_file, \
    make_class_managers_file, make_answers_file, make_cm_key_file, make_all_cm_key_file
from utils.files.templates import make_subjects_file

GOOGLE_SERVICE_FILE = os.path.join(os.getcwd(), 'service_files', GOOGLE_SERVICE_FILENAME)


async def create_files(user_id, file_types: list, message):
    await create_google_file(user_id, file_types, message)
    await create_excel_file(user_id, file_types)


# def change_files(user_id, file_types):
#     change_google_docs(user_id, file_types)


async def create_google_file(user_id, file_types: list, message):
    status_1, file_type = add_google_doc_rows_from_reserve(user_id, file_types)
    if status_1:
        if file_type != 0:
            client = pygsheets.authorize(service_account_file=GOOGLE_SERVICE_FILE)
            for file_type in file_types[file_types.index(file_type):]:
                name = file_alias.get(file_type, 'Файл')
                title = '{} #{}'.format(name, user_id)
                spread_sheet = client.create(title)
                await asyncio.sleep(0.01)
                status_2 = add_google_doc_row(user_id, file_type, spread_sheet.url)
                if not status_2:
                    pass
                    # work_sheet = spread_sheet.sheet1
                    # file_format(work_sheet, file_type)
        user = get_admin(user_id)
        if user['email']:
            await bind_email(user_id, message)


async def create_excel_file(user_id, file_types: list):
    for file_type in file_types:
        await asyncio.sleep(0.01)
        add_excel_doc_row(user_id, file_type)


async def user_files_update(user_id):
    client = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    files = get_user_google_files(user_id)
    for _, file in files.iterrows():
        await asyncio.sleep(0.01)
        update_file(client, file, user_id)


def update_all_files():
    changed_files = get_changed_google_files()
    client = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    for _, file in changed_files.iterrows():
        update_file(client, file, file['user_id'])


def update_file(client, user_file, user_id):
    name = file_alias.get(user_file['file_type'], 'Файл')
    access = get_access(user_id)
    user_id_to_file = None if access == 3 else user_id
    match user_file['file_type']:
        case 'users_file':
            _, data = make_users_file(user_id_to_file)
        case 'status_file':
            _, data = make_olympiads_status_file(user_id_to_file)
        case 'olympiads_file':
            _, data = make_olympiads_with_dates_file()
        case 'class_managers_file':
            _, data = make_class_managers_file()
        case 'answers_file':
            _, data = make_answers_file()
        case 'subjects_file':
            _, data = make_subjects_file()
        case 'cm_key_file':
            _, data = make_cm_key_file(user_id)
        case 'all_cm_key_file':
            _, data = make_all_cm_key_file()
        case _:
            data = pd.DataFrame()
    title = '{} #{}'.format(name, user_id)
    try:
        spread_sheet = client.open_by_url(user_file['url'])
        spread_sheet.title = title
    except pygsheets.exceptions.SpreadsheetNotFound:
        spread_sheet = client.create(title)
    work_sheet = spread_sheet.sheet1
    work_sheet.clear()
    work_sheet.set_dataframe(data, (1, 1))
    file_format(work_sheet, user_file['file_type'])
    _ = set_updated_google_doc(user_id, user_file['file_type'])


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
            pygsheets.datarange.DataRange('A1', 'F1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=1, pixel_size=120)
        case 'subjects_file':
            pygsheets.datarange.DataRange('A1', 'C1', worksheet=work_sheet).apply_format(cell)
        case 'cm_key_file':
            pygsheets.datarange.DataRange('A1', 'D1', worksheet=work_sheet).apply_format(cell)
            work_sheet.adjust_column_width(start=2, pixel_size=50)
            work_sheet.adjust_column_width(start=4, pixel_size=50)
        case 'all_cm_key_file':
            pygsheets.datarange.DataRange('A1', 'C1', worksheet=work_sheet).apply_format(cell)


async def bind_email(user_id, message=None):
    admin = get_admin(user_id)
    email = admin['email']
    files = get_user_google_files(user_id)
    client = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    for _, file in files.iterrows():
        file_type = file['file_type']
        name = file_alias.get(file_type, 'Файл')
        title = '{} #{}'.format(name, user_id)
        url = file['url']
        spread_sheet = client.open_by_url(url)
        spread_sheet.title = title
        to_remove_permissions = []
        for user in spread_sheet.permissions:
            if user['role'] != 'owner':
                to_remove_permissions.append(user['emailAddress'])
        if to_remove_permissions:
            spread_sheet.remove_permission(to_remove_permissions)
        try:
            spread_sheet.share(email)
        except HttpError:
            text = "Не получается привязать файлы. Возможно закончилась квота на автоматическую привязку почты." \
                   " Попробуйте привязать почту завтра, через меню 'Личные данные'."
            if message is not None:
                await message.answer(text)
            else:
                await bot.send_message(chat_id=user_id, text=text)
            

def delete_all_files():
    gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    sheet_list = gc.spreadsheet_titles()
    for sheet in sheet_list:
        spread_sheet = gc.open(sheet)
        spread_sheet.delete()


def generate_reserved_files():
    client = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    status = add_reserved_files_to_db(client)
    return status
