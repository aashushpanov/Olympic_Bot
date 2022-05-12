from aiogram import Dispatcher

from handlers.users.user.help import register_help_handlers
from handlers.users.user.olympiad_options import register_olympiad_options_handlers
from handlers.users.user.personal_data import register_personal_data_handlers


def register_student_handlers(dp: Dispatcher):
    register_olympiad_options_handlers(dp)
    register_help_handlers(dp)
    register_personal_data_handlers(dp)
