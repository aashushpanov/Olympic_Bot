from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards.keyboards import cansel_event_call


def register_cancel_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, commands=['cancel'], state='*')
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state='*')
    dp.register_callback_query_handler(cmd_cancel, cansel_event_call.filter(), state='*')


async def cmd_cancel(message: types.Message | types.CallbackQuery, state: FSMContext):
    await state.finish()
    match message:
        case types.Message():
            await message.answer("Действие отменено")
            await message.delete()
        case types.CallbackQuery():
            await message.answer()
            await message.message.answer('Действие отменено')
            await message.message.delete()
            