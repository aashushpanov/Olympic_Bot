from aiogram import Dispatcher

from states.class_manager.join import register_registration_handlers


def register_class_manager_handlers(dp: Dispatcher):
    register_registration_handlers(dp)

