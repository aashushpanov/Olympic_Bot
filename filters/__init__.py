from aiogram import Dispatcher

from filters.filters import IsAdmin


def register_filters(dp: Dispatcher):
	dp.bind_filter(IsAdmin)
