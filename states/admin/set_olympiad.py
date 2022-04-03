import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd
from pandas import DataFrame

from filters import IsAdmin, TimeAccess
from utils.db.get import get_subjects, get_olympiads
from utils.menu.admin_menu import set_olympiads_call, set_subjects_call
from utils.menu.menu_structure import reset_interest_menu
from utils.db.add import add_olympiads, add_subjects


class SetOlympiads(StatesGroup):
    load_file = State()


class SetSubjects(StatesGroup):
    load_file = State()


def set_olympiads_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_subjects_call.filter(), IsAdmin(), TimeAccess(), state='*')
    dp.register_message_handler(load_subj_file, state=SetSubjects.load_file, content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(start, set_olympiads_call.filter(), IsAdmin(), TimeAccess(), state='*')
    dp.register_message_handler(load_ol_file, state=SetOlympiads.load_file, content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    await callback.message.answer('Загрузите файл')
    if callback.data == 'set_subjects':
        await SetSubjects.load_file.set()
    else:
        await SetOlympiads.load_file.set()


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
        olympiads_new, exist_list = parsing_new_olympiads(olympiads)
        res = await add_olympiads(olympiads=olympiads_new)
        if exist_list:
            await message.answer('Эти олимпиады  уже существуют:\n{}'.format('\n'.join(exist_list)))
        # if subject_not_existing:
        #     await message.answer('Следующих предметов нет в списке:\n {}'.format(', '.join(subject_not_existing)))
        if res and not olympiads_new.empty:
            await message.answer('Следующие олимпиады успешно добавлены:\n {}'
                                 .format(', '.join(olympiads_to_str(olympiads_new))))
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
    columns = ['code', 'name', 'subject_code', 'grade']
    olympiads_new = pd.DataFrame(columns=columns)
    olympiads_exist = pd.DataFrame(columns=columns)
    subjects = get_subjects()
    olympiad_codes = get_olympiads()['code']
    for _, row in olympiads_to_add.iterrows():
        l_grade = row['мл. класс']
        h_grade = row['ст. класс']
        subject_code = subjects[subjects['subject_name'] == row['Предмет']]['code'].item()
        for grade in range(l_grade, h_grade + 1):
            code = row['Префикс'] + '_' + subject_code + '_' + str(grade)
            olympiad = pd.DataFrame([[code, row['Название'], subject_code, grade]], columns=columns)
            if code in olympiad_codes.values:
                olympiads_exist = pd.concat([olympiads_exist, olympiad], axis=0)
            else:
                olympiads_new = pd.concat([olympiads_new, olympiad], axis=0)
    exist_list = olympiads_to_str(olympiads_new)
    return olympiads_new, exist_list


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
