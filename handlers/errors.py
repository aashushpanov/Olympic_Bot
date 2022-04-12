from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, MessageToEditNotFound, InvalidQueryID


def register_errors_handlers(dp: Dispatcher):
    dp.register_errors_handler(message_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(message_to_delete, exception=MessageToDeleteNotFound)
    dp.register_errors_handler(message_not_found, exception=MessageToEditNotFound)
    dp.register_errors_handler(invalid_query_id, exception=InvalidQueryID)


async def message_not_modified(update, error):
    return True


async def message_to_delete(update, error):
    return True


async def message_not_found(update, error):
    return True


async def invalid_query_id(update, error):
    return True
