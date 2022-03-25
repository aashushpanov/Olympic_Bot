from aiogram import Dispatcher
from aiogram import types

from handlers.tree_menu import move
from states.admin.admin_menu import set_admin_menu
from keyboards.tree_menu_keyboard import tree_menu_keyboard

menu, all_childs = set_admin_menu()


def admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(show_menu, commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(list_menu, move.filter())


async def show_menu(message: types.Message):
    await list_menu(message)


async def list_menu(callback: types.CallbackQuery | types.Message, callback_data: dict = None):
    match callback:
        case types.Message():
            markup = tree_menu_keyboard(menu)
            await callback.answer('Меню', reply_markup=markup)
        case types.CallbackQuery():
            if callback_data.get('action') == "d":
                next_node = all_childs.get(callback_data.get('node'))
            elif callback_data.get('action') == 'u':
                next_node = all_childs.get(callback_data.get('node')).parent
            else:
                raise KeyError
            markup = tree_menu_keyboard(next_node)
            await callback.message.edit_reply_markup(markup)
