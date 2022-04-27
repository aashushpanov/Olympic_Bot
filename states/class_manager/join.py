from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import IsExist
from keyboards.keyboards import callbacks_keyboard, grad_keyboard, literal_keyboard, time_keyboard, time_call
from states.user.registration import ru_abc
from utils.db.add import add_class_manager
from utils.db.get import get_user


skip_registration_call = CallbackData('skip_registration')
rewrite_registration_data_call = CallbackData('rewrite_registration_data')


class RegistrationClassManager(StatesGroup):
    start = State()
    get_f_name = State()
    get_l_name = State()
    get_grade = State()
    get_literal = State()
    get_notifications_time = State()


def register_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(password_check, IsExist(), commands=['classroom_teacher'])
    dp.register_message_handler(start, IsExist(), state=RegistrationClassManager.start)
    dp.register_callback_query_handler(rewrite_registration, rewrite_registration_data_call.filter(),
                                       state=RegistrationClassManager.start)
    dp.register_message_handler(get_f_name, state=RegistrationClassManager.get_f_name)
    dp.register_message_handler(get_l_name, state=RegistrationClassManager.get_l_name)
    dp.register_message_handler(get_grade, state=RegistrationClassManager.get_grade)
    dp.register_message_handler(get_literal, state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=RegistrationClassManager.get_notifications_time)
    dp.register_callback_query_handler(quick_registration, skip_registration_call.filter(),
                                       state=RegistrationClassManager.start)


async def password_check(message: types.Message):
    await message.answer('Введите пароль для доступа к функциям классного руководителя')
    await RegistrationClassManager.start.set()


async def start(message: types.Message, state: FSMContext):
    if message.text == config.CLASS_MANAGERS_PASSWORD:
        user = get_user(message.from_user.id)
        grade = 'Класс:{}'.format(str(user['grade']) + user['literal'])
        first_name = 'Имя:'.format(user['first_name'])
        last_name = 'Фамилия'.format(user['last_name'])
        markup = callbacks_keyboard(texts=['Продолжить с этими данными', 'Ввести данные заново'],
                                    callbacks=[skip_registration_call.new(), rewrite_registration_data_call.new()])
        await message.answer("Ваши данные:\n{}\n{}\n{}".format(last_name, first_name, grade), reply_markup=markup)


async def rewrite_registration(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("Введите имя (только имя)")
    await RegistrationClassManager.get_f_name.set()


async def get_f_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректное имя")
            return
    await message.answer("Введите фамилию")
    await state.update_data(f_name=message.text)
    await RegistrationClassManager.get_l_name.set()


async def get_l_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректную фамилию")
            return
    keyword = grad_keyboard()
    await message.answer("Введите номер класса", reply_markup=keyword)
    await state.update_data(l_name=message.text)
    await RegistrationClassManager.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    if int(message.text) in [x for x in range(3, 12)]:
        await state.update_data(grade=message.text)
        await RegistrationClassManager.get_literal.set()
        reply_markup = literal_keyboard()
        await message.answer('Введите литеру своего класса', reply_markup=reply_markup)
    else:
        await message.answer('Введите корректный номер класса')
        return


async def get_literal(message: types.Message, state: FSMContext):
    if len(message.text) == 1 and message.text.lower() in ru_abc:
        await state.update_data(literal=message.text.upper())
        await RegistrationClassManager.get_notifications_time.set()
        reply_markup = time_keyboard()
        await message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)
    else:
        await message.answer('Введите корректную литеру класса')
        return


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    time = int(callback_data.get('data'))
    await callback.answer()
    user = await state.get_data()
    user_id = callback.from_user.id
    add_class_manager(user_id, user['first_name'], user['last_name'], user['grade'], user['literal'], time)
    await callback.message.answer('Вы зарегистрированы как классный руководитель {}'
                                  .format(str(user['grade']) + user['literal']))
    await state.finish()


async def quick_registration(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user = get_user(user_id)
    add_class_manager(user_id, user['first_name'], user['last_name'], user['grade'],
                      user['literal'], user['notify_time'])
    await callback.message.answer('Вы зарегистрированы как классный руководитель {}'
                                  .format(str(user['grade']) + user['literal']))
    await state.finish()
