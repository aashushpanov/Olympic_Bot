import datetime as dt
import pytz

from .updates import update_olympiads_to_track, update_olympiads_activity, update_missed_olympiads, \
    create_notifications, send_notifications, create_question_notifications, greeting
from handlers.users.admin.set_admin import update_admins
from utils.db.add import clean_notifications, update_cm_key_limits
from utils.db.get import get_notifications, get_users_by_notification_time
from utils.files.tables import update_all_files


async def manager():
    """
    Он обновляет базу данных, получает пользователей, которые должны быть уведомлены в настоящее время, получает уведомления
    для этих пользователей и отправляет уведомления.
    """
    hour = dt.datetime.now(pytz.timezone('Europe/Moscow')).time().hour
    # await greeting()

    if 1 <= hour < 2:
        await update_admins()
        update_olympiads_activity()
        update_missed_olympiads()
        update_olympiads_to_track()
        clean_notifications()
        create_notifications()
        create_question_notifications()
        update_all_files()
        update_cm_key_limits()

        users = get_users_by_notification_time(hour)
        notifications = get_notifications(users)
        await send_notifications(notifications)
