import datetime as dt

from fone_tasks.updates import greeting, update_olympiads_to_track, update_olympiads_activity, update_missed_olympiads, \
    create_notifications, send_notifications, create_question_notifications
from utils.db.get import get_notifications, get_users_by_notification_time


async def manager():
    hour = dt.datetime.today().time().hour
    # await greeting()
    # if 0 < hour < 1:
    update_olympiads_activity()
    update_olympiads_to_track()
    update_missed_olympiads()
    create_notifications()
    create_question_notifications()

    users = get_users_by_notification_time(hour)
    notifications = get_notifications(users)
    await send_notifications(notifications)
