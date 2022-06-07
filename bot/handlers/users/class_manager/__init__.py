from aiogram import Dispatcher

from handlers.users.class_manager.confirm_change_name import register_confirm_change_name_handler
from handlers.users.class_manager.get_files import register_get_files_handlers
from handlers.users.class_manager.set_file_format import register_set_file_format


def register_class_manager_handlers(dp: Dispatcher):
    register_get_files_handlers(dp)
    register_set_file_format(dp)
    register_confirm_change_name_handler(dp)
