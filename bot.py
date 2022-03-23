import asyncio

from loader import dp
from handlers.users.admin import register_admin
from handlers.users.user import register_student
from states.user import register_user_handlers


async def main():
    register_admin(dp)
    register_student(dp)
    register_user_handlers(dp)

    await  dp.start_polling(dp)


if __name__ == '__main__':
    asyncio.run(main())
