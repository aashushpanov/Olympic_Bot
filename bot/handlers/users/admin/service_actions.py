from aiogram import Dispatcher, types

from utils.files.tables import generate_reserved_files
from utils.menu.admin_menu import create_reserved_google_files_call


def register_service_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(make_reserved_files, create_reserved_google_files_call.filter())


async def make_reserved_files(callback: types.CallbackQuery):
    await callback.message.answer('Начинаю генерацию.')
    await callback.answer()
    status = generate_reserved_files()
    if status:
        await callback.message.answer('успешно сгенерировано 60 файлов')
    else:
        await callback.message.answer('Что-то пошло не так.')
