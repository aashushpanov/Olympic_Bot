from aiogram import Dispatcher

from states.class_manager.registration import register_registration_handlers


def register_class_manager_states(dp: Dispatcher):
    register_registration_handlers(dp)

