import pandas as pd
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageCantBeDeleted

from filters.filters import delete_message
from utils.db.get import get_olympiads, get_admins
from utils.menu.MenuNode import MenuNode, move

delete_keyboard_call = CallbackData('del')
cansel_event_call = CallbackData('cancel_event')
olympiad_call = CallbackData('olympiad', 'data')
grade_call = CallbackData('grade', 'data')
time_call = CallbackData('time', 'data')
choose_admin_call = CallbackData('choose_admin', 'data')
pages_keyboard_call = CallbackData('pk', 'data')
page_move_call = CallbackData('page_move', 'data')


def keyboard_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(delete_keyboard, delete_keyboard_call.filter(), state='*')


async def delete_keyboard(callback: CallbackQuery, state: FSMContext = None):
    if state:
        await state.finish()
    await delete_message(callback.message)


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
            InlineKeyboardButton(text="\U00002B05 Назад",
                                 callback_data=move.new(action='u', node=menu_node.id, data='', width=1)))

    return markup


def yes_no_keyboard(callback):
    markup = InlineKeyboardMarkup()

    markup.insert(InlineKeyboardButton(text='\U00002705 Да', callback_data=callback))
    markup.insert(InlineKeyboardButton(text='\U0000274C	Нет', callback_data=delete_keyboard_call.new()))

    return markup


def cansel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.insert(InlineKeyboardButton(text='\U0000274C Отмена', callback_data=cansel_event_call.new()))
    return markup


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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    buttons = ['3', '4', '5', '6', '7', '8', '9', '10', '11']
    keyboard.add(*buttons)
    return keyboard


def literal_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    buttons = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'Ф']
    keyboard.add(*buttons)
    return keyboard


def time_keyboard():
    markup = InlineKeyboardMarkup()
    for hour in range(12, 22):
        text = '{}:00-{}:00'.format(str(hour), str(hour + 1))
        markup.insert(InlineKeyboardButton(text=text, callback_data=time_call.new(data=str(hour))))
    return markup


def olympiads_keyboard(subject):
    markup = InlineKeyboardMarkup(row_width=1)
    olympiads = get_olympiads()
    for name, group in olympiads[(olympiads['subject_id'] == subject) & (olympiads['is_active'] == 1)].groupby('name'):
        markup.insert(InlineKeyboardButton(text=name, callback_data=olympiad_call.new(data=name)))
    return markup


def available_grades_keyboard(grades):
    markup = InlineKeyboardMarkup()
    for grade in grades:
        markup.insert(InlineKeyboardButton(text=str(grade), callback_data=grade_call.new(data=grade)))
    return markup


def admins_keyboard():
    admins = get_admins()
    markup = InlineKeyboardMarkup(row_width=1)
    for _, admin in admins.iterrows():
        admin_name = '{} {}'.format(admin['last_name'], admin['first_name'])
        admin_id = admin['admin_id']
        markup.insert(InlineKeyboardButton(text=admin_name, callback_data=choose_admin_call.new(data=admin_id)))
    markup.insert(InlineKeyboardButton(text='Задать всем', callback_data=choose_admin_call.new(data='all')))
    return markup


def pages_keyboard(list_of_instance: pd.DataFrame, callback_column: str, text_column: str, page: int, height: int = 5):
    """
    Он принимает фрейм данных, столбец для использования в качестве данных обратного вызова, столбец для использования в
    качестве текста, текущую страницу и количество строк на странице и возвращает клавиатуру со строками фрейма данных в
    качестве кнопок.

    :param list_of_instance: pd.DataFrame — кадр данных, содержащий данные, которые вы хотите отобразить
    :type list_of_instance: pd.DataFrame
    :param callback_column: столбец в кадре данных, который содержит данные обратного вызова
    :type callback_column: str
    :param text_column: столбец в кадре данных, содержащий текст, который будет отображаться на кнопке
    :type text_column: str
    :param page: int - номер страницы
    :type page: int
    :param height: количество строк для отображения на странице, defaults to 5
    :type height: int (optional)
    :return: Объект InlineKeyboardMarkup
    """
    if list_of_instance.shape[0] - (page + 1) * height == 1:
        top = (page + 1) * height + 1
        last_page = True
    else:
        top = (page + 1) * height
        last_page = False
    if list_of_instance.shape[0] < (page + 1) * height:
        last_page = True
    page_list = list_of_instance.iloc[height*page:top]
    markup = InlineKeyboardMarkup(row_width=1)
    for _, row in page_list.iterrows():
        markup.insert(InlineKeyboardButton(text=row[text_column],
                                           callback_data=pages_keyboard_call.new(data=row[callback_column])))
    left_btn = None
    right_btn = None
    if page != 0:
        left_btn = InlineKeyboardButton(text='\U000025C0', callback_data=page_move_call.new(data='decr'))
    if not last_page:
        right_btn = InlineKeyboardButton(text='\U000025B6', callback_data=page_move_call.new(data='incr'))
    if right_btn is None and left_btn is None:
        return markup
    elif right_btn and left_btn:
        markup.row(left_btn, right_btn)
    else:
        if left_btn:
            btn = left_btn
        else:
            btn = right_btn
        markup.row(btn)
    return markup


