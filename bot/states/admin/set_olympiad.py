import os

import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd
from aiogram.types import InputFile
from aiogram.utils.callback_data import CallbackData

from filters import IsAdmin, TimeAccess
from keyboards.keyboards import callbacks_keyboard, cansel_keyboard, yes_no_keyboard
from utils.db.get import get_subjects, get_olympiads, get_file
from utils.files.reader import read_file
from utils.files.templates import make_olympiads_template, make_subjects_template
from utils.menu.admin_menu import set_olympiads_call, set_subjects_call, set_olympiads_dates_call
from utils.menu.menu_structure import reset_interest_menu
from utils.db.add import add_olympiads, add_subjects, add_dates, change_files, update_olympiads, update_subjects, \
    change_google_docs

# stages = {'школьный': 1, 'муниципальный': 2, 'региональный': 3, 'заключительный': 4, 'пригласительный': 0,
#           'отборочный': 1, ''}


get_dates_template_file_call = CallbackData('get_dates_template_file')
get_subjects_template_file_call = CallbackData('get_subjects_template_file')
get_olympiads_template_file_call = CallbackData('get_olympiads_template_file')
add_not_existing_subjects_call = CallbackData('add_not_existing_subjects', 'data')
add_not_existing_olympiads_call = CallbackData('add_not_existing_olympiads', 'data')
update_dates_call = CallbackData('update_dates')
update_olympiads_call = CallbackData('update_olympiads')
update_subjects_call = CallbackData('update_subjects')


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
    dp.register_callback_query_handler(confirm_load_files, add_not_existing_subjects_call.filter(), IsAdmin(),
                                       state=[SetOlympiads.load_olympiads_file,
                                              SetOlympiads.received_olympiads_template])

    dp.register_callback_query_handler(start, set_olympiads_dates_call.filter(), TimeAccess())
    dp.register_message_handler(load_dates_file, IsAdmin(), TimeAccess(),
                                state=[SetOlympiads.load_olympiads_dates_file, SetOlympiads.received_dates_template],
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(confirm_load_files, add_not_existing_olympiads_call.filter(), IsAdmin(),
                                       state=[SetOlympiads.load_olympiads_dates_file,
                                              SetOlympiads.received_dates_template])

    dp.register_callback_query_handler(update_data, update_olympiads_call.filter(), IsAdmin(), TimeAccess(),
                                       state=[SetOlympiads.load_olympiads_file,
                                              SetOlympiads.received_olympiads_template])
    dp.register_callback_query_handler(update_data, update_dates_call.filter(), IsAdmin(), TimeAccess(),
                                       state=[SetOlympiads.load_olympiads_dates_file,
                                              SetOlympiads.received_dates_template])
    dp.register_callback_query_handler(update_data, update_subjects_call.filter(), IsAdmin(), TimeAccess(),
                                       state=[SetOlympiads.load_subjects_file, SetOlympiads.received_subject_template])


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


async def load_ol_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_data.csv'
        olympiads = await read_file(file_path, document)
        olympiads_new, olympiads_exists, subjects_not_existing, status = parsing_new_olympiads(olympiads)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите пример и загрузите еще раз')
            return
        exist_list = olympiads_to_str(olympiads_exists)
        await state.update_data(olympiads_new=olympiads_new, subjects_not_existing=subjects_not_existing,
                                olympiads_exists=olympiads_exists)
        exist_check = 1
        if exist_list:
            exist_check = 0
            await message.answer('Эти олимпиады  уже существуют:\n{}'.format('\n'.join(exist_list)),
                                 reply_markup=callbacks_keyboard(
                                     texts=['Обновить данные по ним'], callbacks=[update_olympiads_call.new()]))
        if subjects_not_existing:
            await message.answer('Следующих предметов нет в списке:\n{}'.format(', '.join(subjects_not_existing)),
                                 reply_markup=callbacks_keyboard(
                                     texts=['Добавить эти предметы?', 'Все равно загрузить (без них)'],
                                     callbacks=[add_not_existing_subjects_call.new(data='yes'),
                                                add_not_existing_subjects_call.new(data='no')]))
        else:
            if not olympiads_new.empty:
                status = add_olympiads(olympiads=olympiads_new)
                if status:
                    await message.answer('Следующие олимпиады успешно добавлены:\n{}'
                                         .format('\n'.join(olympiads_to_str(olympiads_new))))
                    change_files(['olympiads_file', 'dates_template'])
                    change_google_docs(['olympiads_file'])
                else:
                    await message.answer('Что-то пошло не так.')
            else:
                await message.answer('Ничего не добавлено')
            os.remove(file_path)
            if exist_check:
                await state.finish()
    else:
        await message.answer('Что-то пошло не так.')
        await state.finish()


async def load_subj_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/subject_data.csv'
        subjects = await read_file(file_path, document)
        subjects_new, subjects_exists, status = parsing_subjects(subjects)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите пример и загрузите еще раз')
            return
        await state.update_data(subjects_exists=subjects_exists)
        if not subjects_exists.empty:
            reply_markup = yes_no_keyboard(callback=update_subjects_call.new())
            await message.answer('Предметы с этими кодами уже существуют:\n{}\n\nОбновить данные по ним?'
                                 .format(', '.join(list(subjects_exists['name']))), reply_markup=reply_markup)
        if not subjects_new.empty:
            status = add_subjects(subjects=subjects_new)
            if status:
                await message.answer('Следующие предметы успешно добавлены:\n{}'
                                     .format(', '.join(list(subjects_new['name']))))
                reset_interest_menu()
                change_files(['subjects_file', 'olympiads_template'])
                change_google_docs(['subjects_file'])
            else:
                await message.answer('Что-то пошло не так.')
        else:
            await message.answer('Ничего не добавлено')
        os.remove(file_path)
    else:
        await message.answer('Что-то пошло не так.')
        await state.finish()


async def load_dates_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/dates_data.csv'
        dates = await read_file(file_path, document)
        dates_new, dates_exists, dates_duplicate, olympiads_not_existing, status = parsing_dates(dates)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите пример и загрузите еще раз')
            return
        await state.update_data(dates_new=dates_new, olympiads_not_existing=olympiads_not_existing,
                                dates_exists=dates_exists)
        if not dates_duplicate.empty:
            await message.answer('Даты по этим предметам не однозначны:\n{}\n\nОдному или нескольким классам назначены '
                                 'разные даты.'.format('\n'.join(olympiads_to_str(dates_duplicate))))
        if not dates_exists.empty:
            await message.answer('Даты по этим предметам уже существуют:\n{}'
                                 .format('\n'.join(olympiads_to_str(dates_exists))),
                                 reply_markup=callbacks_keyboard(texts=['Обновить данные по ним'],
                                                                 callbacks=[update_dates_call.new()]))
        if not olympiads_not_existing.empty:
            await message.answer(
                'Следующих предметов нет в списке:\n {}'.format(', '.join(olympiads_to_str(olympiads_not_existing))),
                reply_markup=callbacks_keyboard(texts=['Добавить эти олимпиады?', 'Все равно загрузить (без них)'],
                                                callbacks=[add_not_existing_olympiads_call.new(data='yes'),
                                                           add_not_existing_olympiads_call.new(data='no')]))
        else:
            if not dates_new.empty:
                status = add_dates(dates_new)
                if status:
                    await message.answer('Даты по следующим предметы успешно добавлены:\n{}'
                                         .format('\n'.join(olympiads_to_str(dates_new))))
                    change_files(['olympiads_file'])
                    change_google_docs(['olympiads_file'])
                else:
                    await message.answer('Что-то пошло не так.')
            else:
                await message.answer('Ничего не добавлено')
            os.remove(file_path)
            await state.finish()
    else:
        await message.answer('Что-то пошло не так.')
        await state.finish()


async def confirm_load_files(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    if callback_data.get('data') == 'yes':
        if callback_data.get('@') == 'add_not_existing_olympiads':
            olympiads = data.get('olympiads_not_existing')
            olympiads_list = list(olympiads.groupby('name').groups.keys())
            file_path = make_olympiads_template(olympiads_list)
            await SetOlympiads.load_olympiads_file.set()
        elif callback_data.get('@') == 'add_not_existing_subjects':
            subjects = data.get('subjects_not_existing')
            file_path = make_subjects_template(subjects)
            await SetOlympiads.load_subjects_file.set()
        else:
            raise KeyError('incorrect callback')
        file = InputFile(file_path)
        await callback.message.answer('Заполните этот шаблон, и пришлите сюда.'
                                      ' После чего, заново выберите загрузку.',
                                      reply_markup=cansel_keyboard())
        await callback.message.answer_document(file)

    if callback_data.get('data') == 'no':
        if callback_data.get('@') == 'add_not_existing_olympiads':
            dates_new = data.get('dates_new')
            status = add_dates(dates_new)
            if status:
                if not dates_new.empty:
                    await callback.message.answer('Даты по следующим предметы успешно добавлены:\n{}'
                                                  .format('\n'.join(olympiads_to_str(dates_new))))
                    change_files(['olympiads_file'])
                    change_google_docs(['olympiads_file'])
                else:
                    await callback.message.answer('Ничего не добавлено')
            else:
                await callback.message.answer('Что-то пошло не так.')
            await state.finish()
        elif callback_data.get('@') == 'add_not_existing_subjects':
            olympiads_new = data.get('olympiads_new')
            add_olympiads(olympiads=olympiads_new)
            if not olympiads_new.empty:
                await callback.message.answer('Следующие олимпиады успешно добавлены:\n{}'.
                                              format('\n'.join(olympiads_to_str(olympiads_new))))
                change_files(['olympiads_file', 'dates_template'])
                change_google_docs(['olympiads_file'])
            else:
                await callback.message.answer('Ничего не добавлено')
            await state.finish()


async def update_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    data = await state.get_data()
    if callback.data == 'update_dates':
        data_to_update = data.get('dates_exists')
    elif callback.data == 'update_olympiads':
        data_to_update = data.get('olympiads_exists')
    elif callback.data == 'update_subjects':
        data_to_update = data.get('subjects_exists')
    else:
        data_to_update = pd.DataFrame()
        KeyError('incorrect callback')
    status = 0
    if not data_to_update.empty:
        if callback.data == 'update_dates':
            status = add_dates(data_to_update)
            text_data = olympiads_to_str(data_to_update)
        elif callback.data == 'update_olympiads':
            text_data = olympiads_to_str(data_to_update)
            status = update_olympiads(data_to_update)
        elif callback.data == 'update_subjects':
            text_data = data_to_update['name'].to_list()
            status = update_subjects(data_to_update)
            reset_interest_menu()
            await state.finish()
        else:
            text_data = []
            KeyError('incorrect callback')
        if status:
            await callback.message.answer('Следующие данные успешно обновлены:\n{}'
                                          .format('\n'.join(text_data)))
            change_files(['olympiads_file', 'dates_template', 'subjects_file'])
            change_google_docs(['olympiads_file', 'dates_template', 'subjects_file'])
        else:
            await callback.message.answer('Что-то пошло не так.')
    else:
        await callback.message.answer('Ничего не добавлено')


def parsing_subjects(subjects):
    subjects.dropna(axis=0, how='all', inplace=True)
    expected_columns = ['Предмет', 'Код предмета', 'Раздел']
    if subjects.columns.to_list() != expected_columns:
        return 0, 0, 'wrong_file'
    if subjects.loc[:, expected_columns].isnull().values.any():
        return 0, 0, 'wrong_file'
    columns = ['name', 'code', 'section']
    columns_types = {'Предмет': 'object', 'Код предмета': 'object', 'Раздел': 'object'}
    try:
        subjects = subjects.astype(columns_types)
    except ValueError:
        return 0, 0, 'wrong_file'
    subjects_codes = get_subjects()['code']
    subjects_new = pd.DataFrame(columns=columns)
    subjects_exists = pd.DataFrame(columns=columns)
    for _, row in subjects.iterrows():
        subject = pd.DataFrame([[row['Предмет'], row['Код предмета'], row['Раздел']]], columns=columns)
        if subject['code'].item() in subjects_codes.values:
            subjects_exists = pd.concat([subjects_exists, subject], axis=0)
        else:
            subjects_new = pd.concat([subjects_new, subject], axis=0)
    status = 'ok'
    return subjects_new, subjects_exists, status


def parsing_new_olympiads(olympiads_to_add: pd.DataFrame):
    """
    Берет датафрейм с олимпиадами для добавления, проверяет правильность файла,
    и возвращает датафрейм с новыми олимпиадами, датафрейм с уже существующими олимпиадами, список предметов, которых нет в
    базе,
    и статус

    :param olympiads_to_add: DataFrame со следующими столбцами:
    :type olympiads_to_add: pd.DataFrame
    """
    olympiads_to_add.dropna(axis=0, how='all', inplace=True)
    columns = ['name', 'code', 'subject_id', 'grade', 'urls']
    expected_columns = ['Название', 'Тип', 'Предмет', 'мл. класс', 'ст. класс',
                        'ссылка на регистрацию', 'ссылка на сайт олимпиады', 'ссылка на прохождение олимпиады']
    if olympiads_to_add.columns.to_list() != expected_columns:
        return 0, 0, 0, 'wrong_file'
    if olympiads_to_add.loc[:, ['Название', 'Тип', 'Предмет', 'мл. класс', 'ст. класс']].isnull().values.any():
        return 0, 0, 0, 'wrong_file'
    columns_types = {'Название': 'object', 'Предмет': 'object', 'мл. класс': 'int32', 'ст. класс': 'int32',
                     'ссылка на регистрацию': 'object', 'ссылка на сайт олимпиады': 'object',
                     'ссылка на прохождение олимпиады': 'object'}
    try:
        olympiads_to_add = olympiads_to_add.astype(columns_types)
    except ValueError:
        return 0, 0, 0, 'wrong_file'
    olympiads_new = pd.DataFrame(columns=columns)
    olympiads_exists = pd.DataFrame(columns=columns)
    subjects_not_existing = []
    subjects = get_subjects()
    olympiad_codes = get_olympiads()['code']
    for _, row in olympiads_to_add.iterrows():
        l_grade = int(row['мл. класс'])
        h_grade = int(row['ст. класс'])
        subject_name = row['Предмет']
        if subject_name in subjects['name'].values:
            subject_id = subjects[subjects['name'] == subject_name]['id'].item()
            urls = {'reg_url': row['ссылка на регистрацию'] if isinstance(row['ссылка на регистрацию'], str) else '',
                    'site_url': row['ссылка на сайт олимпиады'] if isinstance(row['ссылка на сайт олимпиады'], str) else '',
                    'ol_url': row['ссылка на прохождение олимпиады'] if isinstance(row['ссылка на сайт олимпиады'], str) else ''}
            for grade in range(l_grade, h_grade + 1):
                code = row['Тип'] + '_' + subject_id + '_' + str(grade)
                olympiad = pd.DataFrame([[row['Название'], code, subject_id, grade, urls]], columns=columns)
                if code in olympiad_codes.values:
                    olympiads_exists = pd.concat([olympiads_exists, olympiad], axis=0)
                else:
                    olympiads_new = pd.concat([olympiads_new, olympiad], axis=0)
        else:
            subjects_not_existing.append(subject_name)
    status = 'ok'
    return olympiads_new, olympiads_exists, subjects_not_existing, status


def parsing_dates(dates_load: pd.DataFrame):
    dates_load.dropna(axis=0, how='all', inplace=True)
    olympiads = get_olympiads()
    expected_columns = ['Название', 'мл. класс', 'ст. класс', 'дата начала',
                        'дата окончания', 'этап', 'предварительная регистрация', 'ключ']
    if dates_load.columns.to_list() != expected_columns:
        return 0, 0, 0, 0, 'wrong_file'
    if dates_load.loc[:, expected_columns].isnull().values.any():
        return 0, 0, 0, 0, 'wrong_file'
    columns_types = {'Название': 'object', 'мл. класс': 'int32', 'ст. класс': 'int32', 'дата начала': 'object',
                     'дата окончания': 'object', 'этап': 'int32', 'предварительная регистрация': 'object',
                     'ключ': 'object'}
    try:
        dates_load = dates_load.astype(columns_types)
    except ValueError:
        return 0, 0, 0, 0, 'wrong_file'
    columns = ['id', 'name', 'grade', 'start_date', 'end_date', 'stage', 'is_active', 'key', 'pre_registration']
    olympiads_not_exist = pd.DataFrame(columns=['name', 'grade'])
    dates = pd.DataFrame(columns=columns)
    dates_new = pd.DataFrame(columns=columns)
    dates_exists = pd.DataFrame(columns=columns)
    dates_duplicate = pd.DataFrame(columns=columns)
    for _, row in dates_load.iterrows():
        l_grade = row['мл. класс']
        h_grade = row['ст. класс']
        for grade in range(l_grade, h_grade + 1):
            olympiad_id = olympiads[(olympiads['name'] == row['Название']) & (olympiads['grade'] == grade)]['id']
            if olympiad_id.empty:
                olympiads_not_exist = pd.concat([olympiads_not_exist, pd.DataFrame([[row['Название'], grade]],
                                                                                   columns=['name', 'grade'])])
                continue
            else:
                olympiad_id = olympiad_id.item()
            start_date = str_to_date(row['дата начала'])
            finish_date = str_to_date(row['дата окончания'])
            active = 1 if dt.date.today() <= finish_date else 0
            key = 1 if row['ключ'].lower() == 'да' else 0
            pre_registration = 1 if row['предварительная регистрация'].lower() == 'да' else 0
            date = pd.DataFrame([[olympiad_id, row['Название'], grade, start_date, finish_date, row['этап'],
                                  active, key, pre_registration]], columns=columns)
            dates = pd.concat([dates, date], axis=0)
    for olympiad_id, group in dates.groupby('id'):
        if group.shape[0] == 1:
            if olympiads[olympiads['id'] == olympiad_id]['is_active'].item():
                dates_exists = pd.concat([dates_exists, group])
            else:
                dates_new = pd.concat([dates_new, group])
        else:
            dates_duplicate = pd.concat([dates_duplicate, group.iloc[[0]]])
    status = 'ok'
    return dates_new, dates_exists, dates_duplicate, olympiads_not_exist, status


def olympiads_to_str(olympiads: pd.DataFrame):
    res = []
    for name, group in olympiads.groupby('name'):
        res.append(str(name) + ' ' + str(list(group['grade'])))
    return res


def str_to_date(date: str):
    date_split = date.split('.')
    date_split.reverse()
    date_split = list(map(int, date_split))
    date = dt.date(*date_split)
    return date
