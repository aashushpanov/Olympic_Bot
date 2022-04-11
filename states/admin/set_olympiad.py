import os

import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd
from aiogram.utils.callback_data import CallbackData

from filters import IsAdmin, TimeAccess
from keyboards.keyboards import callbacks_keyboard
from utils.db.get import get_subjects, get_olympiads, get_file
from utils.menu.admin_menu import set_olympiads_call, set_subjects_call, set_olympiads_dates_call
from utils.menu.menu_structure import reset_interest_menu
from utils.db.add import add_olympiads, add_subjects, add_dates, change_files

# stages = {'школьный': 1, 'муниципальный': 2, 'региональный': 3, 'заключительный': 4, 'пригласительный': 0,
#           'отборочный': 1, ''}


get_dates_template_file_call = CallbackData('get_dates_template_file')
get_subjects_template_file_call = CallbackData('get_subjects_template_file')
get_olympiads_template_file_call = CallbackData('get_olympiads_template_file')


class SetOlympiads(StatesGroup):
    load_olympiads_file = State()
    received_olympiads_template = State()
    load_subjects_file = State()
    received_subject_template = State()
    load_olympiads_dates_file = State()
    received_dates_template = State()


def set_olympiads_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_subjects_call.filter(), TimeAccess())
    dp.register_message_handler(load_subj_file, IsAdmin(), TimeAccess(),
                                state=[SetOlympiads.load_subjects_file, SetOlympiads.received_subject_template],
                                content_types=types.ContentTypes.DOCUMENT)

    dp.register_callback_query_handler(start, set_olympiads_call.filter(), TimeAccess())
    dp.register_message_handler(load_ol_file, IsAdmin(), TimeAccess(),
                                state=[SetOlympiads.load_olympiads_file, SetOlympiads.received_olympiads_template],
                                content_types=types.ContentTypes.DOCUMENT)

    dp.register_callback_query_handler(start, set_olympiads_dates_call.filter(), TimeAccess())
    dp.register_message_handler(load_dates_file, IsAdmin(), TimeAccess(),
                                state=[SetOlympiads.load_olympiads_dates_file, SetOlympiads.received_dates_template],
                                content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    if callback.data == 'set_subjects':
        await callback.answer()
        reply_markup = callbacks_keyboard(texts=['Пример заполнения предметов', 'Скачать шаблон'],
                                          callbacks=[get_file('subjects_example')['url'],
                                                     get_subjects_template_file_call.new()],
                                          cansel_button=True)
        await callback.message.answer(
            'Загрузите файл с предметами, следующие файлы помогут правильно заполнить таблицу:',
            reply_markup=reply_markup)
        await SetOlympiads.load_subjects_file.set()
    if callback.data == 'set_olympiads':
        await callback.answer()
        reply_markup = callbacks_keyboard(texts=['Пример заполнения олимпиад', 'Скачать шаблон'],
                                          callbacks=[get_file('olympiads_example')['url'],
                                                     get_olympiads_template_file_call.new()],
                                          cansel_button=True)
        await callback.message.answer(
            'Загрузите файл с олимпиадами, следующие файлы помогут правильно заполнить таблицу:',
            reply_markup=reply_markup)
        await SetOlympiads.load_olympiads_file.set()
    if callback.data == 'set_olympiads_dates':
        await callback.answer()
        reply_markup = callbacks_keyboard(texts=['Пример заполнения дат этапов', 'Скачать шаблон'],
                                          callbacks=[get_file('dates_example')['url'],
                                                     get_dates_template_file_call.new()],
                                          cansel_button=True)
        await callback.message.answer('Загрузите файл с датами, следующие файлы помогут правильно заполнить таблицу:',
                                      reply_markup=reply_markup)
        await SetOlympiads.load_olympiads_dates_file.set()


async def read_file(file_path, document):
    await document.download(
        destination_file=file_path,
    )

    def to_csv(encoding=None):
        file = pd.read_csv(file_path, sep=';', encoding=encoding)
        if len(file.columns) == 1:
            file = pd.read_csv(file_path, sep=',', encoding=encoding)
        return file

    try:
        file = to_csv('utf8')
    except UnicodeDecodeError:
        file = to_csv('cp1251')
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
            change_files(['olympiads_file', 'dates_template'])
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
            change_files(['subjects_file', 'olympiads_template'])
        else:
            await message.answer('Ничего не добавлено')
        os.remove(file_path)
    await state.finish()


def parsing_new_olympiads(olympiads_to_add: pd.DataFrame):
    olympiads_to_add.dropna(axis=0, how='all', inplace=True)
    columns = ['code', 'name', 'subject_code', 'grade', 'urls']
    olympiads_new = pd.DataFrame(columns=columns)
    olympiads_exist = pd.DataFrame(columns=columns)
    subjects = get_subjects()
    olympiad_codes = get_olympiads()['code']
    olympiads_to_add.astype({'ссылка на регистрацию': 'str', 'ссылка на сайт олимпиады': 'str'})
    for _, row in olympiads_to_add.iterrows():
        l_grade = int(row['мл. класс'])
        h_grade = int(row['ст. класс'])
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
            change_files(['olympiads_file'])
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
