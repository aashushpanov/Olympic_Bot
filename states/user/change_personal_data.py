from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.keyboards import time_keyboard, time_call
from utils.db.add import add_notify_time
from utils.menu.user_menu import change_notify_time_call


class ChangePersonalData(StatesGroup):
    change_notify_time = State()


def register_personal_data_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(change_notify_time_start, change_notify_time_call.filter())
    dp.register_callback_query_handler(change_notify_time, time_call.filter(),
                                       state=ChangePersonalData.change_notify_time)


async def change_notify_time_start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(text='Выберите время для уведомлений', reply_markup=time_keyboard())
    await ChangePersonalData.change_notify_time.set()


async def change_notify_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await callback.message.delete()
    time = int(callback_data.get('data'))
    user_id = callback.from_user.id
    add_notify_time(time, user_id)
    await callback.message.answer('Установлено время уведомлений с {}:00 по {}:00'.format(str(time), str(time + 1)))
    await state.finish()

