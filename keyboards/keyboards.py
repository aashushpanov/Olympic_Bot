from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from utils.db.get import get_olympiads
from utils.menu.MenuNode import MenuNode, move

delete_keyboard_call = CallbackData('del')
cansel_event_call = CallbackData('cancel_event')
olympiad_call = CallbackData('olympiad', 'data')
grade_call = CallbackData('grade', 'data')


def keyboard_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(delete_keyboard, delete_keyboard_call.filter(), state='*')


async def delete_keyboard(callback: CallbackQuery, state: FSMContext = None):
    if state:
        await state.finish()
    await callback.message.delete_reply_markup()


async def tree_menu_keyboard(menu_node: MenuNode, callback: CallbackQuery = None, data=None):
    if callback is not None:
        row_width = int(callback.data.split(':')[-1])
    else:
        row_width = 1
    markup = InlineKeyboardMarkup(row_width=row_width)

    async for _, text, node_callback in menu_node.childs_data(callback=callback, data=data):
        if node_callback.__contains__('://'):
            markup.insert(InlineKeyboardButton(text=text, url=node_callback))
        else:
            markup.insert(InlineKeyboardButton(text=text, callback_data=node_callback))

    if menu_node.parent:
        markup.insert(
            InlineKeyboardButton(text="\U00002B05 Назад", callback_data=move.new(action='u', node=menu_node.id, data='', width=1)))

    return markup


def yes_no_keyboard(callback):
    markup = InlineKeyboardMarkup()

    markup.insert(InlineKeyboardButton(text='\U00002705 Да', callback_data=callback))
    markup.insert(InlineKeyboardButton(text='\U0000274C	Нет', callback_data=delete_keyboard_call.new()))

    return markup


def cansel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.insert(InlineKeyboardButton(text='\U0000274C Отмена', callback_data=cansel_event_call.new()))


def callbacks_keyboard(texts: list, callbacks: list, cansel_button: bool = False):
    if len(texts) != len(callbacks) and len(callbacks) != 0:
        raise KeyError
    button_dict = dict(zip(texts, callbacks))
    markup = InlineKeyboardMarkup(row_width=1)
    for text, callback in button_dict.items():
        if isinstance(callback, str) and isinstance(text, str):
            if callback.__contains__('://'):
                markup.insert(InlineKeyboardButton(text=text, url=callback))
            else:
                markup.insert(InlineKeyboardButton(text=text, callback_data=callback))
        else:
            raise TypeError
    if cansel_button:
        markup.insert(InlineKeyboardButton(text='\U0000274C Отмена', callback_data=cansel_event_call.new()))
    return markup


def grad_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = ['3', '4', '5', '6', '7', '8', '9', '10', '11']
    keyboard.add(*buttons)
    return keyboard


def olympiads_keyboard(subject):
    markup = InlineKeyboardMarkup(row_width=1)
    olympiads = get_olympiads()
    for name, group in olympiads[(olympiads['subject_code'] == subject) & (olympiads['active'] == 1)].groupby('name'):
        markup.insert(InlineKeyboardButton(text=name, callback_data=olympiad_call.new(data=name)))
    return markup


def available_grades_keyboard(grades):
    markup = InlineKeyboardMarkup()
    for grade in grades:
        markup.insert(InlineKeyboardButton(text=str(grade), callback_data=grade_call.new(data=grade)))
    return markup
