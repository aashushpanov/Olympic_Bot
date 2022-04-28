from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import IsExist
from keyboards.keyboards import callbacks_keyboard, grad_keyboard, literal_keyboard, time_keyboard, time_call
from utils.db.add import add_class_manager, change_files
from utils.db.get import get_user, get_access

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}

skip_registration_call = CallbackData('skip_registration')
rewrite_registration_data_call = CallbackData('rewrite_registration_data')
add_extra_literal_call = CallbackData('add_extra_literal')
confirm_literals_call = CallbackData('confirm_literals')


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
    dp.register_callback_query_handler(add_extra_literal, add_extra_literal_call.filter(),
                                       state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(confirm_literals, confirm_literals_call.filter(),
                                       state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=RegistrationClassManager.get_notifications_time)
    dp.register_callback_query_handler(quick_registration, skip_registration_call.filter(),
                                       state=RegistrationClassManager.start)


async def password_check(message: types.Message):
    if get_access(message.from_user.id) == 1:
        await message.answer('Вы уже классный руководитель')
        return
    await message.answer('Введите пароль для доступа к функциям классного руководителя')
    await RegistrationClassManager.start.set()


async def start(message: types.Message, state: FSMContext):
    if message.text == config.CLASS_MANAGERS_PASSWORD:
        user = get_user(message.from_user.id)
        grade = 'Класс: {}'.format(str(user['grade']) + user['literal'])
        first_name = 'Имя: {}'.format(user['first_name'])
        last_name = 'Фамилия: {}'.format(user['last_name'])
        markup = callbacks_keyboard(texts=['Продолжить с этими данными', 'Ввести данные заново'],
                                    callbacks=[skip_registration_call.new(), rewrite_registration_data_call.new()])
        await message.answer("Ваши данные:\n{}\n{}\n{}".format(last_name, first_name, grade), reply_markup=markup)
    else:
        await message.answer('Неверный пароль')


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
        await state.update_data(literal=[])
        await message.answer("Введите литеру своего класса. Если у вас их несколько, просто добавляйте по очереди. В "
                             "конце нажмите 'далее'.", reply_markup=reply_markup)
    else:
        await message.answer('Введите корректный номер класса')
        return


async def get_literal(message: types.Message, state: FSMContext):
    if len(message.text) == 1 and message.text.lower() in ru_abc:
        data = await state.get_data()
        literals = data.get('literal')
        literals.append(message.text)
        await state.update_data(literal=literals)
        markup = callbacks_keyboard(texts=['Дальше'],
                                    callbacks=[confirm_literals_call.new()])
        if len(literals) == 1:
            text = 'Выбран {} класс'
        else:
            text = 'Выбраны {} классы'
        grades = [str(data['grade']) + literal for literal in literals]
        await message.answer(text.format(', '.join(grades)), reply_markup=markup)
    else:
        await message.answer('Введите корректную литеру класса')
        return


async def add_extra_literal(callback: types.CallbackQuery, state: FSMContext):
    reply_markup = literal_keyboard()
    await callback.message.answer('Введите литеру дополнительного класса', reply_markup=reply_markup)


async def confirm_literals(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await RegistrationClassManager.get_notifications_time.set()
    reply_markup = time_keyboard()
    await callback.message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    time = int(callback_data.get('data'))
    await callback.answer()
    user = await state.get_data()
    user_id = callback.from_user.id
    literal = ''.join(user['literal'])
    add_class_manager(user_id, user['f_name'], user['l_name'], user['grade'], literal, time)
    await callback.message.answer("Вы зарегистрированы как классный руководитель {}. Можете вызвать /menu"
                                  .format(', '.join([str(user['grade']) + literal for literal in user['literal']])))
    await state.finish()
    change_files(['users_file'])


async def quick_registration(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    user = get_user(user_id)
    add_class_manager(user_id, user['first_name'], user['last_name'], user['grade'],
                      user['literal'], user['notify_time'])
    await callback.message.answer("Вы зарегистрированы как классный руководитель {}. Можете вызвать /menu"
                                  .format(str(user['grade']) + user['literal']))
    await state.finish()
    change_files(['users_file'])
