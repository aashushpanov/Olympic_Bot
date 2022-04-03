import asyncio

from aiogram import executor, Dispatcher

from filters import register_filters
from keyboards.keyboards import keyboard_handlers
from loader import dp, bot
from handlers.users.admin import register_admin_handlers
from handlers.users.user import register_student_handlers
from notify.example import notify
from states.admin import register_admin_states
from states.user import register_user_states
from commands.user import set_user_commands
from handlers import register_handlers


async def setup(dp: Dispatcher):
    register_filters(dp)
    register_admin_states(dp)
    register_user_states(dp)
    register_student_handlers(dp)
    register_admin_handlers(dp)
    register_handlers(dp)
    keyboard_handlers(dp)
    await set_user_commands(bot)


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(1000, repeat, coro, loop)


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.call_later(1000, repeat, notify, loop)
        executor.start_polling(dp, loop=loop, skip_updates=False, on_startup=setup)
    except KeyboardInterrupt:
        pass
