from aiogram import Dispatcher
from aiogram import types

from handlers.MenuNode import move
from states.admin.admin_menu import set_admin_menu
from states.user.registration import reg_callback
from states.user.user_menu import set_user_menu
from keyboards.tree_menu_keyboard import tree_menu_keyboard, yes_no_keyboard
from utils.db.get import get_access
from .MenuNode import MenuNode
from filters.filters import TimeAccess, IsExist

main_menu = MenuNode()
set_user_menu(main_menu)
set_admin_menu(main_menu)
user_menu = set_user_menu(root_id='user')
all_childs = main_menu.all_childs()
all_childs.update(user_menu.all_childs())


def menu_handlers(dp: Dispatcher):
    dp.register_message_handler(show_menu, IsExist(1), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(reg_suggestion, IsExist(0), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess())


async def reg_suggestion(message: types.Message):
    await message.answer(text='Для доступа к функциям необходимо зарегистрироваться. Сделать это сейчас?',
                         reply_markup=yes_no_keyboard(reg_callback.new()))


async def show_menu(message: types.Message):
    if await get_access(user_id=message.from_user.id):
        menu = main_menu
    else:
        menu = user_menu
    await list_menu(message, menu=menu)


async def list_menu(callback: types.CallbackQuery | types.Message, callback_data: dict = None, menu=None):
    match callback:
        case types.Message():
            markup = await tree_menu_keyboard(menu)
            await callback.answer('Меню', reply_markup=markup)
        case types.CallbackQuery():
            if callback_data.get('action') == "d":
                next_node = all_childs.get(callback_data.get('node'))
            elif callback_data.get('action') == 'u':
                next_node = all_childs.get(callback_data.get('node')).parent
            else:
                raise KeyError
            markup = await tree_menu_keyboard(next_node, callback)
            await callback.message.edit_reply_markup(markup)
