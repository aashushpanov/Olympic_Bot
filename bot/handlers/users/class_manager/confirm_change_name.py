from aiogram import Dispatcher, types

from states.user.change_personal_data import confirm_change_name_call
from utils.db.add import change_name, change_users_files


def register_confirm_change_name_handler(dp: Dispatcher):
    dp.register_callback_query_handler(confirm, confirm_change_name_call.filter())


async def confirm(callback: types.CallbackQuery, callback_data: dict):
    user_id = callback_data.get('u_i')
    first_name = callback_data.get('f_n')
    last_name = callback_data.get('l_n')
    status = change_name(user_id, first_name, last_name)
    if status:
        await callback.message.answer('Данные изменены')
        change_users_files(user_id, ['users_file'])
    else:
        await callback.message.answer('Что-то пошло не так.')
