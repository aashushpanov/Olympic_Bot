from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from keyboards.keyboards import time_keyboard, callbacks_keyboard, time_call
from utils.db.add import add_admin
from utils.google_sheets.create import create_file, user_files_update

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', ' '}


admin_reg_call = CallbackData('admin_reg')
skip_email_admin_call = CallbackData('skip_email_admin')


class RegistrationAdmin(StatesGroup):
    get_f_name = State()
    get_l_name = State()
    get_notifications_time = State()
    get_email = State()


def register_registration_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, admin_reg_call.filter())
    dp.register_message_handler(get_f_name, state=RegistrationAdmin.get_f_name)
    dp.register_message_handler(get_l_name, state=RegistrationAdmin.get_l_name)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=RegistrationAdmin.get_notifications_time)
    dp.register_message_handler(get_email, state=RegistrationAdmin.get_email)
    dp.register_callback_query_handler(get_email, skip_email_admin_call.filter(), state=RegistrationAdmin.get_email)


async def start(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.message.answer("Введите имя и отчество (через пробел).")
    await RegistrationAdmin.get_f_name.set()


async def get_f_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректное имя")
            return
    await message.answer("Введите фамилию")
    await state.update_data(f_name=message.text)
    await RegistrationAdmin.get_l_name.set()


async def get_l_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректную фамилию")
            return
    await state.update_data(l_name=message.text)
    reply_markup = time_keyboard()
    await message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)
    await RegistrationAdmin.get_notifications_time.set()


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    time = int(callback_data.get('data'))
    await state.update_data(time=time)
    await RegistrationAdmin.get_email.set()
    markup = callbacks_keyboard(texts=['Пропустить'], callbacks=[skip_email_admin_call.new()])
    await callback.message.answer('Введите почту. (Для подключения Google таблиц)', reply_markup=markup)


async def get_email(message: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = message.from_user.id
    match message:
        case types.Message():
            email = message.text
        case types.CallbackQuery():
            email = ''
            message = message.message
        case _:
            email = ''
    user = await state.get_data()
    add_admin(user_id, user['f_name'], user['l_name'], user['time'], email)
    await message.answer("Вы зарегистрированы как Администратор. Подождите буквально одну минуту пока создаются файлы.")
    await state.finish()
    create_admins_files(user_id)
    user_files_update(user_id)
    await message.answer("Все готово. Можете вызвать /menu.")


def create_admins_files(user_id):
    file_types = ['users_file', 'status_file', 'subjects_file', 'olympiads_file', 'class_managers_file', 'answers_file']
    create_file(user_id, file_types)
