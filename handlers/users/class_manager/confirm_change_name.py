from aiogram import Dispatcher, types

from states.user.change_personal_data import confirm_change_name_call
from utils.db.add import change_name, change_files, change_google_docs


def register_confirm_change_name_handler(dp: Dispatcher):
    dp.register_callback_query_handler(confirm, confirm_change_name_call.filter())


async def confirm(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback_data.get('u_i')
    first_name = callback_data.get('f_n')
    last_name = callback_data.get('l_n')
    change_name(user_id, first_name, last_name)
    await callback.message.answer('Данные изменены')
    change_files(['users_file'])
    change_google_docs(['users_file'])
