from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, MessageToEditNotFound, InvalidQueryID, \
    MessageCantBeDeleted


def register_errors_handlers(dp: Dispatcher):
    dp.register_errors_handler(message_not_modified, exception=MessageNotModified)
    dp.register_errors_handler(message_to_delete, exception=MessageToDeleteNotFound)
    dp.register_errors_handler(message_not_found, exception=MessageToEditNotFound)
    dp.register_errors_handler(invalid_query_id, exception=InvalidQueryID)
    dp.register_errors_handler(message_cant_delete_for_everyone, exception=MessageCantBeDeleted)


async def message_not_modified(*args):
    return True


async def message_to_delete(*args):
    return True


async def message_not_found(*args):
    return True


async def invalid_query_id(*args):
    return True


async def message_cant_delete_for_everyone(*args):
    pass

