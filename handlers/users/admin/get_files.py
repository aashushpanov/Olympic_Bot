import pandas as pd
from aiogram import Dispatcher, types
from aiogram.types import InputFile

from states.admin.set_olympiad import get_dates_template_file_call, SetOlympiads, get_olympiads_template_file_call, \
    get_subjects_template_file_call
from utils.db.add import set_file_ids
from utils.db.get import get_olympiads, get_subjects, get_file
from utils.menu.admin_menu import get_olympiads_file_call, get_subjects_file_call


def register_get_files_handlers(dp: Dispatcher):
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


async def send_file(callback, file_type):
    file_status = get_file(file_type)
    if file_status['changed']:
        match file_type:
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
    subjects = get_subjects()
    file_path = 'data/files/to_send/subjects.csv'
    columns_rename = {'code': 'Код предмета', 'subject_name': 'Предмет', 'section': 'Раздел'}
    subjects.rename(columns=columns_rename, inplace=True)
    subjects.to_csv(file_path, index=False, sep=';')
    return file_path


def make_subjects_template():
    columns = ['Предмет', 'Код предмета', 'Раздел']
    subjects_template = pd.DataFrame(columns=columns)
    file_path = 'data/files/to_send/subjects_template.csv'
    subjects_template.to_csv(file_path, index=False, sep=';')
    return file_path


def make_olympiads_template():
    subjects = get_subjects()
    subjects_list = list(subjects['subject_name'].values)
    columns = ['Префикс', 'Название', 'Предмет', 'мл. класс', 'ст. класс', 'ссылка на регистрацию', 'ссылка на сайт олимпиады', 'Доступные предметы']
    olympiads_template = pd.DataFrame([['', '', '', '', '', '', '', x] for x in subjects_list], columns=columns)
    file_path = 'data/files/to_send/olympiads_template.csv'
    olympiads_template.to_csv(file_path, index=False, sep=';')
    return file_path


def make_olympiads_dates_template():
    olympiads = get_olympiads()
    olympiads_list = list(olympiads.groupby('name').groups.keys())
    columns = ['Название', 'мл. класс', 'ст. класс', 'дата начала', 'дата окончания',
               'этап', 'предварительная регистрация', 'ключ']
    olympiads_file = pd.DataFrame([[x, '', '', '', '', '', '', ''] for x in olympiads_list], columns=columns)
    file_path = 'data/files/to_send/dates_template.csv'
    olympiads_file.to_csv(file_path, index=False, sep=';')
    return file_path


def make_olympiads_with_dates_file():
    file_path = 'data/files/to_send/all_olympiads.csv'
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
        olympiads_file.to_csv(file_path, index=False, sep=';')
    return file_path
