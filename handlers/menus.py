from aiogram import Dispatcher
from aiogram import types
from aiogram.utils.callback_data import CallbackData

from data import config
from loader import bot
from filters.filters import TimeAccess, IsExist
from states.admin.registration import admin_reg_call
from states.class_manager.registration import class_manager_reg_call
from utils.menu.MenuNode import move
from keyboards.keyboards import yes_no_keyboard, callbacks_keyboard
from states.user.registration import user_reg_call
from utils.db.get import get_access
from utils.menu.menu_structure import list_menu, main_menu, user_menu, admin_group_menu, class_manager_menu


reg_call = CallbackData('reg')
reg_admin_deny_call = CallbackData('reg_admin_deny')


def main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(show_main_menu, IsExist(1), commands=['menu'],
                                chat_type=types.ChatType.PRIVATE, state='*')
    dp.register_message_handler(reg_suggestion, IsExist(0), commands=['menu'], chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(choose_role, reg_call.filter(), IsExist(0), chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(show_admins_group_menu, IsExist(1), commands=['menu'],
                                is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state='*')
    dp.register_callback_query_handler(reg_admin_deny, reg_admin_deny_call.filter())


async def reg_suggestion(message: types.Message):
    await message.answer(text='Для доступа к функциям необходимо зарегистрироваться. Сделать это сейчас?',
                         reply_markup=yes_no_keyboard(reg_call.new()))


async def choose_role(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    texts = ['Ученик', 'Классный руководитель', 'Администратор']
    callbacks = [user_reg_call.new(), class_manager_reg_call.new()]
    admins = await bot.get_chat_administrators(config.ADMIN_GROUP_ID)
    admins = set([admin['user']['id'] for admin in admins if not admin['user']['is_bot']])
    if callback.from_user.id in admins:
        callbacks.append(admin_reg_call.new())
    else:
        callbacks.append(reg_admin_deny_call.new())
    await callback.message.answer('Выберите должность',
                                  reply_markup=callbacks_keyboard(texts=texts, callbacks=callbacks, cansel_button=True))


async def reg_admin_deny(callback: types.CallbackQuery):
    await callback.answer('У вас недостаточно прав. Обратитесь к ответственному за олимпиадное движение.',
                          show_alert=True)


async def show_admins_group_menu(message: types.Message):
    menu = admin_group_menu
    await list_menu(message, menu=menu, title='Меню')


async def show_main_menu(message: types.Message, state=None):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        await message.answer('Действие отменено')
    match get_access(user_id=message.from_user.id):
        case 2:
            menu = main_menu
        case 1:
            menu = class_manager_menu
        case _:
            menu = user_menu
    await list_menu(message, menu=menu, title='Меню')





