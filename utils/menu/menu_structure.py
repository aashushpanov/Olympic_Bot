from aiogram import types

from utils.menu.MenuNode import MenuNode
from keyboards.keyboards import tree_menu_keyboard
from states.admin.admin_menu import set_admin_menu
from states.user.user_menu import set_user_menu, set_interest_menu

main_menu = MenuNode()

set_user_menu(main_menu)
set_admin_menu(main_menu)

user_menu = set_user_menu(root_id='user')

interest_menu = set_interest_menu()

all_childs = main_menu.all_childs()
all_childs.update(user_menu.all_childs())
all_childs.update(interest_menu.all_childs())


async def list_menu(callback: types.CallbackQuery | types.Message, callback_data: dict = None, menu=None, title=''):
    global all_childs
    match callback:
        case types.Message():
            markup = await tree_menu_keyboard(menu)
            await callback.answer(title, reply_markup=markup)
        case types.CallbackQuery():
            if callback_data.get('action') == "d":
                next_node = all_childs.get(callback_data.get('node'))
            elif callback_data.get('action') == 'u':
                next_node = all_childs.get(callback_data.get('node')).parent
            else:
                raise KeyError
            markup = await tree_menu_keyboard(next_node, callback)
            await callback.message.edit_reply_markup(markup)
            

