from aiogram import Dispatcher

from handlers.users.class_manager.get_files import register_get_files_handlers


def register_class_manager_handlers(dp: Dispatcher):
    register_get_files_handlers(dp)
