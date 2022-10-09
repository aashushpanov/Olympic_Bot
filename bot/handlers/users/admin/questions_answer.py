from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData

from data import config
from filters import IsAdmin
from fone_tasks.updates import show_admin_question_call
from loader import bot
from utils.db.add import add_question_answer, add_questions_admin_message_id, change_users_files
from utils.db.get import get_new_questions, get_question, get_admin

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
            question_id = question['id']
            text = 'Номер вопроса: {}\n\n{}'.format(question_id, question['question'])
            message = await callback.message.answer(text=text)
            message_id = message.message_id
            questions.loc[index, 'admin_message_id'] = message_id
        add_questions_admin_message_id(questions)
    else:
        await callback.message.answer('Вопросов нет')


async def question_answer(message: types.Message):
    if message.reply_to_message:
        message_to_reply = message.reply_to_message
        question_id = message_to_reply.text.split('\n')[0].split(' ')[-1]
        question = get_question(question_id)
        if question.empty:
            return
        if question['answer'] == '':
            answer = message.text
            admin_id = message.from_user.id
            status = add_question_answer(question_id, answer, admin_id)
            if status:
                new_text = '{}\n\nОтвет: {}'.format(message_to_reply.text, answer)
                await bot.edit_message_text(text=new_text, message_id=message_to_reply.message_id,
                                            chat_id=config.ADMIN_GROUP_ID)
                await bot.delete_message(message_id=message.message_id, chat_id=config.ADMIN_GROUP_ID)
                user_id = question['from_user']
                admin = get_admin(admin_id)
                text = 'Ответ на ваш вопрос номер {} от {} {}:\n\n{}'.format(question_id, admin.get('last_name', 'Администратор'),
                                                                             admin.get('first_name', ''), answer)
                chat = types.Chat(id=user_id)
                user_message = types.Message(message_id=question['user_message_id'], chat=chat)
                await user_message.reply(text=text)
                # await bot.forward_message(chat_id=user_id, text=text)
                change_users_files(None, ['answers_file'])
            else:
                await message.answer('Что-то пошло не так.')
        else:
            await message.answer('На этот вопрос уже ответили')
            await message.delete()









