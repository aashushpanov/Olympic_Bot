import os

import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd
from aiogram.types import InputFile
from aiogram.utils.callback_data import CallbackData

from filters import IsAdmin, TimeAccess
from keyboards.keyboards import callbacks_keyboard, cansel_keyboard
from utils.db.get import get_subjects, get_olympiads, get_file
from utils.menu.admin_menu import set_olympiads_call, set_subjects_call, set_olympiads_dates_call
from utils.menu.menu_structure import reset_interest_menu
from utils.db.add import add_olympiads, add_subjects, add_dates, change_files

# stages = {'школьный': 1, 'муниципальный': 2, 'региональный': 3, 'заключительный': 4, 'пригласительный': 0,
#           'отборочный': 1, ''}


get_dates_template_file_call = CallbackData('get_dates_template_file')
get_subjects_template_file_call = CallbackData('get_subjects_template_file')
get_olympiads_template_file_call = CallbackData('get_olympiads_template_file')
add_not_existing_subjects_call = CallbackData('add_not_existing_subjects', 'data')
add_not_existing_olympiads_call = CallbackData('add_not_existing_olympiads', 'data')


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
        file_to_encode = pd.read_csv(file_path, sep=';', encoding=encoding)
        if len(file_to_encode.columns) == 1:
            file_to_encode = pd.read_csv(file_path, sep=',', encoding=encoding)
        return file_to_encode

    try:
        file = to_csv('utf8')
    except UnicodeDecodeError:
        file = to_csv('cp1251')
    return file


def make_subjects_template(subjects: list = []):
    file_path = 'data/files/to_send/subjects_template.xlsx'
    columns = ['Предмет', 'Код предмета', 'Раздел']
    subjects_template = pd.DataFrame([[x, '', ''] for x in subjects], columns=columns)
    subjects_template.to_excel(file_path, index=False)
    return file_path


def make_olympiads_template(olympiads: list = []):
    file_path = 'data/files/to_send/olympiads_template.xlsx'
    subjects = get_subjects()
    subjects_list = list(subjects['subject_name'].values)
    ol_subj_list = merge_lists(olympiads, subjects_list)
    columns = ['Префикс', 'Название', 'Предмет', 'мл. класс', 'ст. класс', 'ссылка на регистрацию',
               'ссылка на сайт олимпиады', 'Доступные предметы']
    olympiads_template = pd.DataFrame([['', ol, '', '', '', '', '', subj] for ol, subj in ol_subj_list],
                                      columns=columns)
    olympiads_template.to_excel(file_path, index=False)
    return file_path


def merge_lists(list1, list2):
    res = []
    i = 0
    while i <= len(list1) or i <= len(list2):
        if i < len(list1):
            item1 = list1[i]
        else:
            item1 = ''
        if i < len(list2):
            item2 = list2[i]
        else:
            item2 = ''
        res.append((item1, item2))
        i += 1
    return res


async def load_ol_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_data.csv'
        olympiads = await read_file(file_path, document)
        olympiads_new, olympiads_exist, subjects_not_existing, status = parsing_new_olympiads(olympiads)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите шаблон и загрузите еще раз')
            return
        exist_list = olympiads_to_str(olympiads_exist)
        await state.update_data(olympiads_new=olympiads_new, subjects_not_existing=subjects_not_existing)
        if exist_list:
            await message.answer('Эти олимпиады  уже существуют:\n{}'.format('\n'.join(exist_list)))
        if subjects_not_existing:
            await message.answer('Следующих предметов нет в списке:\n {}'.format(', '.join(subjects_not_existing)),
                                 reply_markup=callbacks_keyboard(
                                     texts=['Добавить эти предметы?', 'Все равно загрузить (без них)'],
                                     callbacks=[add_not_existing_subjects_call.new(data='yes'),
                                                add_not_existing_subjects_call.new(data='no')]))
        else:
            if not olympiads_new.empty:
                add_olympiads(olympiads=olympiads_new)
                await message.answer('Следующие олимпиады успешно добавлены:\n{}'
                                     .format('\n'.join(olympiads_to_str(olympiads_new))))
                change_files(['olympiads_file', 'dates_template'])
            else:
                await message.answer('Ничего не добавлено')
            os.remove(file_path)
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
                                      ' После чего, заново выберите загрузку олимпиад.',
                                      reply_markup=cansel_keyboard())
        await callback.message.answer_document(file)

    if callback_data.get('data') == 'no':
        if callback_data.get('@') == 'add_not_existing_olympiads':
            dates_new = data.get('dates_new')
            add_dates(dates_new)
            if not dates_new.empty:
                await callback.message.answer('Даты по следующим предметы успешно добавлены:\n{}'
                                              .format('\n'.join(olympiads_to_str(dates_new))))
                change_files(['olympiads_file'])
            else:
                await callback.message.answer('Ничего не добавлено')
            await state.finish()
        elif callback_data.get('@') == 'add_not_existing_subjects':
            olympiads_new = data.get('olympiads_new')
            add_olympiads(olympiads=olympiads_new)
            if not olympiads_new.empty:
                await callback.message.answer('Следующие олимпиады успешно добавлены:\n{}'.
                                              format('\n'.join(olympiads_to_str(olympiads_new))))
                change_files(['olympiads_file', 'dates_template'])
            else:
                await callback.message.answer('Ничего не добавлено')


