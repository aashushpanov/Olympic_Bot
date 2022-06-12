from aiogram import Dispatcher

from states.registration import register_registration_handlers


def register_common_handlers(dp: Dispatcher):
    register_registration_handlers(dp)
