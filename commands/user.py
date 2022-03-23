from aiogram import Bot
from aiogram.types import BotCommand


async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command="/registration", description="Регистрация в системе")
    ]
    await bot.set_my_commands(commands)
