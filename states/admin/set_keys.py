import pandas as pd
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters import TimeAccess, IsAdmin
from keyboards.keyboards import available_grades_keyboard, grade_call, yes_no_keyboard
from states.admin.set_olympiad import read_file
from utils.db.add import set_keys
from utils.db.get import get_olympiads, get_subjects
from utils.menu.admin_menu import set_keys_call


load_keys_to_db_call = CallbackData('load_keys_to_db')


class AddKeys(StatesGroup):
    choose_grade = State()
    load_confirm = State()


def set_key_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_keys_call.filter(), TimeAccess())
    dp.register_callback_query_handler(choose_grade, grade_call.filter(), state=AddKeys.choose_grade)
    dp.register_message_handler(confirm_keys_file, IsAdmin(), TimeAccess(), state=[AddKeys.load_confirm],
                                content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(load_keys_file, load_keys_to_db_call.filter(), IsAdmin(), TimeAccess(),
                                       state=AddKeys.load_confirm)


async def start(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    grades = [x for x in range(3, 12)]
    await callback.message.answer('Выберите класс', reply_markup=available_grades_keyboard(grades))
    await AddKeys.choose_grade.set()


async def choose_grade(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    grade = callback_data.get('data')
    await state.update_data(grade=grade)
    await callback.message.answer('Загрузите файл с ключами для {}-x классов'.format(grade))
    await callback.message.delete()
    await AddKeys.load_confirm.set()


async def confirm_keys_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/keys_file.csv'
        data = await state.get_data()
        grade = int(data.get('grade'))
        keys_file = await read_file(file_path, document)
        keys, conflict_subjects, non_existent_olympiads, keys_count, keys_nums = parce_keys(keys_file, grade)
        await state.update_data(keys=keys)
        await state.update_data(keys_count=keys_count)
        res_string = [[subject, num] for subject, num in keys_nums.items()]
        if non_existent_olympiads:
            await message.answer('Под эти предметы нет олимпиад:\n{}'.format('\n'.join(non_existent_olympiads)))
        if conflict_subjects:
            await message.answer('Для следующих предметов есть несколько олимпиад:\n{}\n\nВозможно дублирование '
                                 'олимпиад или неправильно выставлена необходимость ключа'
                                 .format('\n'.join([subject + ': ' + str(olympiads) for subject, olympiads in conflict_subjects.items()])))
        if not keys.empty:
            await message.answer('''Ключи для {}-х классов готовы к загрузке, убедитесь в правильности файла.\n\n
            Найдены следующие предметы:\n{}\n\nЗагрузить?'''
                                 .format(grade, '\n'.join([' '.join(olympiad) for olympiad in res_string])),
                                 reply_markup=yes_no_keyboard(callback=load_keys_to_db_call.new()))


async def load_keys_file(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.message.delete_reply_markup()
    await callback.answer()
    data = await state.get_data()
    keys = data.get('keys')
    keys_count = data.get('keys_count')
    await callback.message.answer('Начинаю загрузку')
    set_keys(keys, keys_count)
    await callback.message.answer('Загрузка завершена')


def parce_keys(keys_file, grade):
    keys_file = keys_file.loc[:, (~keys_file.columns.str.contains('^Unnamed')) & (~keys_file.columns.str.contains('Ключи'))]
    keys_file = keys_file.drop([0])
    keys_file.dropna(axis=0, how='all', inplace=True)
    keys_file.dropna(axis=1, how='all', inplace=True)
    keys_subjects = list(keys_file.columns.values)
    olympiads = get_olympiads()
    subjects = get_subjects()
    olympiads = olympiads.join(subjects.set_index('code'), on='subject_code')
    olympiads = olympiads[olympiads['grade'] == grade]
    conflict_subjects = {}
    non_existent_olympiads = []
    columns = ['olympiad_code', 'no', 'key']
    keys = pd.DataFrame(columns=columns)
    keys_count = {}
    keys_nums = {}
    for keys_subject in keys_subjects:
        target_olympiads = olympiads[(olympiads['subject_name'] == keys_subject) & (olympiads['key_needed'] == 1)]
        if target_olympiads.shape[0] == 0:
            non_existent_olympiads.append(keys_subject)
        elif target_olympiads.shape[0] > 1:
            conflict_subjects[keys_subject] = list(target_olympiads['name'].values)
        else:
            key_list = keys_file[keys_subject].values
            olympiad_code = target_olympiads['code'].iloc[0]
            count = olympiads[olympiads['code'] == olympiad_code]['keys_count'].iloc[0]
            subject_keys = pd.DataFrame([[olympiad_code, i, key] for i, key in enumerate(key_list)], columns=columns)
            subject_keys['no'] = subject_keys['no'] + count
            keys = pd.concat([keys, subject_keys])
            keys_count[olympiad_code] = int(count) + len(key_list)
            keys_nums[keys_subject] = str(len(key_list)) + ' ключей'
    return keys, conflict_subjects, non_existent_olympiads, keys_count, keys_nums
