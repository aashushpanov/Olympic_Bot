from aiogram import Dispatcher
from aiogram import types

from data import config
from loader import bot
from utils.db.add import set_admin_access
from utils.db.get import get_access


def set_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(set_admin, commands=['registration'], chat_type=types.ChatType.GROUP,
                                is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)
    dp.register_message_handler(rejected, commands=['registration'], chat_type=types.ChatType.GROUP)


async def set_admin(message: types.Message):
    status = await get_access(message.from_user.id)
    if not status:
        await set_admin_access(message.from_user.id)
    await bot.send_message(message.from_user.id, "Вы администратор")
    await message.delete()


async def rejected(message: types.Message):
    await bot.send_message(message.from_user.id, "У вас не достаточно прав")
    await message.delete()
