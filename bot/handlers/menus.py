import os

import pygsheets as pygsheets
from aiogram import Dispatcher
from aiogram import types

from data import config
from data.config import GOOGLE_SERVICE_FILENAME
from filters.filters import TimeAccess, IsExist
from states.registration import reg_call
from utils.db.add import set_updated_google_doc
from utils.files.tables import update_file
from utils.menu.MenuNode import move
from keyboards.keyboards import yes_no_keyboard
from utils.db.get import get_access, get_admin, get_user_google_file
from utils.menu.generator_functions import update_file_call
from utils.menu.menu_structure import list_menu, main_menu, user_menu, admin_group_menu, class_manager_menu


GOOGLE_SERVICE_FILE = os.path.join(os.getcwd(), 'bot', 'service_files', GOOGLE_SERVICE_FILENAME)


def main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(show_main_menu, IsExist(1), commands=['menu'],
                                chat_type=types.ChatType.PRIVATE, state='*')
    dp.register_message_handler(reg_suggestion, IsExist(0), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(show_admins_group_menu, IsExist(1), commands=['menu'],
                                is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state='*')
    dp.register_callback_query_handler(update_google_doc, update_file_call.filter())


async def reg_suggestion(message: types.Message):
    await message.answer(text='Для доступа к функциям необходимо зарегистрироваться. Сделать это сейчас?',
                         reply_markup=yes_no_keyboard(reg_call.new()))


async def show_admins_group_menu(message: types.Message):
    menu = admin_group_menu
    await list_menu(message, menu=menu, title='Меню')


async def show_main_menu(message: types.Message, state=None):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        await message.answer('Действие отменено')
    match get_access(user_id=message.from_user.id):
        case 3:
            menu = main_menu
        case 2:
            menu = class_manager_menu
        case _:
            menu = user_menu
    await list_menu(message, menu=menu, title='Меню')


async def update_google_doc(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer('Данные обновляются. Дождитесь маленькой стрелки в углу кнопки.', show_alert=True)
    file_type = callback_data.get('type')
    user_id = callback.from_user.id
    admin = get_admin(user_id)
    user_file = get_user_google_file(user_id, file_type)
    client = pygsheets.authorize(service_file=GOOGLE_SERVICE_FILE)
    update_file(client, user_file, user_id)
    status = set_updated_google_doc(user_id, file_type)
    if status == 0:
        await callback.message.answer('Что-то пошло не так.')
    markup = callback.message.reply_markup
    for button in markup.inline_keyboard:
        button_cd = button[0].callback_data
        if button_cd and button_cd.split(':')[-1] == file_type:
            button[0].callback_data = ''
            button[0].url = user_file['url']
    await callback.message.edit_reply_markup(markup)
