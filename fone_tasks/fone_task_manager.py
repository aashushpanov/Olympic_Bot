from fone_tasks.updates import greeting, update_olympiads_to_track, update_olympiads_activity, update_missed_olympiads, \
    create_notifications, send_notifications
from utils.db.get import get_notifications


async def manager():
    # await greeting()
    update_olympiads_activity()
    update_olympiads_to_track()
    # update_missed_olympiads()
    create_notifications()
    notifications = get_notifications()
    await send_notifications(notifications)
