from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, MessageToEditNotFound, InvalidQueryID


def register_errors_handlers(dp: Dispatcher):
    dp.register_errors_handler(message_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(message_to_delete, exception=MessageToDeleteNotFound)
    dp.register_errors_handler(message_not_found, exception=MessageToEditNotFound)
    dp.register_errors_handler(invalid_query_id, exception=InvalidQueryID)


async def message_not_modified():
    return True


async def message_to_delete():
    return True


async def message_not_found():
    return True


async def invalid_query_id():
    return True
