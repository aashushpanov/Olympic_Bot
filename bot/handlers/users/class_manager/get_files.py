from aiogram import Dispatcher, types
from aiogram.types import InputFile

from filters.filters import IsClassManager
from utils.files.data_files import make_users_file, make_olympiads_status_file, make_cm_key_file
from utils.menu.generator_functions import get_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_file, get_file_call.filter(), IsClassManager())


async def get_file(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    if callback_data.get('type') == 'users_file':
        file_path, _ = make_users_file(callback.from_user.id)
    elif callback_data.get('type') == 'status_file':
        file_path, _ = make_olympiads_status_file(callback.from_user.id)
    elif callback_data.get('type') == 'cm_key_file':
        file_path, _ = make_cm_key_file(callback.from_user.id)
    else:
        raise KeyError('Неверный тип файла')
    file = InputFile(file_path)
    await callback.message.answer_document(file)

