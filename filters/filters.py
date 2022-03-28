import datetime as dt
from aiogram import types
from aiogram.dispatcher.filters import Filter

from utils.db.get import get_access


class IsAdmin(Filter):

    async def check(self, message: types.Message):
        access = await get_access(message.from_user.id)
        return access


class TimeAccess(Filter):
    async def check(self, callback: types.CallbackQuery):
        delta = abs(dt.datetime.now() - callback.message.date)
        access = 15 * 60 - delta.seconds
        return 0 if access < 0 else 1
