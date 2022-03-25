from aiogram import Dispatcher
from aiogram import types

from handlers.MenuNode import move
from states.admin.admin_menu import set_admin_menu
from states.user.user_menu import set_user_menu
from keyboards.tree_menu_keyboard import tree_menu_keyboard
from utils.db.get import get_access
from .MenuNode import MenuNode

admin_menu = MenuNode()
set_user_menu(admin_menu)
set_admin_menu(admin_menu)
all_childs = admin_menu.all_childs()
user_menu = set_user_menu()


def menu_handlers(dp: Dispatcher):
	dp.register_message_handler(show_menu, commands=['menu'], chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(list_menu, move.filter())


async def show_menu(message: types.Message):
	if get_access(message.from_user.id):
		menu = admin_menu
	else:
		menu = user_menu
	await list_menu(message, menu=menu)


async def list_menu(callback: types.CallbackQuery | types.Message, callback_data: dict = None, menu=None):
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
