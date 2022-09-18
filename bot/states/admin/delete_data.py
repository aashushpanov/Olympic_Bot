import pandas as pd
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters import TimeAccess, IsAdmin
from filters.filters import delete_message
from keyboards.keyboards import callbacks_keyboard, yes_no_keyboard
from utils.db.add import remove_subjects, remove_olympiads, change_users_files, delete_all_db_data, remove_all_olympiads
from utils.db.get import get_olympiads, get_subjects, get_common_file
from utils.files.reader import read_file
from utils.menu.admin_menu import get_subjects_file_call, get_olympiads_file_call, delete_subjects_call, \
    delete_olympiads_call, delete_all_call
from utils.files.tables import delete_all_files


confirm_delete_all = CallbackData('confirm_delete')
delete_all_olympiads_call = CallbackData('delete_all_olympiads')
confirm_delete_all_olympiads_call = CallbackData('confirm_delete_all_olympiads')


class DeleteData(StatesGroup):
    delete_subjects = State()
    delete_olympiads = State()
    delete_all = State()


def delete_data_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, delete_subjects_call.filter(), TimeAccess())
    dp.register_callback_query_handler(start, delete_olympiads_call.filter(), TimeAccess())
    dp.register_callback_query_handler(ask_confirm_delete_all_olympiads, delete_all_olympiads_call.filter(),
                                       TimeAccess(), state=DeleteData.delete_olympiads)
    dp.register_callback_query_handler(delete_all_olympiads, confirm_delete_all_olympiads_call.filter(),
                                       TimeAccess(), state=DeleteData.delete_olympiads)
    dp.register_callback_query_handler(start, delete_all_call.filter(), TimeAccess())
    dp.register_message_handler(delete_subjects, IsAdmin(), TimeAccess(),
                                state=[DeleteData.delete_subjects],
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_message_handler(delete_olympiads, IsAdmin(), TimeAccess(),
                                state=[DeleteData.delete_olympiads],
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(delete_all, confirm_delete_all.filter(), IsAdmin(), TimeAccess(),
                                state=DeleteData.delete_all)


async def start(callback: types.CallbackQuery):
    await callback.answer()
    if callback.data == 'delete_subjects':
        reply_markup = callbacks_keyboard(texts=['Пример файла на удаление предметов', 'Список текущих предметов'],
                                          callbacks=[get_common_file('subjects_to_delete_example')['file_data'],
                                                     get_subjects_file_call.new()], cansel_button=True)
        await callback.message.answer('Загрузите файл с предметами которые надо удалить. При удалении предметов так же удаляться олимпиады по этим предметам.',
                                      reply_markup=reply_markup)
        await DeleteData.delete_subjects.set()
    elif callback.data == 'delete_olympiads':
        reply_markup = callbacks_keyboard(texts=['Пример файла на удаление олимпиад', 'Список текущих олимпиад',
                                                 'Удалить все олимпиады и ключи'],
                                          callbacks=[get_common_file('olympiads_to_delete_example')['file_data'],
                                                     get_olympiads_file_call.new(), delete_all_olympiads_call.new()],
                                          cansel_button=True)
        await callback.message.answer('Загрузите файл с олимпиадами которые надо удалить',
                                      reply_markup=reply_markup)
        await DeleteData.delete_olympiads.set()
    elif callback.data == 'delete_all':
        reply_markup = yes_no_keyboard(callback=confirm_delete_all.new())
        await callback.message.answer('Это удалит всех пользователей, все предметы, олимпиады и ключи из системы.',
                                      reply_markup=reply_markup)
        await DeleteData.delete_all.set()


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
            change_users_files(message.from_user.id, ['olympiads_file', 'dates_template', 'subjects_file'])
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
            change_users_files(message.from_user.id, ['olympiads_file', 'dates_template'])
        else:
            await message.answer('Ничего не удалено.')
    await state.finish()


async def ask_confirm_delete_all_olympiads(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_message(callback.message)
    markup = callbacks_keyboard(texts=['Точно'], callbacks=[confirm_delete_all_olympiads_call.new()], cansel_button=True)
    await callback.message.answer('Вы точно хотите удалить все олимпиады и ключи к ним? Это действие необратимо.',
                                  reply_markup=markup)


async def delete_all_olympiads(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_message(callback.message)
    status = remove_all_olympiads()
    if status:
        await callback.message.answer('Все олимпиады и ключи удалены из системы.')
    else:
        await callback.message.answer('Что-то пошло не так')
    await state.finish()


async def delete_all(callback: types.CallbackQuery, state: FSMContext):
    delete_all_files()
    delete_all_db_data()
    await callback.message.answer('Все данные удалены.')
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
    olympiads_ids = []
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('id'), on='subject_id')
    for _, row in olympiads_to_delete.iterrows():
        ids = olympiads[(olympiads['name'] == row['Название']) &
                          (olympiads['subject_name'] == row['Предмет'])]['id'].values
        for olympiad_id in ids:
            olympiads_ids.append(olympiad_id)
    status = 'ok'
    return olympiads_ids, status
