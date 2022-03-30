from loader import bot
from utils.db.get import get_users


async def notify():
    users = await get_users()
    for user in users:
        user_id = int(user[0][1:-1].split(',')[0])
        await bot.send_message(user_id, text='hi')