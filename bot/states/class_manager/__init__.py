from aiogram import Dispatcher

from states.class_manager.change_email import register_change_email_handlers
from states.class_manager.registration import register_registration_handlers


def register_class_manager_states(dp: Dispatcher):
    register_registration_handlers(dp)
    register_change_email_handlers(dp)

