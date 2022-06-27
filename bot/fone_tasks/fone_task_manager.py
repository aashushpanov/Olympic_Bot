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
    It updates the database, gets the users who need to be notified, gets the notifications for those users, and sends the
    notifications
    """
    hour = dt.datetime.now(pytz.timezone('Europe/Moscow')).time().hour
    await greeting()
    if 0 <= hour < 1:
        await update_admins()
        update_olympiads_activity()
        update_olympiads_to_track()
        update_missed_olympiads()
        clean_notifications()
        create_notifications()
        create_question_notifications()
        update_all_files()
    # update_cm_key_limits()

    users = get_users_by_notification_time(hour)
    notifications = get_notifications(users)
    await send_notifications(notifications)
