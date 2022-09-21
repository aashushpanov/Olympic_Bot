import pandas as pd
import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from data import config
from data.config import PERSONAL_AGREEMENT
from filters import IsExist, TimeAccess
from filters.filters import delete_message
from keyboards.keyboards import callbacks_keyboard, cansel_keyboard, grad_keyboard, time_keyboard, literal_keyboard, \
    yes_no_keyboard, time_call
from loader import bot
from utils.db.add import set_user_file_format, add_admin, add_olympiads_to_track, add_user, add_class_manager, \
    change_users_files, add_teaching
from utils.db.get import get_access, get_subject, get_olympiads
from utils.files.tables import user_files_update, create_files
from utils.menu.MenuNode import move
from utils.menu.menu_structure import list_menu, interest_menu, interest_menu_no_confirm
from utils.menu.user_menu import add_interest_call, confirm

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', ' '}


reg_call = CallbackData('reg')

admin_reg_call = CallbackData('admin_reg')
reg_admin_deny_call = CallbackData('reg_admin_deny')

user_reg_call = CallbackData('user_reg')
personal_data_agreement_call = CallbackData('personal_data_agreement')

teacher_reg_call = CallbackData('teacher_reg')
add_extra_subject_call = CallbackData('add_extra_subject')
confirm_subjects_call = CallbackData('confirm_subjects')

class_manager_reg_call = CallbackData('class_manager_reg')
skip_registration_call = CallbackData('skip_registration')
get_subject_call = CallbackData('get_subject')
skip_teaching_call = CallbackData('skip_teaching')
rewrite_registration_data_call = CallbackData('rewrite_registration_data')
add_extra_grade_call = CallbackData('add_extra_literal')
confirm_grades_call = CallbackData('confirm_literals')
skip_email_call = CallbackData('skip_email')

confirm_personal_data_call = CallbackData('confirm_personal_data')
restart_registration_call = CallbackData('restart_registration')

class Registration(StatesGroup):
    check_data = State()
    password_check = State()
    start = State()
    get_f_name = State()
    get_l_name = State()
    get_grade = State()
    get_literal = State()
    get_grade_quantity = State()
    ask_teaching = State()
    get_subjects = State()
    get_interest = State()
    confirm_data = State()
    get_notifications_time = State()
    personal_data_agreement = State()
    get_email = State()


def register_registration_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(choose_role, reg_call.filter(), IsExist(0), chat_type=types.ChatType.PRIVATE)

    dp.register_callback_query_handler(clear_registration, class_manager_reg_call.filter())
    dp.register_callback_query_handler(clear_registration, teacher_reg_call.filter())

    dp.register_callback_query_handler(reg_admin_deny, reg_admin_deny_call.filter())

    dp.register_callback_query_handler(start, user_reg_call.filter(), state='*', chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(start, admin_reg_call.filter(), state='*', chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(start, state=Registration.start)

    dp.register_message_handler(get_f_name, state=Registration.get_f_name)
    dp.register_message_handler(get_l_name, state=Registration.get_l_name)

    dp.register_message_handler(get_grade, state=Registration.get_grade)
    dp.register_message_handler(get_literal, state=Registration.get_literal)

    dp.register_message_handler(get_grade_quantity, state=Registration.get_grade_quantity)
    dp.register_callback_query_handler(add_extra_grade, add_extra_grade_call.filter(),
                                       state=Registration.get_literal)
    dp.register_callback_query_handler(add_extra_grade, add_extra_grade_call.filter(),
                                       state=Registration.get_grade_quantity)
    dp.register_callback_query_handler(ask_teaching, confirm_grades_call.filter(),
                                       state=Registration.get_literal)

    dp.register_callback_query_handler(confirm_data, confirm_grades_call.filter(),
                                        state=Registration.get_grade_quantity)
    dp.register_callback_query_handler(confirm_data, get_subject_call.filter(),
                                        state=Registration.ask_teaching)                                  
    # dp.register_callback_query_handler(ask_teaching, confirm_grades_call.filter(),
    #                                    state=Registration.get_grade_quantity)
    # dp.register_callback_query_handler(ask_subject, get_subject_call.filter(),
    #                                    state=Registration.ask_teaching)

    dp.register_callback_query_handler(ask_subject, add_extra_subject_call.filter(), state=Registration.get_literal)
    dp.register_callback_query_handler(get_teaching_subjects, add_interest_call.filter(),
                                       state=Registration.get_subjects)
    dp.register_callback_query_handler(confirm_data, confirm_subjects_call.filter(),
                                       state=Registration.get_literal)
    dp.register_callback_query_handler(confirm_data, skip_teaching_call.filter(),
                                       state=Registration.ask_teaching)                             

    dp.register_callback_query_handler(add_interest, add_interest_call.filter(), state=Registration.get_interest)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state=Registration.get_interest)
    dp.register_callback_query_handler(confirm_data, confirm.filter(), state=Registration.get_interest)
    dp.register_callback_query_handler(start, restart_registration_call.filter(), state='*')

    dp.register_callback_query_handler(ask_notification_time, confirm_personal_data_call.filter(),
                                       state=Registration.confirm_data)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=Registration.get_notifications_time)
    dp.register_callback_query_handler(personal_data_agreement, personal_data_agreement_call.filter(), TimeAccess(1),
                                       state=Registration.personal_data_agreement)

    dp.register_message_handler(get_email, state=Registration.get_email)
    dp.register_callback_query_handler(get_email, skip_email_call.filter(), state=Registration.get_email)


