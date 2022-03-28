from aiogram import Dispatcher

from filters.filters import IsAdmin, TimeAccess


def register_filters(dp: Dispatcher):
	dp.bind_filter(TimeAccess)
	dp.bind_filter(IsAdmin)
