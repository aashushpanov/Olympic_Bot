from aiogram import types
from aiogram.dispatcher import Dispatcher

from keyboards.keyboards import callbacks_keyboard
from utils.db.add import set_user_file_format
from utils.db.get import get_admin
from utils.menu.admin_menu import set_excel_format_call, set_google_doc_format_call
from utils.menu.class_manager_menu import change_email_call


def register_set_file_format(dp: Dispatcher):
    dp.register_callback_query_handler(set_excel_format, set_excel_format_call.filter())
    dp.register_callback_query_handler(set_google_doc_format, set_google_doc_format_call.filter())


async def set_excel_format(callback: types.CallbackQuery):
    await callback.answer()
    status = set_user_file_format(callback.from_user.id, 0)
    if status:
        await callback.message.answer('В качестве формата выгружаемых файлов выбран EXCEL.')
    else:
        await callback.message.answer('Что-то пошло не так.')


async def set_google_doc_format(callback: types.CallbackQuery):
    await callback.answer()
    if get_admin(callback.from_user.id)['email'] is None:
        markup = callbacks_keyboard(texts=['Установить'], callbacks=[change_email_call.new()])
        await callback.message.answer('Не выбрана почта для привязки таблиц. Сначала установите ее.',
                                      reply_markup=markup)
        return
    status = set_user_file_format(callback.from_user.id, 1)
    if status:
        await callback.message.answer('В качестве формата выгружаемых файлов выбраны Google таблицы.')
    else:
        await callback.message.answer('Что-то пошло не так.')

