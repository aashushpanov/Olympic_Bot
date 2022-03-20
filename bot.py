import asyncio

from loader import dp
from handlers.users.admin import register_admin
from handlers.users.student import register_student


async def main():
    register_admin(dp)
    register_student(dp)

    await  dp.start_polling(dp)


if __name__ == '__main__':
    asyncio.run(main())