async def load_subj_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/subject_data.csv'
        subjects = await read_file(file_path, document)
        subjects_new, subjects_exist, status = parsing_subjects(subjects)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите шаблон и загрузите еще раз')
            return
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
    expected_columns = ['Префикс', 'Название', 'Предмет', 'мл. класс', 'ст. класс',
                        'ссылка на регистрацию', 'ссылка на сайт олимпиады']
    if olympiads_to_add.columns.to_list != expected_columns or olympiads_to_add['мл. класс'].dtypes != 'int64' or \
            olympiads_to_add['ст. класс'].dtypes != 'int64':
        return 0, 0, 0, 'wrong_file'
    olympiads_new = pd.DataFrame(columns=columns)
    olympiads_exist = pd.DataFrame(columns=columns)
    subjects_not_existing = []
    subjects = get_subjects()
    olympiad_codes = get_olympiads()['code']
    olympiads_to_add.astype({'ссылка на регистрацию': 'str', 'ссылка на сайт олимпиады': 'str'})
    for _, row in olympiads_to_add.iterrows():
        l_grade = int(row['мл. класс'])
        h_grade = int(row['ст. класс'])
        subject_name = row['Предмет']
        if subject_name in subjects['subject_name'].values:
            subject_code = subjects[subjects['subject_name'] == subject_name]['code'].item()
            urls = {'reg_url': row['ссылка на регистрацию'] if isinstance(row['ссылка на регистрацию'], str) else '',
                    'site_url': row['ссылка на сайт олимпиады'] if isinstance(row['ссылка на сайт олимпиады'],
                                                                              str) else ''}
            for grade in range(l_grade, h_grade + 1):
                code = row['Префикс'] + '_' + subject_code + '_' + str(grade)
                olympiad = pd.DataFrame([[code, row['Название'], subject_code, grade, urls]], columns=columns)
                if code in olympiad_codes.values:
                    olympiads_exist = pd.concat([olympiads_exist, olympiad], axis=0)
                else:
                    olympiads_new = pd.concat([olympiads_new, olympiad], axis=0)
        else:
            subjects_not_existing.append(subject_name)
    status = 'ok'
    return olympiads_new, olympiads_exist, subjects_not_existing, status


def olympiads_to_str(olympiads: pd.DataFrame):
    res = []
    for name, group in olympiads.groupby('name'):
        res.append(str(name) + ' ' + str(list(group['grade'])))
    return res


def parsing_subjects(subjects):
    subjects.dropna(axis=0, how='all', inplace=True)
    expected_columns = ['Предмет', 'Код предмета', 'Раздел']
    if subjects.columns.to_list != expected_columns:
        return 0, 0, 'wrong_file'
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
    status = 'ok'
    return subjects_new, subjects_exists, status


async def load_dates_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/dates_data.csv'
        dates = await read_file(file_path, document)
        dates_new, dates_exists, dates_duplicate, olympiads_not_existing, status = parsing_dates(dates)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите шаблон и загрузите еще раз')
            return
        await state.update_data(dates_new=dates_new, olympiads_not_existing=olympiads_not_existing)
        if not dates_duplicate.empty:
            await message.answer('Даты по этим предметам не однозначны:\n{}'
                                 .format('\n'.join(olympiads_to_str(dates_duplicate))))
        if not dates_exists.empty:
            await message.answer('Даты по этим предметам уже существуют:\n{}'
                                 .format('\n'.join(olympiads_to_str(dates_exists))))
        if not olympiads_not_existing.empty:
            await message.answer(
                'Следующих предметов нет в списке:\n {}'.format(', '.join(olympiads_to_str(olympiads_not_existing))),
                reply_markup=callbacks_keyboard(texts=['Добавить эти олимпиады?', 'Все равно загрузить (без них)'],
                                                callbacks=[add_not_existing_olympiads_call.new(data='yes'),
                                                           add_not_existing_olympiads_call.new(data='no')]))
        else:
            if not dates_new.empty:
                add_dates(dates_new)
                await message.answer('Даты по следующим предметы успешно добавлены:\n {}'
                                     .format('\n'.join(olympiads_to_str(dates_new))))
                change_files(['olympiads_file'])
            else:
                await message.answer('Ничего не добавлено')
            os.remove(file_path)
            await state.finish()


def parsing_dates(dates_load: pd.DataFrame):
    dates_load.dropna(axis=0, how='all', inplace=True)
    olympiads = get_olympiads()
    expected_columns = ['Название', 'мл. класс', 'ст. класс', 'дата начала',
                        'дата окончания', 'этап', 'предварительная регистрация', 'ключ']
    if dates_load.columns.to_list() != expected_columns or dates_load['мл. класс'].dtype != 'int64' or \
            dates_load['ст. класс'].dtype != 'int64' or dates_load['этап'].dtype != 'int64':
        return 0, 0, 0, 0, 'wrong_file'
    columns = ['code', 'name', 'grade', 'start_date', 'finish_date', 'stage', 'active', 'key', 'pre_registration']
    olympiads_not_exist = pd.DataFrame(columns=['name', 'grade'])
    dates = pd.DataFrame(columns=columns)
    dates_new = pd.DataFrame(columns=columns)
    dates_exists = pd.DataFrame(columns=columns)
    dates_duplicate = pd.DataFrame(columns=columns)
    for _, row in dates_load.iterrows():
        l_grade = row['мл. класс']
        h_grade = row['ст. класс']
        for grade in range(l_grade, h_grade + 1):
            code = olympiads[(olympiads['name'] == row['Название']) & (olympiads['grade'] == grade)]['code']
            if code.empty:
                olympiads_not_exist = pd.concat([olympiads_not_exist, pd.DataFrame([[row['Название'], grade]],
                                                                                   columns=['name', 'grade'])])
                continue
            else:
                code = code.item()
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
    status = 'ok'
    return dates_new, dates_exists, dates_duplicate, olympiads_not_exist, status


def str_to_date(date: str):
    date_split = date.split('.')
    date_split.reverse()
    date_split = list(map(int, date_split))
    date = dt.date(*date_split)
    return date
