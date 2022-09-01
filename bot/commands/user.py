from aiogram import Bot
from aiogram.types import BotCommand


async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command="/menu", description="Меню"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/cancel", description="Отменить"),
    ]
    await bot.set_my_commands(commands)
