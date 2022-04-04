from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters import TimeAccess
from utils.menu.MenuNode import move
from keyboards.keyboards import grad_keyboard
from utils.menu.user_menu import add_interest_call, confirm
from utils.db.add import add_user
from utils.db.get import is_exist
from utils.menu.menu_structure import list_menu, interest_menu

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}

reg_callback = CallbackData('reg')


class Registration(StatesGroup):
    get_f_name = State()
    get_l_name = State()
    get_grade = State()
    get_interest = State()


def register_registration(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state='*')
    dp.register_callback_query_handler(start, reg_callback.filter(), state='*', chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(get_f_name, state=Registration.get_f_name)
    dp.register_message_handler(get_l_name, state=Registration.get_l_name)
    dp.register_message_handler(get_grade, state=Registration.get_grade)
    dp.register_callback_query_handler(add_interest, add_interest_call.filter(), state=Registration.get_interest)
    dp.register_callback_query_handler(list_menu, move.filter(), TimeAccess(), state=Registration.get_interest)
    dp.register_callback_query_handler(get_interest, confirm.filter(), state=Registration.get_interest)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")


async def start(callback: types.CallbackQuery):
    status = await is_exist(callback.message.from_user.id)
    if status:
        await callback.answer("Вы уже зарегистрированы")
        return
    await callback.message.delete_reply_markup()
    await callback.message.answer("Введите имя, в любой момент можете написать 'отмена', если не хотите продолжать "
                                  "регистрацию")
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
    await message.answer("Введите класс", reply_markup=keyword)
    await state.update_data(l_name=message.text)
    await Registration.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)
    await Registration.get_interest.set()
    await state.update_data({'interest': set()})
    await list_menu(message, menu=interest_menu, title='Выберете предметы, которыми вы интересуетесь')


async def add_interest(callback: types.CallbackQuery, state: FSMContext, callback_data: dict = None):
    user = str(callback.from_user.id)
    state.storage.data.get(user).get(user).get('data').get('interest').add(callback_data.get('data'))
    await callback.answer('Запомним')


async def get_interest(callback: types.CallbackQuery, state: FSMContext):
    user = await state.get_data()
    await add_user(callback.from_user.id, user.get('f_name'), user.get('l_name'), user.get('grade'), user.get('interest'))
    await callback.message.answer("Регистрация завершена", reply_markup=types.ReplyKeyboardRemove())
    await callback.answer('')
    await state.finish()

