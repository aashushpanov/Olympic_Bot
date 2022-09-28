import datetime as dt
import math

from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageCantBeDeleted

from filters import TimeAccess
from filters.filters import delete_message
from keyboards.keyboards import yes_no_keyboard
from utils.db.add import set_registration, set_execution, change_users_files, set_olympiad_status_inactive
from utils.db.get import get_olympiad, get_key_from_db, get_olympiad_status, get_user, get_olympiads, get_key_by_id, \
    get_access, get_class_managers_grades
from utils.menu.generator_functions import get_dates_call, get_key_call, confirm_execution_question_call, \
    confirm_registration_question_call, set_olympiad_inactive_call
from utils.menu.user_menu import get_nearest_olympiads_call

confirm_registration_call = CallbackData('confirm_registration', 'data', 'stage')
confirm_execution_call = CallbackData('confirm_execution', 'data', 'stage')


def register_olympiad_options_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_dates, get_dates_call.filter())
    dp.register_callback_query_handler(get_key, get_key_call.filter())
    dp.register_callback_query_handler(confirm_registration_question, confirm_registration_question_call.filter())
    dp.register_callback_query_handler(confirm_registration, confirm_registration_call.filter())
    dp.register_callback_query_handler(confirm_execution_question, confirm_execution_question_call.filter())
    dp.register_callback_query_handler(confirm_execution, confirm_execution_call.filter())
    dp.register_callback_query_handler(get_nearest_olympiads, get_nearest_olympiads_call.filter(), TimeAccess())
    dp.register_callback_query_handler(set_olympiad_inactive, set_olympiad_inactive_call.filter(), TimeAccess())


async def get_dates(callback: types.CallbackQuery, callback_data: dict):
    olympiad = get_olympiad(callback_data.get('data'))
    start_date = olympiad['start_date']
    end_date = olympiad['end_date']
    status = 'проходила ' if dt.date.today() > end_date else 'проходит '
    if start_date == end_date:
        dates = end_date.strftime('%d.%m.%y')
    else:
        dates = 'с ' + start_date.strftime('%d.%m.%y') + ' по ' + end_date.strftime('%d.%m.%y')
    await callback.answer('Олимпиада ' + status + dates, show_alert=True)


async def get_key(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    olympiad_id = callback_data.get('data')
    olympiad = get_olympiad(olympiad_id)
    if olympiad.empty:
        return
    if olympiad['keys_count'] == 0:
        await callback.answer('К сожалению, ключи на эту олимпиаду закончились. Обратитесь к классному руководителю.',
                              show_alert=True)
        return
    if olympiad['keys_count'] is None:
        await callback.answer('Ключи для этой олимпиады еще не загружены.', show_alert=True)
        return
    stage = olympiad['stage']
    key_id = get_olympiad_status(user_id, olympiad_id, stage)['key_id']
    if math.isnan(key_id):
        key, status = get_key_from_db(user_id, olympiad_id, stage)
        if status:
            change_users_files(callback.from_user.id, ['status_file'])
        else:
            await callback.answer('К сожалению, ключ получить не удалось', show_alert=True)
            return
    else:
        key = get_key_by_id(key_id)
    if key:
        await callback.answer()
        await callback.message.answer(key)
        await callback.message.answer('Это ваш ключ. Если он не работает, обратитесь к классному '
                                      'руководителю.'.format(key))
    else:
        await callback.answer('К сожалению, ключ получить не удалось', show_alert=True)


async def confirm_registration_question(callback: types.CallbackQuery, callback_data: dict):
    olympiad_id = callback_data.get('data')
    stage = get_olympiad(olympiad_id)['stage']
    status = get_olympiad_status(callback.from_user.id, olympiad_id, stage)['status']
    if status == 'idle':
        await callback.answer()
        await callback.message.answer('Удалось зарегистрироваться?',
                                      reply_markup=yes_no_keyboard(confirm_registration_call.new(data=olympiad_id,
                                                                                                 stage=stage)))
    else:
        await callback.answer('Вы уже заявили о регистрации на эту олимпиаду', show_alert=True)


async def confirm_registration(callback: types.CallbackQuery, callback_data: dict):
    await delete_message(callback.message)
    user_id = callback.from_user.id
    user = get_user(user_id)
    olympiad_code = callback_data.get('data')
    stage = callback_data.get('stage')
    status = set_registration(olympiad_code, user_id, stage)
    if status:
        await callback.answer('Регистрация подтверждена', show_alert=True)
        change_users_files(user_id, ['status_file'])
    else:
        await callback.message.answer('Что-то пошло не так.')


async def confirm_execution_question(callback: types.CallbackQuery, callback_data: dict):
    olympiad_id = callback_data.get('data')
    stage = get_olympiad(olympiad_id)['stage']
    status = get_olympiad_status(callback.from_user.id, olympiad_id, stage)['status_code']
    if status == 1:
        await callback.answer()
        await callback.message.answer('Удалось пройти олимпиаду?',
                                      reply_markup=yes_no_keyboard(confirm_execution_call.new(data=olympiad_id,
                                                                                              stage=stage)))
    elif status == 2:
        try:
            await callback.message.delete()
        except MessageCantBeDeleted:
            await callback.message.delete_reply_markup()
        await callback.answer('Вы уже заявили о выполнении данной олимпиады', show_alert=True)


async def confirm_execution(callback: types.CallbackQuery, callback_data: dict):
    await delete_message(callback.message)
    user_id = callback.from_user.id
    user = get_user(user_id)
    olympiad_code = callback_data.get('data')
    stage = int(callback_data.get('stage').split('.')[0])
    status = set_execution(olympiad_code, user_id, stage)
    if status:
        await callback.answer('Выполнение подтверждено', show_alert=True)
        change_users_files(user_id, ['status_file'])
    else:
        await callback.message.answer('Что-то пошло не так.')


async def get_nearest_olympiads(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    olympiads = get_olympiads()
    access = get_access(callback.from_user.id)
    if access == 0:
        olympiads = olympiads[(olympiads['grade'] == user['grade']) & (olympiads['is_active'] == 1)]
    elif access == 2:
        grades = get_class_managers_grades(callback.from_user.id)
        olympiads = olympiads[(olympiads['is_active'] == 1) & (olympiads['grade'].isin(grades['grade_num']))].groupby('name')['start_date'].min().reset_index()
    elif access == 3:
        olympiads = olympiads[olympiads['is_active'] == 1].groupby('name')['start_date'].min().reset_index()
    olympiads = olympiads.sort_values(by=['start_date'])
    olympiads_list = [olympiad['name'] + ' ' + olympiad['start_date'].strftime('%d.%m')
                      for _, olympiad in olympiads.iterrows()]
    if olympiads_list:
        await callback.answer()
        await callback.message.answer("\n".join(olympiads_list))
    else:
        await callback.answer('В ближайшее время ничего нет.', show_alert=True)


async def set_olympiad_inactive(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback.from_user.id
    olympiad_id = callback_data.get('data')
    status = set_olympiad_status_inactive(user_id, olympiad_id)
    if status:
        await callback.answer('Вы больше не будете получать уведомления об этой олимпиаде.', show_alert=True)
    else:
        await callback.answer('Что-тот пошло не так.', show_alert=True)
