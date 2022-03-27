from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from handlers.MenuNode import MenuNode, move
from utils.db.get import get_access


async def tree_menu_keyboard(menu_node: MenuNode, callback: CallbackQuery = None):
    markup = InlineKeyboardMarkup()

    async for _, text, node_callback in menu_node.childs_data(callback=callback):
        markup.insert(InlineKeyboardButton(text=text, callback_data=node_callback))

    if menu_node.parent:
        markup.insert(
                InlineKeyboardButton(text='Назад', callback_data=move.new(action='u', node=menu_node.id, data='')))

    return markup
