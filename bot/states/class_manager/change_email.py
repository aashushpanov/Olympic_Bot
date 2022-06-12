from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.keyboards import cansel_keyboard
from utils.db.add import add_email
from utils.files.tables import bind_email
from utils.menu.class_manager_menu import change_email_call


class ChangeEmail(StatesGroup):
    start = State()
    get_email = State()


def register_change_email_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, change_email_call.filter())
    dp.register_message_handler(get_email, state=ChangeEmail.get_email)


async def start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    markup = cansel_keyboard()
    await callback.message.answer('Введите почту для привязки Google таблиц', reply_markup=markup)
    await ChangeEmail.get_email.set()


async def get_email(message: types.Message, state: FSMContext):
    email = message.text
    status = add_email(message.from_user.id, email)
    if status:
        bind_email(message.from_user.id)
        await message.answer('Ваша новая почта {}. Что бы ее поменять, зайдите в Меню>Личные данные>Изменить почту.'
                             .format(email))
    else:
        await message.answer('Что-то пошло не так.')
    await state.finish()
