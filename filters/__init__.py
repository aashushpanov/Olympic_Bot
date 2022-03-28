from aiogram import Dispatcher

from filters.filters import IsAdmin, TimeAccess, IsExist


def register_filters(dp: Dispatcher):
	dp.bind_filter(TimeAccess)
	dp.bind_filter(IsAdmin)
	dp.bind_filter(IsExist)
