from mailbox import Message

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils.db.add import add_user


class Registration(StatesGroup):
    get_f_name = State()
    get_l_name = State()
    get_grade = State()


def register_registration(dp: Dispatcher):
    dp.register_message_handler(start, comands="регистрация", state='*')
    dp.register_message_handler(get_f_name, state=Registration.get_f_name)
    dp.register_message_handler(get_l_name, state=Registration.get_l_name)
    dp.register_message_handler(get_grade, state=Registration.get_grade)


async def start(message: types.Message):
    await message.answer("Введите имя")
    await Registration.get_l_name.set()


async def get_f_name(message: types.Message, state: FSMContext):
    await message.answer("Введите фамилию")
    await Registration.get_f_name.set()


async def get_l_name(message: types.Message, state: FSMContext):
    await message.answer("Введите класс")
    await Registration.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
    user = await state.get_data()
    add_user(message.from_user.id, user.get('get_f_name'), user.get('get_l_name'), user.get('get_grade'))
    await message.answer("Регистрация завершена")
