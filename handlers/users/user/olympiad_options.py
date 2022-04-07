import datetime as dt

from aiogram import Dispatcher, types

from utils.db.get import get_olympiad
from utils.menu.user_menu import get_dates_call


def register_olympiad_options_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_dates, get_dates_call.filter())


async def get_dates(callback: types.CallbackQuery, callback_data: dict):
    olympiad = get_olympiad(callback_data.get('data'))
    start_date = olympiad['start_date'].item()
    finish_date = olympiad['finish_date'].item()
    status = 'проходила ' if dt.date.today() > finish_date else 'проходит '
    if start_date == finish_date:
        dates = finish_date.strftime('%d.%m.%y')
    else:
        dates = 'с ' + start_date.strftime('%d.%m.%y') + ' по ' + finish_date.strftime('%d.%m.%y')
    await callback.message.answer('Олимпиада ' + status + dates)

