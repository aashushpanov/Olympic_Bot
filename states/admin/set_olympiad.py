import os

import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd

from filters import IsAdmin, TimeAccess
from utils.db.get import get_subjects, get_olympiads
from utils.menu.admin_menu import set_olympiads_call, set_subjects_call, set_olympiads_dates_call
from utils.menu.menu_structure import reset_interest_menu
from utils.db.add import add_olympiads, add_subjects, add_dates

# stages = {'школьный': 1, 'муниципальный': 2, 'региональный': 3, 'заключительный': 4, 'пригласительный': 0,
#           'отборочный': 1, ''}


class SetOlympiads(StatesGroup):
    load_olympiads_file = State()
    load_subjects_file = State()
    load_olympiads_dates_file = State()


def set_olympiads_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_subjects_call.filter(), TimeAccess(), state='*')
    dp.register_message_handler(load_subj_file, IsAdmin(), TimeAccess(), state=SetOlympiads.load_subjects_file,
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(start, set_olympiads_call.filter(), TimeAccess(), state='*')
    dp.register_message_handler(load_ol_file, IsAdmin(), TimeAccess(), state=SetOlympiads.load_olympiads_file,
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(start, set_olympiads_dates_call.filter(), TimeAccess(), state='*')
    dp.register_message_handler(load_dates_file, IsAdmin(), TimeAccess(), state=SetOlympiads.load_olympiads_dates_file,
                                content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    await callback.message.answer('Загрузите файл')
    if callback.data == 'set_subjects':
        await SetOlympiads.load_subjects_file.set()
    if callback.data == 'set_olympiads':
        await SetOlympiads.load_olympiads_file.set()
    if callback.data == 'set_olympiads_dates':
        await SetOlympiads.load_olympiads_dates_file.set()


async def read_file(file_path, document):
    await document.download(
        destination_file=file_path,
    )
    file = pd.read_csv(file_path, sep=';')
    if len(file.columns) == 1:
        file = pd.read_csv(file_path, sep=',')
    return file


async def load_ol_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_data.csv'
        olympiads = await read_file(file_path, document)
        olympiads_new, olympiads_exist = parsing_new_olympiads(olympiads)
        res = add_olympiads(olympiads=olympiads_new)
        exist_list = olympiads_to_str(olympiads_exist)
        if exist_list:
            await message.answer('Эти олимпиады  уже существуют:\n{}'.format('\n'.join(exist_list)))
        # if subject_not_existing:
        #     await message.answer('Следующих предметов нет в списке:\n {}'.format(', '.join(subject_not_existing)))
        if res and not olympiads_new.empty:
            await message.answer('Следующие олимпиады успешно добавлены:\n{}'
                                 .format('\n'.join(olympiads_to_str(olympiads_new))))
        else:
            await message.answer('Ничего не добавлено')
        os.remove(file_path)
        await state.finish()


async def load_subj_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/subject_data.csv'
        subjects = await read_file(file_path, document)
        subjects_new, subjects_exist = parsing_subjects(subjects)
        res = add_subjects(subjects=subjects_new)
        if not subjects_exist.empty:
            await message.answer('Предметы с этими кодами уже существуют:\n {}'
                                 .format(', '.join(list(subjects_exist['name']))))
        if res and not subjects_new.empty:
            await message.answer('Следующие предметы успешно добавлены:\n {}'
                                 .format(', '.join(list(subjects_new['name']))))
            reset_interest_menu()
        else:
            await message.answer('Ничего не добавлено')
        os.remove(file_path)
    await state.finish()


def parsing_new_olympiads(olympiads_to_add: pd.DataFrame):
    columns = ['code', 'name', 'subject_code', 'grade', 'urls']
    olympiads_new = pd.DataFrame(columns=columns)
    olympiads_exist = pd.DataFrame(columns=columns)
    subjects = get_subjects()
    olympiad_codes = get_olympiads()['code']
    olympiads_to_add.astype({'ссылка на регистрацию': 'str', 'ссылка на сайт олимпиады': 'str'})
    for _, row in olympiads_to_add.iterrows():
        l_grade = row['мл. класс']
        h_grade = row['ст. класс']
        subject_code = subjects[subjects['subject_name'] == row['Предмет']]['code'].item()
        urls = {'reg_url': row['ссылка на регистрацию'] if isinstance(row['ссылка на регистрацию'], str) else '',
                'site_url': row['ссылка на сайт олимпиады'] if isinstance(row['ссылка на сайт олимпиады'], str) else ''}
        for grade in range(l_grade, h_grade + 1):
            code = row['Префикс'] + '_' + subject_code + '_' + str(grade)
            olympiad = pd.DataFrame([[code, row['Название'], subject_code, grade, urls]], columns=columns)
            if code in olympiad_codes.values:
                olympiads_exist = pd.concat([olympiads_exist, olympiad], axis=0)
            else:
                olympiads_new = pd.concat([olympiads_new, olympiad], axis=0)
    return olympiads_new, olympiads_exist


def olympiads_to_str(olympiads: pd.DataFrame):
    res = []
    for name, group in olympiads.groupby('name'):
        res.append(str(name) + ' ' + str(list(group['grade'])))
    return res


def parsing_subjects(subjects):
    columns = ['name', 'code', 'section']
    subjects_codes = get_subjects()['code']
    subjects_new = pd.DataFrame(columns=columns)
    subjects_exists = pd.DataFrame(columns=columns)
    for _, row in subjects.iterrows():
        subject = pd.DataFrame([[row['Предмет'], row['Код предмета'], row['Раздел']]], columns=columns)
        if subject['code'].item() in subjects_codes.values:
            subjects_exists = pd.concat([subjects_exists, subject], axis=0)
        else:
            subjects_new = pd.concat([subjects_new, subject], axis=0)
    return subjects_new, subjects_exists


async def load_dates_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/dates_data.csv'
        dates = await read_file(file_path, document)
        dates_new, dates_exists, dates_duplicate = parsing_dates(dates)
        res = add_dates(dates_new)
        if not dates_duplicate.empty:
            await message.answer('Даты по этим предметам не однозначны:\n {}'
                                 .format('\n'.join(olympiads_to_str(dates_duplicate))))
        if not dates_exists.empty:
            await message.answer('Даты по этим предметам уже существуют:\n {}'
                                 .format('\n'.join(olympiads_to_str(dates_exists))))
        if res and not dates_new.empty:
            await message.answer('Даты по следующим предметы успешно добавлены:\n {}'
                                 .format('\n'.join(olympiads_to_str(dates_new))))
        else:
            await message.answer('Ничего не добавлено')
        os.remove(file_path)
    await state.finish()


def parsing_dates(dates_load: pd.DataFrame):
    olympiads = get_olympiads()
    columns = ['code', 'name', 'grade', 'start_date', 'finish_date', 'stage', 'active', 'key', 'pre_registration']
    dates = pd.DataFrame(columns=columns)
    dates_new = pd.DataFrame(columns=columns)
    dates_exists = pd.DataFrame(columns=columns)
    dates_duplicate = pd.DataFrame(columns=columns)
    for _, row in dates_load.iterrows():
        l_grade = row['мл. класс']
        h_grade = row['ст. класс']
        for grade in range(l_grade, h_grade + 1):
            code = olympiads[(olympiads['name'] == row['Название']) & (olympiads['grade'] == grade)]['code'].item()
            start_date = str_to_date(row['дата начала'])
            finish_date = str_to_date(row['дата окончания'])
            active = 1 if dt.date.today() < finish_date else 0
            key = 1 if row['ключ'] == 'да' else 0
            pre_registration = 1 if row['предварительная регистрация'] == 'да' else 0
            date = pd.DataFrame([[code, row['Название'], grade, start_date, finish_date, row['этап'],
                                  active, key, pre_registration]], columns=columns)
            dates = pd.concat([dates, date], axis=0)
    for code, group in dates.groupby('code'):
        if group.shape[0] == 1:
            if olympiads[olympiads['code'] == code]['active'].item():
                dates_exists = pd.concat([dates_exists, group])
            else:
                dates_new = pd.concat([dates_new, group])
        else:
            dates_duplicate = pd.concat([dates_duplicate, group.iloc[[0]]])
    return dates_new, dates_exists, dates_duplicate


def str_to_date(date: str):
    date_split = date.split('.')
    date_split.reverse()
    date_split = list(map(int, date_split))
    date = dt.date(*date_split)
    return date