async def choose_role(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    # texts = ['Ученик', 'Учитель', 'Классный руководитель', 'Администратор']
    # callbacks = [user_reg_call.new(), teacher_reg_call.new(), class_manager_reg_call.new()]
    texts = ['Ученик', 'Классный руководитель', 'Администратор']
    callbacks = [user_reg_call.new(), class_manager_reg_call.new()]
    admins = await bot.get_chat_administrators(config.ADMIN_GROUP_ID)
    admins = set([admin['user']['id'] for admin in admins if not admin['user']['is_bot']])
    if callback.from_user.id in admins:
        callbacks.append(admin_reg_call.new())
    else:
        callbacks.append(reg_admin_deny_call.new())
    await callback.message.answer('Выберите должность',
                                  reply_markup=callbacks_keyboard(texts=texts, callbacks=callbacks, cansel_button=True))


async def reg_admin_deny(callback: types.CallbackQuery):
    await callback.answer('У вас недостаточно прав. Обратитесь к ответственному за олимпиадное движение.',
                          show_alert=True)


async def password_check(message: types.Message):
    if get_access(message.from_user.id) == 2:
        await message.answer('Вы уже классный руководитель')
        return
    await message.answer('Введите пароль для доступа к функциям классного руководителя')
    await Registration.check_data.set()


async def clear_registration(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer('Введите пароль', reply_markup=cansel_keyboard())
    prefix = callback_data.get('@')
    if prefix == 'teacher_reg':
        await state.update_data(access=1)
    elif prefix == 'class_manager_reg':
        await state.update_data(access=2)
    await Registration.start.set()


async def start(message: types.Message | types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    match message:
        case types.CallbackQuery():
            await message.answer()
            message = message.message
            async with state.proxy() as data:
                access = data.get('access')
            if access is None:
                prefix = callback_data.get('@')
                if prefix == 'user_reg':
                    access = 0
                    await state.update_data(access=0)
                elif prefix == 'admin_reg':
                    access = 3
                    await state.update_data(access=3)
                else:
                    access = 0
            permission = True
        case types.Message():
            data = await state.get_data()
            access = data.get('access', 0)
            if access == 2 and message.text == config.CLASS_MANAGERS_PASSWORD \
                    or access == 1 and message.text == config.TEACHER_PASSWORD:
                permission = True
            else:
                permission = False
        case _:
            permission = False
            access = 0

    if permission:
        if access == 0:
            await message.answer("Введите имя (только имя). Обратите внимание, данные"
                                 " после регистрации нельзя поменять.")
        else:
            await message.answer("Введите имя и отчество (через пробел)")
        await Registration.get_f_name.set()
    else:
        await message.answer('Неверный пароль. Попробуйте ещё раз.')
        await asyncio.sleep(2)


async def get_f_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректное имя")
            return
    await message.answer("Введите фамилию")
    await state.update_data(f_name=message.text)
    await Registration.get_l_name.set()


async def get_l_name(message: types.Message, state: FSMContext):
    for let in message.text.lower():
        if let not in ru_abc:
            await message.answer("Введите корректную фамилию")
            return
    data = await state.get_data()
    access = data.get('access')
    keyword = grad_keyboard()
    await state.update_data(l_name=message.text)
    if access == 3:
        text = "Подтвердите данные\n\n"
        f_name = data['f_name']
        l_name = message.text
        text += "Имя: {} {}".format(l_name, f_name)
        markup = callbacks_keyboard(texts=['Все верно', "Начать заново"],
                                    callbacks=[confirm_personal_data_call.new(), restart_registration_call.new()])
        await message.answer(text, reply_markup=markup)
        await Registration.confirm_data.set()
        return
    await message.answer("Введите номер класса", reply_markup=keyword)
    if access == 2:
        await state.update_data(grades=[], literals=[], quantity=[])

    if access == 1:
        await Registration.get_subjects.set()
    else:
        await Registration.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    if message.text in [str(x) for x in range(3, 12)]:
        data = await state.get_data()
        access = data.get('access')
        await Registration.get_literal.set()
        reply_markup = literal_keyboard()
        await message.answer("Введите литеру класса.", reply_markup=reply_markup)
        if data.get('current_subject_id'):
            async with state.proxy() as data:
                subject_id = data['current_subject_id']
                data['subjects'][subject_id]['grades'].append(int(message.text))
        elif access == 2:
            grades = data.get('grades')
            grades.append(int(message.text))
            await state.update_data(grades=grades)
        elif access == 0:
            await state.update_data(grade=int(message.text))
    else:
        await message.answer('Введите корректный номер класса')
        return


async def get_literal(message: types.Message, state: FSMContext):
    if len(message.text) == 1 and message.text.lower() in ru_abc:
        data = await state.get_data()
        if data.get('current_subject_id'):
            async with state.proxy() as data:
                subject_id = data['current_subject_id']
                data['subjects'][subject_id]['literals'].append(message.text)
                subjects = data['subjects']
            subjects_list = []
            for subject_id, grades in subjects.items():
                name = get_subject(subject_id)['name']
                grades = ', '.join(
                    [str(grades['grades'][i]) + grades['literals'][i] for i in range(len(grades['grades']))])
                subject_str = f'{name}: {grades}'
                subjects_list.append(subject_str)
            text = 'Выбранные предметы:\n\n{}'.format('\n\n'.join(subjects_list))
            markup = callbacks_keyboard(texts=['Еще один класс', 'Еще один предмет', 'Закончить выбор'],
                                        callbacks=[add_extra_grade_call.new(), add_extra_subject_call.new(),
                                                   confirm_subjects_call.new()])
            await message.answer(text, reply_markup=markup)
        elif data.get('access') == 2:
            async with state.proxy() as data:
                data['literals'].append(message.text.upper())
            await Registration.get_grade_quantity.set()
            await message.answer('Введите численность этого класса')
        elif data.get('access') == 0:
            await state.update_data(literal=message.text.upper())
            await Registration.get_interest.set()
            await state.update_data({'interest': set()})
            await list_menu(message, menu=interest_menu, title='Выберете предметы, которыми вы интересуетесь')
    else:
        await message.answer('Введите корректную литеру класса')
        return


async def get_grade_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer('Неправильный формат численности класса.')
        return
    if 4 < quantity < 50:
        async with state.proxy() as data:
            literals = data['literals']
            grades = data['grades']
            data['quantity'].append(quantity)
            quantity = data['quantity']
        if len(literals) == 1:
            text = 'Выбран класс {}'
        else:
            text = 'Выбранные классы: {}'
        grades = ['{}{}: {}чел.'.format(grades[i], literals[i], quantity[i]) for i in range(len(literals))]
        markup = callbacks_keyboard(texts=['Еще один класс', 'Закончить выбор'],
                                    callbacks=[add_extra_grade_call.new(), confirm_grades_call.new()])
        await message.answer(text.format(', '.join(grades)), reply_markup=markup)
    else:
        await message.answer('Неправильный формат численности класса.')


async def add_extra_grade(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
    reply_markup = grad_keyboard()
    await callback.message.answer('Введите номер дополнительного класса', reply_markup=reply_markup)
    await Registration.get_grade.set()


async def add_interest(callback: types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    async with state.proxy() as data:
        data['interest'].add(callback_data.get('data'))
    # user = str(callback.from_user.id)
    # state.storage.data.get(user).get(user).get('data').get('interest').add(callback_data.get('data'))
    await callback.answer('Запомним')


async def ask_teaching(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.answer()
    texts = ['Добавить', 'Пропустить']
    callbacks = [get_subject_call.new(), skip_teaching_call.new()]
    await Registration.ask_teaching.set()
    reply_markup = callbacks_keyboard(texts=texts, callbacks=callbacks)
    await callback.message.answer('Если вы преподаете в школе, можно добавить отслеживание олимпиад'
                                  ' у ваших учеников по выбранному предмету.', reply_markup=reply_markup)


async def ask_subject(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await delete_message(callback.message)
    await list_menu(callback.message, menu=interest_menu_no_confirm,
                    title='Выберете предмет, который преподаете.')
    await Registration.get_subjects.set()


async def get_teaching_subjects(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await delete_message(callback.message)
    subject_id = callback_data.get('data')
    async with state.proxy() as data:
        if not data.get('subjects'):
            data['subjects'] = {}
        if not data.get('subjects').get(subject_id):
            data['subjects'][subject_id] = {'grades': [], 'literals': []}
        data['current_subject_id'] = subject_id
    keyword = grad_keyboard()
    await Registration.get_grade.set()
    await callback.message.answer("Введите номер класса", reply_markup=keyword)


async def confirm_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    async with state.proxy() as data:
        text = "Подтвердите данные\n\n"
        f_name = data['f_name']
        l_name = data['l_name']
        text += "Имя: {} {}".format(l_name, f_name)

        access = data['access']
        if access == 2:
            grades = data['grades']
            literals = data['literals']
            quantity = data['quantity']
            grades = ['{}{}: {}чел.'.format(grades[i], literals[i], quantity[i]) for i in range(len(literals))]
            text += "\nКлассы: {}".format(', '.join(grades))
        if access == 0:
            grade = data['grade']
            literal = data['literal']
            text += "\nКласс: {}{}".format(grade, literal)
    await callback.answer()
    markup = callbacks_keyboard(texts=['Все верно', "Начать заново"],
                                callbacks=[confirm_personal_data_call.new(), restart_registration_call.new()])
    await callback.message.answer(text, reply_markup=markup)
    await Registration.confirm_data.set()


async def ask_notification_time(callback: types.CallbackQuery):
    await callback.answer()
    await delete_message(callback.message)
    reply_markup = time_keyboard()
    await callback.message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)
    await Registration.get_notifications_time.set()


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await delete_message(callback.message)
    time = int(callback_data.get('data'))
    await callback.message.answer('Выбранное время для уведомлений с {}:00 по {}:00'.format(time, time + 1))
    await state.update_data(time=time)
    data = await state.get_data()
    access = data.get('access')
    if access != 0:
        await Registration.get_email.set()
        markup = callbacks_keyboard(texts=['Пропустить'], callbacks=[skip_email_call.new()])
        await callback.message.answer('Введите почту. (Для подключения Google таблиц)', reply_markup=markup)
    else:
        markup = yes_no_keyboard(callback=personal_data_agreement_call.new())
        url = PERSONAL_AGREEMENT
        await callback.message.answer('''Вы согласны на <a href="{}">обработку персональных данных</a>?'''.format(url),
                                      reply_markup=markup, parse_mode='HTML')
        await Registration.personal_data_agreement.set()


async def get_email(message: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = message.from_user.id
    match message:
        case types.Message():
            email = message.text
            if not email.__contains__('@') or not email.__contains__('.'):
                markup = callbacks_keyboard(texts=['Пропустить'], callbacks=[skip_email_call.new()])
                await message.answer('Введите корректную почту', reply_markup=markup)
                return
        case types.CallbackQuery():
            email = None
            message = message.message
            await delete_message(message)
        case _:
            email = None
    user = await state.get_data()
    access = user.get('access')
    if access == 3:
        status = add_admin(user_id, user['f_name'], user['l_name'], user['time'], email)
        if status:
            await message.answer("Вы зарегистрированы как Администратор."
                                 " Подождите буквально одну минуту пока создаются файлы.")
            await state.finish()
            await create_admins_files(user_id, message)
            # await message.answer("Все готово. Можете вызвать /menu.")
        else:
            await message.answer('Что-то пошло не так.')
            await state.finish()
            return
    if access == 2:
        literals = user.get('literals')
        grades = user.get('grades')
        quantity = user.get('quantity')
        status = add_class_manager(user_id, user['f_name'], user['l_name'], grades, literals, quantity,
                                   user['time'], email)
        if status == 0:
            await message.answer('Что-то пошло не так.')
            await state.finish()
            return
        if user.get('current_subject_id'):
            status = add_teaching(user_id, user['subjects'])
            await create_files(user_id, ['teaching_file'])
            if status:
                subject_texts = []
                for subject_id in user['subjects'].keys():
                    subject_data = user['subjects'][subject_id]
                    grade_list = [str(subject_data['grades'][i]) + subject_data['literals'][i]
                                  for i in range(len(subject_data['grades']))]
                    subject_name = get_subject(subject_id)['name']
                    subject_text = "{} в {}".format(subject_name, ', '.join(grade_list))
                    subject_texts.append(subject_text)
                text = "Вы зарегистрированы как учитель по {}".format('\n'.join(subject_texts))
                await message.answer(text)
            else:
                await message.answer('Не удалось зарегистрировать предметы.')
        await message.answer("Вы зарегистрированы как классный руководитель {}."
                             " Подождите буквально одну минуту пока создаются файлы. Вам придет оповещение."
                             .format(', '.join([str(grades[i]) + literals[i] for i in range(len(literals))])))
        await create_class_managers_files(user_id, message)
        change_users_files(user_id, ['cm_file', 'users_file'])
    if email is not None:
        status = set_user_file_format(user_id, 1)
        if status == 0:
            await message.answer('Что-то пошло не так.')
    # await user_files_update(user_id)
    await message.answer("Все готово, можете вызвать /menu.")
    await state.finish()


async def personal_data_agreement(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    user = await state.get_data()
    try:
        status = add_user(callback.from_user.id, user.get('f_name'), user.get('l_name'), user.get('grade'),
                          user.get('literal'), user.get('interest'), user.get('time'))
    except KeyError:
        await callback.message.answer('Что-то пошло не так')
        return
    if status == 0:
        await callback.message.answer('Что-то пошло не так')
        return
    olympiads_to_add, status = add_olympiads(user.get('interest'), callback.from_user.id, user.get('grade'))
    if status:
        if not olympiads_to_add.empty:
            await callback.message.answer('Следующие олимпиады за ваш класс добавлены в отслеживаемые:\n{}'
                                          .format('\n'.join(list(olympiads_to_add['name']))))
        else:
            await callback.message.answer('К сожалению, олимпиады добавить не удалось')
    else:
        await callback.message.answer('При добавлении олимпиад произошла ошибка.')
    change_users_files(callback.from_user.id, ['users_file'])
    await callback.message.answer('Регистрация завершена, можете вызвать /menu.')
    await state.finish()


def add_olympiads(interests, user_id, grade):
    olympiads = get_olympiads()
    olympiads_to_add = pd.DataFrame(olympiads[(olympiads['subject_id'].isin(list(map(int, interests)))) &
                                              (olympiads['grade'] == int(grade)) & (olympiads['is_active'])],
                                    columns=olympiads.columns)
    status = add_olympiads_to_track(olympiads_to_add, user_id)
    return olympiads_to_add, status


async def create_admins_files(user_id, message):
    file_types = ['users_file', 'status_file', 'subjects_file', 'olympiads_file', 'class_managers_file',
                  'answers_file', 'all_cm_key_file']
    await create_files(user_id, file_types, message)


async def create_class_managers_files(user_id, message):
    file_types = ['users_file', 'status_file', 'cm_key_file']
    await create_files(user_id, file_types, message)
