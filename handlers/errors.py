from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageNotModified


def register_errors_handlers(dp: Dispatcher):
    dp.register_errors_handler(message_not_modified, exception=MessageNotModified)


async def message_not_modified(update, error):
    return True
