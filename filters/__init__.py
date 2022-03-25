from filters.filters import IsAdmin


def register_filters(dp):
	dp.register_filter(IsAdmin)