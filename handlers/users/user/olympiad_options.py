import datetime as dt

from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData

from filters import TimeAccess
from keyboards.keyboards import yes_no_keyboard
from utils.db.add import set_registration, set_execution
from utils.db.get import get_olympiad, get_key_from_db, get_olympiad_status
from utils.menu.user_menu import get_dates_call, get_key_call, confirm_execution_question_call,\
    confirm_registration_question_call


confirm_registration_call = CallbackData('confirm_registration', 'data', 'stage')
confirm_execution_call = CallbackData('confirm_execution', 'data', 'stage')


def register_olympiad_options_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_dates, get_dates_call.filter())
    dp.register_callback_query_handler(get_key, get_key_call.filter())
    dp.register_callback_query_handler(confirm_registration_question, confirm_registration_question_call.filter(), TimeAccess())
    dp.register_callback_query_handler(confirm_registration, confirm_registration_call.filter(), TimeAccess())
    dp.register_callback_query_handler(confirm_execution_question, confirm_execution_question_call.filter(), TimeAccess())
    dp.register_callback_query_handler(confirm_execution, confirm_execution_call.filter(), TimeAccess())


async def get_dates(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    olympiad = get_olympiad(callback_data.get('data'))
    start_date = olympiad['start_date']
    finish_date = olympiad['finish_date']
    status = 'проходила ' if dt.date.today() > finish_date else 'проходит '
    if start_date == finish_date:
        dates = finish_date.strftime('%d.%m.%y')
    else:
        dates = 'с ' + start_date.strftime('%d.%m.%y') + ' по ' + finish_date.strftime('%d.%m.%y')
    await callback.message.answer('Олимпиада ' + status + dates)


async def get_key(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    user_id = callback.from_user.id
    olympiad_code = callback_data.get('data')
    stage = get_olympiad(olympiad_code)['stage']
    key = get_olympiad_status(user_id, olympiad_code, stage)['taken_key']
    if key == '':
        key = get_key_from_db(user_id, olympiad_code, stage)
    if key:
        await callback.message.answer('Ваш ключ:\n{}\nЕсли данный ключ не работает, обратитесь к классному '
                                      'руководителю.'.format(key))
    else:
        await callback.message.answer('К сожалению, ключ получить не удалось')


async def confirm_registration_question(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    olympiad_code = callback_data.get('data')
    stage = get_olympiad(olympiad_code)['stage']
    status = get_olympiad_status(callback.from_user.id, olympiad_code, stage)['status']
    if status == 'idle':
        await callback.message.answer('Удалось зарегистрироваться?',
                                      reply_markup=yes_no_keyboard(confirm_registration_call.new(data=olympiad_code, stage=stage)))
    else:
        await callback.message.answer('Вы уже заявили о регистрации на эту олимпиаду')


async def confirm_registration(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    await callback.message.delete()
    user_id = callback.from_user.id
    olympiad_code = callback_data.get('data')
    stage = callback_data.get('stage')
    set_registration(olympiad_code, user_id, stage)
    await callback.message.answer('Регистрация подтверждена')


async def confirm_execution_question(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    olympiad_code = callback_data.get('data')
    stage = get_olympiad(olympiad_code)['stage']
    status = get_olympiad_status(callback.from_user.id, olympiad_code, stage)['status']
    if status == 'reg':
        await callback.message.answer('Удалось пройти олимпиаду?',
                                      reply_markup=yes_no_keyboard(confirm_execution_call.new(data=olympiad_code, stage=stage)))
    elif status == 'done':
        await callback.message.answer('Вы уже заявили о выполнении данной олимпиады')


async def confirm_execution(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    await callback.message.delete()
    user_id = callback.from_user.id
    olympiad_code = callback_data.get('data')
    stage = callback_data.get('stage')
    set_execution(olympiad_code, user_id, stage)
    await callback.message.answer('Выполнение подтверждено')
