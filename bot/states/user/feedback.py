import pandas as pd
import datetime as dt
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data import config
from keyboards.keyboards import cansel_keyboard
from loader import bot
from utils.db.add import add_question, change_users_files
from utils.db.get import get_user, get_admin
from utils.menu.user_menu import question_to_admin_call


class AddQuestion(StatesGroup):
    admin_question = State()


def register_questions_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, question_to_admin_call.filter())
    dp.register_message_handler(receive_question, state=AddQuestion.admin_question)


async def start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer('Опишите проблему максимально точно и, при необходимости, укажите название '
                                  'олимпиады.\n\nНапишите вопрос здесь \U00002B07', reply_markup=cansel_keyboard())
    await AddQuestion.admin_question.set()


async def receive_question(message: types.Message, state: FSMContext):
    question_text = message.text
    user = get_user(message.from_user.id)
    grade = user['grade']
    literal = user['literal']
    question_from = '{} {} из {} спрашивает:\n\n'.format(user['l_name'], user['f_name'],
                                                         str(grade) + literal)
    index = ['user_id', 'question', 'user_message_id', 'date']
    date = dt.date.today()
    user_message_id = message.message_id
    question = pd.Series([message.from_user.id, question_from + question_text, user_message_id, date], index=index)
    question_no, status = add_question(question)
    if status:
        await message.answer('Вопрос зарегистрирован по номером {}, подождите пока администратор на него ответит.'.
                             format(question_no))
        text = 'Задан вопрос: {}\n\n{}'.format(question_no, question['message'])
        await bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=text)
        change_users_files(None, ['answers_file'])
    else:
        await message.answer('Что-то пошло не так.')
    await state.finish()

