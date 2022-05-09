from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import IsAdmin
from fone_tasks.updates import show_admin_question_call
from loader import bot
from utils.db.add import set_message_id_to_questions, add_question_answer, change_files, change_google_docs
from utils.db.get import get_new_questions, get_question, get_user

question_answer_call = CallbackData('q_a', 'no', 'id')


def register_questions_answer_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_questions, show_admin_question_call.filter(),
                                       is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)
    dp.register_message_handler(question_answer, IsAdmin(), is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)


async def show_questions(callback: types.CallbackQuery):
    await callback.answer()
    questions = get_new_questions()
    if not questions.empty:
        for index, question in questions.iterrows():
            question_no = question['no']
            text = 'Номер вопроса: {}\n\n{}'.format(question_no, question['message'])
            message = await callback.message.answer(text=text)
            message_id = message.message_id
            questions.loc[index, 'message_id'] = message_id
        set_message_id_to_questions(questions)
    else:
        await callback.message.answer('Вопросов нет')


async def question_answer(message: types.Message):
    if message.reply_to_message:
        message_to_reply = message.reply_to_message
        question_no = message_to_reply.text.split('\n')[0].split(' ')[-1]
        question = get_question(question_no)
        if question.empty:
            return
        if question['answer'] == '':
            answer = message.text
            admin_id = message.from_user.id
            add_question_answer(question_no, answer, admin_id)
            new_text = '{}\n\nОтвет: {}'.format(message_to_reply.text, answer)
            await bot.edit_message_text(text=new_text, message_id=message_to_reply.message_id,
                                        chat_id=config.ADMIN_GROUP_ID)
            await bot.delete_message(message_id=message.message_id, chat_id=config.ADMIN_GROUP_ID)
            user_id = question['from_user']
            admin = get_user(admin_id)
            text = 'Ответ на ваш вопрос номер {} от {} {}:\n\n{}'.format(question_no, admin['last_name'],
                                                                         admin['first_name'], answer)
            await bot.send_message(chat_id=user_id, text=text)
            change_files(['answers_file'])
            change_google_docs(['answers_file'])
        else:
            await message.answer('На этот вопрос уже ответили')
            await message.delete()









