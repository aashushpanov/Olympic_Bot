from aiogram import types

from utils.menu.MenuNode import MenuNode
from keyboards.keyboards import tree_menu_keyboard
from utils.menu.admin_menu import set_admin_menu
from utils.menu.user_menu import set_user_menu, set_interest_menu


main_menu = MenuNode()

set_user_menu(main_menu)
set_admin_menu(main_menu)

user_menu = set_user_menu(root_id='user')

interest_menu = set_interest_menu()

menu_childs = main_menu.all_childs()
menu_childs.update(user_menu.all_childs())
menu_childs.update(interest_menu.all_childs())


def reset_interest_menu():
    global interest_menu
    key_to_del = []
    for key, value in menu_childs.items():
        if key.startswith('o_interest_'):
            key_to_del.append(key)
    for key in key_to_del:
        menu_childs.pop(key)
    interest_menu.clean_childs()
    interest_menu = set_interest_menu(interest_menu)
    menu_childs.update(interest_menu.all_childs())


async def list_menu(callback: types.CallbackQuery | types.Message, callback_data: dict = None, menu=None, title=''):
    match callback:
        case types.Message():
            markup = await tree_menu_keyboard(menu)
            await callback.answer(title, reply_markup=markup)
        case types.CallbackQuery():
            if callback_data.get('action') == "d":
                next_node = menu_childs.get(callback_data.get('node'))
            elif callback_data.get('action') == 'u':
                next_node = menu_childs.get(callback_data.get('node')).parent
            else:
                raise KeyError
            markup = await tree_menu_keyboard(next_node, callback)
            await callback.message.edit_reply_markup(markup)
