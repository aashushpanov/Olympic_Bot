import pandas as pd
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from filters import TimeAccess, IsAdmin
from keyboards.keyboards import callbacks_keyboard
from utils.db.add import remove_subjects, remove_olympiads, change_files, change_google_docs
from utils.db.get import get_file, get_olympiads, get_subjects
from utils.files.reader import read_file
from utils.menu.admin_menu import get_subjects_file_call, get_olympiads_file_call, delete_subjects_call, \
    delete_olympiads_call


class DeleteData(StatesGroup):
    delete_subjects = State()
    delete_olympiads = State()


def delete_data_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, delete_subjects_call.filter(), TimeAccess())
    dp.register_callback_query_handler(start, delete_olympiads_call.filter(), TimeAccess())
    dp.register_message_handler(delete_subjects, IsAdmin(), TimeAccess(),
                                state=[DeleteData.delete_subjects],
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_message_handler(delete_olympiads, IsAdmin(), TimeAccess(),
                                state=[DeleteData.delete_olympiads],
                                content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    await callback.answer()
    if callback.data == 'delete_subjects':
        reply_markup = callbacks_keyboard(texts=['Пример файла на удаление предметов', 'Список текущих предметов'],
                                          callbacks=[get_file('subjects_to_delete_example')['url'],
                                                     get_subjects_file_call.new()], cansel_button=True)
        await callback.message.answer('Загрузите файл с предметами которые надо удалить',
                                      reply_markup=reply_markup)
        await DeleteData.delete_subjects.set()
    elif callback.data == 'delete_olympiads':
        reply_markup = callbacks_keyboard(texts=['Пример файла на удаление олимпиад', 'Список текущих олимпиад'],
                                          callbacks=[get_file('olympiads_to_delete_example')['url'],
                                                     get_olympiads_file_call.new()], cansel_button=True)
        await callback.message.answer('Загрузите файл с олимпиадами которые надо удалить',
                                      reply_markup=reply_markup)
        await DeleteData.delete_olympiads.set()


async def delete_subjects(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/subject_to_delete.csv'
        subjects_to_delete = await read_file(file_path, document)
        subjects_codes, status = parsing_subject_to_delete(subjects_to_delete)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите шаблон и загрузите еще раз')
            return
        deleted_subjects, status = remove_subjects(subjects_codes)['name'].values
        if status == 0:
            await message.answer('Что-то пошло не так.')
            await state.finish()
            return
        if deleted_subjects:
            await message.answer('Удалены следующие предметы:\n{}'.format('\n'.join(deleted_subjects)))
            change_files(['olympiads_file', 'dates_template', 'subjects_file'])
            change_google_docs(['olympiads_file', 'dates_template', 'subjects_file'])
        else:
            await message.answer('Ничего не удалено.')
    await state.finish()


async def delete_olympiads(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_to_delete.csv'
        olympiads_to_delete = await read_file(file_path, document)
        olympiads_ids, status = parsing_olympiads_to_delete(olympiads_to_delete)
        if status == 'wrong_file':
            await message.answer('Неверный формат файла. Внимательно изучите шаблон и загрузите еще раз')
            return
        deleted_olympiads, status = remove_olympiads(olympiads_ids)
        if status == 0:
            await message.answer('Что-то пошло не так.')
            await state.finish()
            return
        subjects = get_subjects()
        deleted_olympiads = deleted_olympiads.join(subjects.set_index('code'), on='subject_code')
        olympiads_names = []
        deleted_olympiads = deleted_olympiads.astype({'grade': 'int32'})
        for name, group in deleted_olympiads.groupby(['name', 'subject_name']):
            olympiads_names.append(name[0] + ' (' + name[1] + ')' + ' ' + str(group['grade'].to_list()))
        if not deleted_olympiads.empty:
            await message.answer('Удалены следующие олимпиады:\n{}'.format('\n'.join(olympiads_names)))
            change_files(['olympiads_file', 'dates_template'])
            change_google_docs(['olympiads_file', 'dates_template'])
        else:
            await message.answer('Ничего не удалено.')
    await state.finish()


def parsing_subject_to_delete(subjects_to_delete: pd.DataFrame):
    subjects_to_delete.dropna(axis=0, how='all', inplace=True)
    expected_columns = ['Предмет', 'Код предмета']
    if not all(expected_column in subjects_to_delete.columns.to_list() for expected_column in expected_columns):
        return 0, 'wrong_file'
    subject_codes = []
    for _, row in subjects_to_delete.iterrows():
        subject_codes.append(row['Код предмета'])
    status = 'ok'
    return subject_codes, status


def parsing_olympiads_to_delete(olympiads_to_delete):
    olympiads_to_delete.dropna(axis=0, how='all', inplace=True)
    expected_columns = ['Название', 'Предмет']
    if not all(expected_column in olympiads_to_delete.columns.to_list() for expected_column in expected_columns):
        return 0, 'wrong_file'
    olympiads_codes = []
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('id'), on='subject_id')
    for _, row in olympiads_to_delete.iterrows():
        ids = olympiads[(olympiads['name'] == row['Название']) &
                          (olympiads['subject_name'] == row['Предмет'])]['id'].values
        for olympiad_id in ids:
            olympiads_codes.append(olympiad_id)
    status = 'ok'
    return olympiads_ids, status
