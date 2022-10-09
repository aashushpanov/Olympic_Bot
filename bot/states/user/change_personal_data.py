from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters.filters import delete_message
from keyboards.keyboards import time_keyboard, time_call, callbacks_keyboard, yes_no_keyboard
from loader import bot
from utils.db.add import add_notify_time
from utils.db.get import get_user, get_class_manager_by_grade
from utils.menu.user_menu import change_notify_time_call, change_name_call

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}


sent_name_to_confirm_call = CallbackData('sent_name_to_confirm')
fix_name_call = CallbackData('first_name')
confirm_change_name_call = CallbackData('ccn', 'ui', 'f', 'l')


class ChangePersonalData(StatesGroup):
    change_notify_time = State()
    change_first_name = State()
    change_last_name = State()
    confirm = State()


def register_personal_data_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(change_notify_time_start, change_notify_time_call.filter())
    dp.register_callback_query_handler(change_notify_time, time_call.filter(),
                                       state=ChangePersonalData.change_notify_time)
    dp.register_callback_query_handler(change_name_start, change_name_call.filter())
    dp.register_message_handler(get_first_name, state=ChangePersonalData.change_first_name)
    dp.register_message_handler(get_last_name, state=ChangePersonalData.change_last_name)


async def change_notify_time_start(callback: types.CallbackQuery):
    await callback.answer()
    await delete_message(callback.message)
    await callback.message.answer(text='Выберите время для уведомлений', reply_markup=time_keyboard())
    await ChangePersonalData.change_notify_time.set()


async def change_notify_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await callback.message.delete()
    time = int(callback_data.get('data'))
    user_id = callback.from_user.id
    status = add_notify_time(time, user_id)
    if status:
        await callback.message.answer('Установлено время уведомлений с {}:00 по {}:00'.format(str(time), str(time + 1)))
    else:
        await callback.message.answer('Что-то пошло не так.')
    await state.finish()


async def change_name_start(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    class_manager = get_class_manager_by_grade(user['grade'], user['literal'])
    if class_manager.empty:
        await callback.answer('Ваш классный руководитель еще не зарегистрирован.', show_alert=True)
        return
    await callback.message.answer('Введите имя.')
    await ChangePersonalData.change_first_name.set()


async def get_first_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректное имя")
            return
    user = get_user(message.from_user.id)
    class_manager = get_class_manager_by_grade(user['grade'], user['literal'])
    await state.update_data(prev_first_name=user['f_name'])
    await state.update_data(prev_last_name=user['l_name'])
    await state.update_data(first_name=message.text)
    await state.update_data(cm_id=class_manager['admin_id'])
    await message.answer('Введите фамилию.')
    await ChangePersonalData.change_last_name.set()


async def get_last_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректную фамилию")
            return
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    first_name = data.get('first_name')
    last_name = message.text
    markup = callbacks_keyboard(texts=['Отправить', 'Исправить'],
                                callbacks=[sent_name_to_confirm_call.new(), fix_name_call.new()])
    await message.answer('Проверьте данные перед отправкой:\nИмя {}\nФамилия {}'.format(first_name, last_name),
                         reply_markup=markup)
    await ChangePersonalData.confirm.set()


async def confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    text = "Ученик {} {} хочет изменить данные на {} {}\n\nИзменить?".\
        format(data.get('prev_last_name'), data.get('prev_first_name'), data.get('last_name'), data.get('first_name'))
    markup = yes_no_keyboard(callback=confirm_change_name_call.new(u_i=callback.message.from_user.id,
                                                                   f=data.get('first_name'), l=data.get('last_name'),))
    message = await bot.send_message(chat_id=data.get('cm_id'), text=text, reply_markup=markup)
    if message.id:
        await callback.message.answer('Данные отправлены классному руководителю на согласование.')
    else:
        await callback.message.answer('Что-то пошло не так')
    await state.finish()

