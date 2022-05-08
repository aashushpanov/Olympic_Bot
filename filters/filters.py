import datetime as dt
from aiogram import types
from aiogram.dispatcher.filters import Filter

from utils.db.get import get_access, is_exist


class IsAdmin(Filter):

    async def check(self, message: types.Message):
        access = get_access(message.from_user.id)
        return 1 if access == 2 else 0


class IsClassManager(Filter):

    async def check(self, message: types.Message):
        access = get_access(message.from_user.id)
        return 1 if access == 1 else 0


class TimeAccess(Filter):
    def __init__(self, minutes=15):
        self.minutes = minutes

    async def check(self, callback: types.CallbackQuery | types.Message):
        match callback:
            case types.CallbackQuery():
                message = callback.message
            case types.Message():
                message = callback
            case _:
                raise TypeError
        delta = abs(dt.datetime.now() - message.date)
        access = self.minutes - delta.seconds//60
        if access < 0:
            await message.answer('Действие уже недоступно', show_alert=True)
            await message.delete()
            return 0
        else:
            return 1


class IsExist(Filter):
    key = 'is_exist'

    def __init__(self, target=1):
        self.target = target

    async def check(self, data: types.CallbackQuery | types.Message):
        result = 0
        match data:
            case types.CallbackQuery():
                result = await is_exist(data.message.chat.id)
            case types.Message():
                result = await is_exist(data.from_user.id)
        return result == self.target
