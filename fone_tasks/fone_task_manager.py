from fone_tasks.updates import greeting, update_olympiads_to_track
from loader import bot
from utils.db.get import get_users


async def manager():
    await greeting()
    update_olympiads_to_track()
