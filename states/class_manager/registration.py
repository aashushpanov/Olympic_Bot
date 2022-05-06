from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import IsExist
from keyboards.keyboards import callbacks_keyboard, grad_keyboard, literal_keyboard, time_keyboard, time_call, \
    cansel_keyboard
from utils.db.add import add_class_manager, change_files, class_manager_migrate
from utils.db.get import get_user, get_access, get_admin
from utils.google_sheets.create import create_file, user_files_update

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', ' '}

class_manager_reg_call = CallbackData('class_manager_reg')
skip_registration_call = CallbackData('skip_registration')
rewrite_registration_data_call = CallbackData('rewrite_registration_data')
add_extra_grade_call = CallbackData('add_extra_literal')
confirm_grades_call = CallbackData('confirm_literals')
skip_email = CallbackData('skip_email')


class RegistrationClassManager(StatesGroup):
    start = State()
    check_data = State()
    get_f_name = State()
    get_l_name = State()
    get_grade = State()
    get_literal = State()
    get_notifications_time = State()
    get_email = State()


def register_registration_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(clear_registration, class_manager_reg_call.filter())
    dp.register_message_handler(start, state=RegistrationClassManager.start)
    dp.register_message_handler(password_check, IsExist(), commands=['classroom_teacher'])
    dp.register_message_handler(check_data, IsExist(), state=RegistrationClassManager.check_data)
    dp.register_callback_query_handler(rewrite_registration, rewrite_registration_data_call.filter(),
                                       state=RegistrationClassManager.start)
    dp.register_message_handler(get_f_name, state=RegistrationClassManager.get_f_name)
    dp.register_message_handler(get_l_name, state=RegistrationClassManager.get_l_name)
    dp.register_message_handler(get_grade, state=RegistrationClassManager.get_grade)
    dp.register_message_handler(get_literal, state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(add_extra_grade, add_extra_grade_call.filter(),
                                       state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(confirm_grades, confirm_grades_call.filter(),
                                       state=RegistrationClassManager.get_literal)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=RegistrationClassManager.get_notifications_time)
    dp.register_message_handler(get_email, state=RegistrationClassManager.get_email)
    dp.register_callback_query_handler(get_email, skip_email.filter(), state=RegistrationClassManager.get_email)
    dp.register_callback_query_handler(quick_registration, skip_registration_call.filter(),
                                       state=RegistrationClassManager.start)


async def password_check(message: types.Message):
    if get_access(message.from_user.id) == 1:
        await message.answer('Вы уже классный руководитель')
        return
    await message.answer('Введите пароль для доступа к функциям классного руководителя')
    await RegistrationClassManager.check_data.set()


async def check_data(message: types.Message):
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


async def clear_registration(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Введите пароль', reply_markup=cansel_keyboard())
    await RegistrationClassManager.start.set()


async def start(message: types.Message):
    if message.text == config.CLASS_MANAGERS_PASSWORD:
        await message.answer("Введите имя и отчество (через пробел)")
        await RegistrationClassManager.get_f_name.set()
    else:
        await message.answer('Неверный пароль.')


async def rewrite_registration(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await callback.message.answer("Введите имя и отчество (через пробел)")
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
    await message.answer("Введите номер класса. ", reply_markup=keyword)
    await state.update_data(l_name=message.text)
    await state.update_data(grades=[])
    await state.update_data(literals=[])
    await RegistrationClassManager.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    if int(message.text) in [x for x in range(3, 12)]:
        data = await state.get_data()
        grades = data.get('grades')
        grades.append(int(message.text))
        await state.update_data(grades=grades)
        await RegistrationClassManager.get_literal.set()
        reply_markup = literal_keyboard()
        await message.answer("Введите литеру своего класса.", reply_markup=reply_markup)
    else:
        await message.answer('Введите корректный номер класса')
        return


async def get_literal(message: types.Message, state: FSMContext):
    if len(message.text) == 1 and message.text.lower() in ru_abc:
        data = await state.get_data()
        literals = data.get('literals')
        grades = data.get('grades')
        literals.append(message.text)
        await state.update_data(literals=literals)
        markup = callbacks_keyboard(texts=['Еще один класс', 'Дальше'],
                                    callbacks=[add_extra_grade_call.new(), confirm_grades_call.new()])
        if len(literals) == 1:
            text = 'Выбран {} класс'
        else:
            text = 'Выбраны {} классы'
        grades = [str(grades[i]) + literals[i] for i in range(len(literals))]
        await message.answer(text.format(', '.join(grades)), reply_markup=markup)
    else:
        await message.answer('Введите корректную литеру класса')
        return


async def add_extra_grade(callback: types.CallbackQuery):
    reply_markup = grad_keyboard()
    await callback.message.answer('Введите номер дополнительного класса', reply_markup=reply_markup)
    await RegistrationClassManager.get_grade.set()


async def confirm_grades(callback: types.CallbackQuery):
    await callback.answer()
    await RegistrationClassManager.get_notifications_time.set()
    reply_markup = time_keyboard()
    await callback.message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    time = int(callback_data.get('data'))
    await state.update_data(time=time)
    await RegistrationClassManager.get_email.set()
    markup = callbacks_keyboard(texts=['Пропустить'], callbacks=[skip_email.new()])
    await callback.message.answer('Введите почту. (Для подключения Google таблиц)', reply_markup=markup)


async def get_email(message: types.Message | types.CallbackQuery, state: FSMContext):
    match message:
        case types.Message():
            email = message.text
        case types.CallbackQuery:
            email = ''
            message = message.message
        case _:
            email = ''
    user = await state.get_data()
    literals = user.get('literals')
    grades = user.get('grades')
    user_id = message.from_user.id
    add_class_manager(user_id, user['f_name'], user['l_name'], grades, literals, user['time'], email)
    await message.answer("Вы зарегистрированы как классный руководитель {}. Можете вызвать /menu"
                         .format(', '.join([str(grades[i]) + literals[i] for i in range(len(literals))])))
    await state.finish()
    create_class_managers_files(user_id)
    user_files_update(user_id)
    change_files(['cm_file', 'users_file'])


async def quick_registration(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    class_manager_migrate(user_id)
    user = get_admin(user_id)
    await callback.message.answer("Вы зарегистрированы как классный руководитель {}. Можете вызвать /menu"
                                  .format(str(user['grade'][0]) + user['literal'][0]))
    await state.finish()
    create_class_managers_files(user_id)
    user_files_update(user_id)
    change_files(['cm_file', 'users_file'])


def create_class_managers_files(user_id):
    file_types = ['users_file', 'status_file']
    for file_type in file_types:
        create_file(user_id, file_type)
