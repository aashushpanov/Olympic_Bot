from aiogram import Dispatcher, types
from aiogram.types import InputFile

from filters.filters import IsClassManager
from utils.db.get import get_admin
from utils.files.data_files import make_users_file, make_olympiads_status_file
from utils.menu.generator_functions import get_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_file, get_file_call.filter(), IsClassManager())


async def get_file(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    user = get_admin(callback.from_user.id)
    if callback_data.get('type') == 'users_file':
        file_path, _ = make_users_file(user['grades'], user['literals'])
    else:
        file_path, _ = make_olympiads_status_file(user['grades'], user['literals'])
    file = InputFile(file_path)
    await callback.message.answer_document(file)

