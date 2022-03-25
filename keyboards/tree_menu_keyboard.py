from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.MenuNode import MenuNode, move


def tree_menu_keyboard(menu_node: MenuNode):
    markup = InlineKeyboardMarkup()

    for _, text, callback in menu_node.childs_data:
        markup.insert(InlineKeyboardButton(text=text, callback_data=callback))

    if menu_node.parent:
        markup.insert(InlineKeyboardButton(text='Назад', callback_data=move.new(action='u', node=menu_node.id)))

    return markup
