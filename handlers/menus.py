from aiogram import Dispatcher
from aiogram import types

from filters.filters import TimeAccess, IsExist
from utils.menu.MenuNode import move
from keyboards.keyboards import yes_no_keyboard
from states.user.registration import reg_callback
from utils.db.get import get_access
from utils.menu.menu_structure import list_menu, main_menu, user_menu


def main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(show_main_menu, IsExist(1), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(reg_suggestion, IsExist(0), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state='*')


async def reg_suggestion(message: types.Message):
    await message.answer(text='Для доступа к функциям необходимо зарегистрироваться. Сделать это сейчас?',
                         reply_markup=yes_no_keyboard(reg_callback.new()))


async def show_main_menu(message: types.Message):
    if await get_access(user_id=message.from_user.id):
        menu = main_menu
    else:
        menu = user_menu
    await list_menu(message, menu=menu, title='Меню')





