import datetime as dt

from aiogram import Dispatcher, types

from utils.db.get import get_olympiad, get_key_from_db, get_olympiad_status
from utils.menu.user_menu import get_dates_call, get_key_call


def register_olympiad_options_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_dates, get_dates_call.filter())
    dp.register_callback_query_handler(get_key, get_key_call.filter())


async def get_dates(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    olympiad = get_olympiad(callback_data.get('data'))
    start_date = olympiad['start_date'].item()
    finish_date = olympiad['finish_date'].item()
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
    stage = get_olympiad(olympiad_code)['stage'].item()
    key = get_olympiad_status(user_id, olympiad_code, stage)['taken_key']
    if key == '':
        key = get_key_from_db(user_id, olympiad_code, stage)
    if key:
        await callback.message.answer('Ваш ключ:\n{}\nЕсли данный ключ не работает, обратитесь к классному '
                                      'руководителю.'.format(key))
    else:
        await callback.message.answer('К сожалению, ключ получить не удалось')

