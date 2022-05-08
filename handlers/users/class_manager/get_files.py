from aiogram import Dispatcher, types
from aiogram.types import InputFile

from utils.db.get import get_user
from utils.files.data_files import make_users_file, make_olympiads_status_file
from utils.menu.generator_functions import get_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_file, get_file_call.filter())


async def get_file(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    user = get_user(callback.from_user.id)
    if callback_data.get('type') == 'users_file':
        file_path = make_users_file(user['grade'], list(user['literal']))
    else:
        file_path = make_olympiads_status_file(user['grade'], list(user['literal']))
    file = InputFile(file_path)
    await callback.message.answer_document(file)

