import pandas as pd

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters import TimeAccess
from utils.menu.MenuNode import move
from keyboards.keyboards import grad_keyboard, time_call, time_keyboard, literal_keyboard, yes_no_keyboard
from utils.menu.user_menu import add_interest_call, confirm
from utils.db.add import add_user, add_olympiads_to_track, change_files, change_google_docs
from utils.db.get import is_exist, get_olympiads
from utils.menu.menu_structure import list_menu, interest_menu

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}

user_reg_call = CallbackData('user_reg')
personal_data_agreement_call = CallbackData('personal_data_agreement')


class Registration(StatesGroup):
    get_f_name = State()
    get_l_name = State()
    get_grade = State()
    get_literal = State()
    get_interest = State()
    get_notifications_time = State()
    personal_data_agreement = State()


def register_registration_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, user_reg_call.filter(), state='*', chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(get_f_name, state=Registration.get_f_name)
    dp.register_message_handler(get_l_name, state=Registration.get_l_name)
    dp.register_message_handler(get_grade, state=Registration.get_grade)
    dp.register_message_handler(get_literal, state=Registration.get_literal)
    dp.register_callback_query_handler(add_interest, add_interest_call.filter(), state=Registration.get_interest)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state=Registration.get_interest)
    dp.register_callback_query_handler(get_interest, confirm.filter(), state=Registration.get_interest)
    dp.register_callback_query_handler(get_notifications_time, time_call.filter(),
                                       state=Registration.get_notifications_time)
    dp.register_callback_query_handler(personal_data_agreement, personal_data_agreement_call.filter(), TimeAccess(1),
                                       state=Registration.personal_data_agreement)


async def start(callback: types.CallbackQuery):
    status = await is_exist(callback.message.from_user.id)
    if status:
        await callback.answer("Вы уже зарегистрированы")
        return
    await callback.message.delete_reply_markup()
    await callback.message.answer("Введите имя (только имя). Обратите внимание, данные"
                                  " после регистрации нельзя поменять.")
    await Registration.get_f_name.set()


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
    keyword = grad_keyboard()
    await message.answer("Введите номер класса", reply_markup=keyword)
    await state.update_data(l_name=message.text)
    await Registration.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    if message.text.isdigit() and int(message.text) in [x for x in range(3, 12)]:
        await state.update_data(grade=message.text)
        await Registration.get_literal.set()
        reply_markup = literal_keyboard()
        await message.answer('Введите литеру своего класса', reply_markup=reply_markup)
    else:
        await message.answer('Введите корректный номер класса')
        return


async def get_literal(message: types.Message, state: FSMContext):
    if len(message.text) == 1 and message.text.lower() in ru_abc:
        await state.update_data(literal=message.text.upper())
        await Registration.get_interest.set()
        await state.update_data({'interest': set()})
        await list_menu(message, menu=interest_menu, title='Выберете предметы, которыми вы интересуетесь')
    else:
        await message.answer('Введите корректную литеру класса')
        return


async def add_interest(callback: types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    user = str(callback.from_user.id)
    state.storage.data.get(user).get(user).get('data').get('interest').add(callback_data.get('data'))
    await callback.answer('Запомним')


async def get_interest(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    reply_markup = time_keyboard()
    await callback.message.answer('Выберете удобное время для уведомлений', reply_markup=reply_markup)
    await Registration.get_notifications_time.set()


async def get_notifications_time(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    time = int(callback_data.get('data'))
    await callback.answer()
    await callback.message.delete()
    await state.update_data(time=time)
    markup = yes_no_keyboard(callback=personal_data_agreement_call.new())
    url = "https://docs.google.com/document/d/1EgF13-M14QiQZYCjp0U2Eq4Q4B-401YbT9X-n0WJ_iw/edit?usp=sharing"
    await callback.message.answer('''Вы согласны на <a href="{}">обработку персональных данных</a>?'''.format(url),
                                  reply_markup=markup, parse_mode='HTML')
    await Registration.personal_data_agreement.set()


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
    change_files(['users_file'])
    change_google_docs(['users_file'], user.get('grade'), user.get('literal'))
    await callback.message.answer('Регистрация завершена, можете вызвать /menu.')
    await state.finish()


def add_olympiads(interests, user_id, grade):
    olympiads = get_olympiads()
    olympiads_to_add = pd.DataFrame(olympiads[(olympiads['subject_code'].isin(interests)) &
                                              (olympiads['grade'] == int(grade)) & (olympiads['active'])],
                                    columns=olympiads.columns)
    status = add_olympiads_to_track(olympiads_to_add, user_id)
    return olympiads_to_add, status
