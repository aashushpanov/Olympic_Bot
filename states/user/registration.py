from mailbox import Message

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils.db.add import add_user

ru_abc = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф',
          'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}


class Registration(StatesGroup):
	get_f_name = State()
	get_l_name = State()
	get_grade = State()


def register_registration(dp: Dispatcher):
	dp.register_message_handler(start, commands=["регистрация"], state='*')
	dp.register_message_handler(get_f_name, state=Registration.get_f_name)
	dp.register_message_handler(get_l_name, state=Registration.get_l_name)
	dp.register_message_handler(get_grade, state=Registration.get_grade)


async def start(message: types.Message):
	await message.answer("Введите имя")
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
	await message.answer("Введите класс")
	await state.update_data(l_name=message.text)
	await Registration.get_grade.set()


async def get_grade(message: types.Message, state: FSMContext):
	await state.update_data(grade=message.text)
	user = await state.get_data()
	add_user(message.from_user.id, user.get('f_name'), user.get('l_name'), user.get('grade'))
	await message.answer("Регистрация завершена")
