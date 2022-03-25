from aiogram import types
from aiogram.dispatcher.filters import Filter

from utils.db.get import get_access


class IsAdmin(Filter):

	async def check(self, message: types.Message):
		access = await get_access(message.from_user.id)
		return access
