import pandas as pd
from aiogram import Dispatcher, types
from aiogram.types import InputFile

from states.admin.set_olympiad import get_dates_template_file_call, SetOlympiads, get_olympiads_template_file_call, \
    get_subjects_template_file_call
from utils.db.add import set_file_ids
from utils.db.get import get_olympiads, get_subjects, get_file, get_all_olympiads_status, get_users
from utils.menu.admin_menu import get_olympiads_file_call, get_subjects_file_call, get_status_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_status_file, get_status_file_call.filter())
    dp.register_callback_query_handler(send_olympiads_with_dates_file, get_olympiads_file_call.filter())
    dp.register_callback_query_handler(send_subjects_file, get_subjects_file_call.filter())
    dp.register_callback_query_handler(send_olympiads_template_file, get_olympiads_template_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_dates_template_file, get_dates_template_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_subjects_template_file, get_subjects_template_file_call.filter(), state='*')


async def send_olympiads_with_dates_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'olympiads_file')


async def send_olympiads_template_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'olympiads_template')


async def send_subjects_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'subjects_file')


async def send_subjects_template_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'subjects_template')


async def send_dates_template_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'dates_template')


async def send_status_file(callback: types.CallbackQuery, callback_data: dict):
    await send_file(callback, 'status_file')


async def send_file(callback, file_type):
    file_status = get_file(file_type)
    if file_status['changed']:
        match file_type:
            case 'status_file':
                file_path = make_olympiads_status_file()
            case 'olympiads_file':
                file_path = make_olympiads_with_dates_file()
            case 'olympiads_template':
                file_path = make_olympiads_template()
                await SetOlympiads.received_olympiads_template.set()
            case 'dates_template':
                file_path = make_olympiads_dates_template()
                await SetOlympiads.received_dates_template.set()
            case 'subjects_file':
                file_path = make_subjects_file()
            case 'subjects_template':
                file_path = make_subjects_template()
                await SetOlympiads.received_subject_template.set()
            case _:
                raise KeyError
        file = InputFile(file_path)
        message = await callback.message.answer_document(file)
        file_id = message.document.file_id
        file_unique_id = message.document.file_unique_id
        set_file_ids(file_type, file_id, file_unique_id)
    else:
        await callback.message.answer_document(file_status['file_id'])
    await callback.answer()


def make_subjects_file():
    file_path = 'data/files/to_send/subjects.xlsx'
    subjects = get_subjects()
    columns_rename = {'code': 'Код предмета', 'subject_name': 'Предмет', 'section': 'Раздел'}
    subjects.rename(columns=columns_rename, inplace=True)
    subjects.to_excel(file_path, index=False)
    return file_path


def make_subjects_template():
    file_path = 'data/files/to_send/subjects_template.xlsx'
    columns = ['Предмет', 'Код предмета', 'Раздел']
    subjects_template = pd.DataFrame(columns=columns)
    subjects_template.to_excel(file_path, index=False)
    return file_path


def make_olympiads_template():
    file_path = 'data/files/to_send/olympiads_template.xlsx'
    subjects = get_subjects()
    subjects_list = list(subjects['subject_name'].values)
    columns = ['Префикс', 'Название', 'Предмет', 'мл. класс', 'ст. класс', 'ссылка на регистрацию', 'ссылка на сайт олимпиады', 'Доступные предметы']
    olympiads_template = pd.DataFrame([['', '', '', '', '', '', '', x] for x in subjects_list], columns=columns)
    olympiads_template.to_excel(file_path, index=False)
    return file_path


def make_olympiads_dates_template():
    file_path = 'data/files/to_send/dates_template.xlsx'
    olympiads = get_olympiads()
    olympiads_list = list(olympiads.groupby('name').groups.keys())
    columns = ['Название', 'мл. класс', 'ст. класс', 'дата начала', 'дата окончания',
               'этап', 'предварительная регистрация', 'ключ']
    olympiads_file = pd.DataFrame([[x, '', '', '', '', '', '', ''] for x in olympiads_list], columns=columns)
    olympiads_file.to_excel(file_path, index=False)
    return file_path


def make_olympiads_with_dates_file():
    file_path = 'data/files/to_send/all_olympiads.xlsx'
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('code'), on='subject_code')
    olympiads_groups = olympiads.groupby(['name', 'start_date', 'finish_date'])
    columns = ['Название', 'Предмет', 'Этап', 'Дата начала', 'Дата окончания', 'мл. класс', 'ст. класс',
               'Активна', 'Ключ', 'Предварительная регистрация', 'Ссылка на сайт олимпиады', 'Ссылка на регистрацию']
    olympiads_file = pd.DataFrame(columns=columns)
    for name, group in olympiads_groups:
        min_grade = group['grade'].min()
        max_grade = group['grade'].max()
        urls = group['urls'].iloc[0]
        site_url = urls.get('site_url')
        reg_url = urls.get('reg_url')
        subject_name = group['subject_name'].iloc[0]
        active = 'Да' if group['active'].iloc[0] else 'Нет'
        key_needed = 'Да' if group['key_needed'].iloc[0] else 'Нет'
        pre_registration = 'Да' if group['pre_registration'].iloc[0] else 'Нет'
        stage = group['stage'].iloc[0]
        start_date = name[1].strftime('%d.%m.%y')
        finish_date = name[2].strftime('%d.%m.%y')
        olympiad = pd.DataFrame([[name[0], subject_name, stage, start_date, finish_date, min_grade, max_grade, active,
                                  key_needed, pre_registration, site_url, reg_url]], columns=columns)
        olympiads_file = pd.concat([olympiads_file, olympiad], axis=0)
        # olympiads_file.to_csv(file_path, index=False, sep=';')
    olympiads_file.to_excel(file_path, index=False)
    return file_path


def make_olympiads_status_file():
    file_path = 'data/files/to_send/status_file.xlsx'
    users = get_users()
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads_status = get_all_olympiads_status()
    olympiads_status = olympiads_status.join(olympiads.set_index('code'), on='olympiad_code', rsuffix='real')
    olympiads_status = olympiads_status.join(subjects.set_index('code'), on='subject_code')
    olympiads_status = olympiads_status.join(users.set_index('user_id'), on='user_id', rsuffix='user')
    columns = ['Имя', 'Фамилия', 'Класс', 'Олимпиада', 'Предмет', 'Ключ', 'Статус']
    status_file = pd.DataFrame(columns=columns)
    for _, olympiad_status in olympiads_status.iterrows():
        f_name = olympiad_status['first_name']
        l_name = olympiad_status['last_name']
        literal = olympiad_status['literal'] if olympiad_status['literal'] else ''
        grade = str(olympiad_status['grade']) + literal
        olympiad_name = olympiad_status['name']
        subject = olympiad_status['subject_name']
        key = olympiad_status['taken_key']
        match olympiad_status['status']:
            case 'idle':
                status = 'Добавлена'
            case 'reg':
                status = 'Зарегистрирован'
            case 'done':
                status = 'Пройдена'
            case 'missed':
                status = 'Пропущена'
            case _:
                status = 'Не определен'
        new_olympiad_status = pd.DataFrame([[f_name, l_name, grade, olympiad_name, subject, key, status]], columns=columns)
        status_file = pd.concat([status_file, new_olympiad_status], axis=0)
    status_file.to_excel(file_path, index=False)
    return file_path

