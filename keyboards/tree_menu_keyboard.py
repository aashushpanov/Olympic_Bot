from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from handlers.MenuNode import MenuNode, move
from utils.db.get import get_access


async def tree_menu_keyboard(menu_node: MenuNode, callback: CallbackQuery = None):
    markup = InlineKeyboardMarkup()

    for _, text, node_callback in menu_node.childs_data:
        markup.insert(InlineKeyboardButton(text=text, callback_data=node_callback))

    if callback:
        access = await get_access(callback.message.from_user.id)
    else:
        access = 0
    if menu_node.parent:
        if menu_node.parent.id != 'root' or (menu_node.parent.id == 'root' and access):
            markup.insert(InlineKeyboardButton(text='Назад', callback_data=move.new(action='u', node=menu_node.id)))

    return markup
