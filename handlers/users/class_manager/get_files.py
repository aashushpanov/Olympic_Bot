from aiogram import Dispatcher, types
from aiogram.types import InputFile

from utils.db.get import get_user
from utils.files.data_files import make_users_file, make_olympiads_status_file
from utils.menu.class_manager_menu import get_cm_status_file_call, get_cm_users_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_status_file, get_cm_status_file_call.filter())
    dp.register_callback_query_handler(send_users_file, get_cm_users_file_call.filter())


async def send_users_file(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id)
    file_path = make_users_file(user['grade'], list(user['literal']))
    file = InputFile(file_path)
    await callback.message.answer_document(file)


async def send_status_file(callback: types.CallbackQuery):
    await callback.answer()
    user = get_user(callback.from_user.id)
    file_path = make_olympiads_status_file(user['grade'], list(user['literal']))
    file = InputFile(file_path)
    await callback.message.answer_document(file)


