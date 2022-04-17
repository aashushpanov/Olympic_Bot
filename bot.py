import asyncio

from aiogram import executor, Dispatcher

from filters import register_filters
from keyboards.keyboards import keyboard_handlers
from loader import dp, bot
from handlers.users.admin import register_admin_handlers
from handlers.users.user import register_student_handlers
from fone_tasks.fone_task_manager import manager
from states.admin import register_admin_states
from states.user import register_user_states
from commands.user import set_user_commands
from handlers import register_handlers, register_errors_handlers

TIMEOUT = 1000


async def setup(dp: Dispatcher):
    register_handlers(dp)
    register_errors_handlers(dp)
    register_filters(dp)
    register_admin_states(dp)
    register_user_states(dp)
    register_student_handlers(dp)
    register_admin_handlers(dp)
    keyboard_handlers(dp)
    await set_user_commands(bot)


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(TIMEOUT, repeat, coro, loop)


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.call_later(TIMEOUT, repeat, manager, loop)
        executor.start_polling(dp, loop=loop, skip_updates=False, on_startup=setup)
    except KeyboardInterrupt:
        pass
    