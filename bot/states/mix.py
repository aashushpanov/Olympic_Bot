from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from keyboards.keyboards import yes_no_keyboard
from utils.db.add import set_user_inactive, delete_user
from utils.db.get import get_access
from utils.menu.user_menu import delete_yourself_call


def register_mix_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(ask_delete_confirm, delete_yourself_call.filter())
    dp.register_callback_query_handler(confirm_delete_user, confirm_delete_yourself_call.filter(),
                                       state=DeleteYourself.ask_delete_confirm)


class DeleteYourself(StatesGroup):
    ask_delete_confirm = State()
    

confirm_delete_yourself_call = CallbackData('confirm_delete_yourself')


async def ask_delete_confirm(callback: types.CallbackQuery):
    await callback.answer()
    markup = yes_no_keyboard(callback=confirm_delete_yourself_call.new())
    await callback.message.answer('Вы точно хотите удалить себя из системы?',
                                  reply_markup=markup)
    await DeleteYourself.ask_delete_confirm.set()


async def confirm_delete_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    access = get_access(user_id)
    if access == 0:
        status = set_user_inactive(user_id)
    else:
        status = delete_user(user_id)
    if status:
        await callback.message.answer('Вы удалены из системы')
    else:
        await callback.message.answer('Что-то пошло не так.')
    await state.finish()
