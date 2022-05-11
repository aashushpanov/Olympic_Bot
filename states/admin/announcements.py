import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters import IsAdmin
from keyboards.keyboards import cansel_keyboard, callbacks_keyboard
from loader import bot
from utils.db.get import get_file, get_users, get_olympiads, get_all_olympiads_status, get_class_managers
from utils.menu.admin_menu import announcement_call, grade_announcement_call, subject_announcement_call, \
    olympiad_announcement_call, cm_announcement_call

send_announcement_call = CallbackData('send_announcement')
fix_announcement_call = CallbackData('fix_announcement', 'data')


class Announcement(StatesGroup):
    everybody = State()
    by_grade = State()
    by_olympiad = State()
    by_subject = State()
    by_cm = State()
    confirm = State()


def register_announcement_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(everybody_start, announcement_call.filter())
    dp.register_callback_query_handler(by_grade_start, grade_announcement_call.filter())
    dp.register_callback_query_handler(by_olympiad_start, olympiad_announcement_call.filter())
    dp.register_callback_query_handler(by_subject_start, subject_announcement_call.filter())
    dp.register_callback_query_handler(by_cm_start, cm_announcement_call.filter())
    dp.register_message_handler(receive_announcement, IsAdmin(), state=Announcement.all_states)
    dp.register_callback_query_handler(sending_confirm, send_announcement_call.filter(), state=Announcement.confirm)
    dp.register_callback_query_handler(fix_announcement, fix_announcement_call.filter(), state=Announcement.confirm)


async def everybody_start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer('Введите объявление для всех \U00002B07.', reply_markup=cansel_keyboard())
    await Announcement.everybody.set()


async def by_grade_start(callback: types.CallbackQuery):
    await callback.answer()
    markup = callbacks_keyboard(texts=['Посмотреть пример'], callbacks=[get_file('grade_announcement_example')['url']],
                                cansel_button=True)
    await callback.message.answer('Введите объявление для одного или нескольких классов \U00002B07.'
                                  ' Формат сообщения можно посмотреть в примере', reply_markup=markup)
    await Announcement.by_grade.set()


async def by_olympiad_start(callback: types.CallbackQuery):
    await callback.answer()
    markup = callbacks_keyboard(texts=['Посмотреть пример'],
                                callbacks=[get_file('olympiad_announcement_example')['url']],
                                cansel_button=True)
    await callback.message.answer('Введите объявление для одной или нескольких олимпиад \U00002B07.'
                                  ' Формат сообщения можно посмотреть в примере', reply_markup=markup)
    await Announcement.by_olympiad.set()


async def by_subject_start(callback: types.CallbackQuery):
    await callback.answer()
    markup = callbacks_keyboard(texts=['Посмотреть пример'],
                                callbacks=[get_file('subject_announcement_example')['url']],
                                cansel_button=True)
    await callback.message.answer('Введите объявление для одного или нескольких предметов \U00002B07.'
                                  ' Формат сообщения можно посмотреть в примере', reply_markup=markup)
    await Announcement.by_subject.set()


async def by_cm_start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer('Введите объявление для всех классных руководителей \U00002B07.',
                                  reply_markup=cansel_keyboard())
    await Announcement.by_cm.set()


async def receive_announcement(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    announcement = {}
    messages = {}
    match current_state:
        case 'Announcement:everybody':
            user_list = tuple(get_users()['user_id'].to_list())
            announcement = {user_list: message.text}
            messages = {'Всем': message.text}
            current_state = 'AnnouncementEverybody'
        case 'Announcement:by_grade':
            messages = parsing_by_grade(message.text)
            users = get_users()
            announcement = {}
            for grade, text in messages.items():
                user_list = tuple(users[users['grade'] == grade])
                announcement[user_list] = text
            current_state = 'AnnouncementByGrade'
        case 'Announcement:by_olympiad':
            messages = parsing_by_olympiad(message.text)
            announcement = {}
            olympiads = get_olympiads()
            olympiads_status = get_all_olympiads_status()
            for olympiad_name, text in messages.items():
                olympiad_codes = olympiads[olympiads['name'] == olympiad_name]['code'].to_list()
                user_list = tuple(olympiads_status[olympiads_status['olympiad_code'].isin(olympiad_codes)]
                                  ['user_id'].to_list())
                announcement[user_list] = text
            current_state = 'AnnouncementByOlympiad'
        case 'Announcement:by_subject':
            messages = parsing_by_subject(message.text)
            announcement = {}
            users = get_users()
            for subject, text in messages.items():
                user_list = tuple(users[subject in users['interest']])
                announcement[user_list] = text
            current_state = 'AnnouncementBySubject'
        case 'Announcement:by_cm':
            user_list = tuple(get_class_managers()['admin_id'].to_list())
            announcement = {user_list: message.text}
            messages = {'Классным руководителям': message.text}
            current_state = 'AnnouncementByCm'
        case _:
            pass
    await state.update_data(announcement=announcement)
    markup = callbacks_keyboard(texts=['Отправить', 'Исправить'],
                                callbacks=[send_announcement_call.new(), fix_announcement_call.new(data=current_state)])
    message_list = ['({}):\n{}'.format(target, message) for target, message in messages.items()]
    await message.answer("Проверьте правильность сообщений:\n{}".format('\n\n'.join(message_list)), reply_markup=markup)
    await Announcement.confirm.set()


async def sending_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    for users, message in data.get('announcement').items():
        for user in users:
            await bot.send_message(chat_id=user, text=message)
            await asyncio.sleep(0.04)
        await callback.message.answer('Отправка завершена.')


async def fix_announcement(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    await callback.message.delete_reply_markup()
    prev_state = callback_data.get('data')
    match prev_state:
        case 'AnnouncementEverybody':
            await Announcement.everybody.set()
            file_name = ''
        case 'AnnouncementByGrade':
            await Announcement.by_grade.set()
            file_name = 'grade_announcement_example'
        case 'AnnouncementByOlympiad':
            await Announcement.by_olympiad.set()
            file_name = 'olympiad_announcement_example'
        case 'AnnouncementBySubject':
            await Announcement.by_subject.set()
            file_name = 'subject_announcement_example'
        case 'AnnouncementByCm':
            await Announcement.by_cm.set()
            file_name = ''
        case _:
            await state.finish()
            file_name = ''
    if file_name != '':
        markup = callbacks_keyboard(texts=['Посмотреть пример'],
                                    callbacks=[get_file(file_name)['url']],
                                    cansel_button=True)
    else:
        markup = None
    await callback.message.answer('Отправьте объявление еще раз.', reply_markup=markup)


def parsing_by_grade(message):
    messages = message.split('\n\n')
    message_by_grade = {}
    for message in messages:
        grades = message.split('\n')[0][:-1]
        if grades.__contains__(','):
            grades = grades.split(',')
            grades = [int(grade) for grade in grades]
        elif grades.__contains__('-'):
            grades_borders = grades.split('-')
            grades = [grade for grade in range(int(grades_borders[0]), int(grades_borders[1]) + 1)]
        else:
            grades = [int(grades)]
        text = '\n'.join(message.split('\n')[1:])
        for grade in grades:
            message_by_grade[grade] = text
    return message_by_grade


def parsing_by_olympiad(message):
    messages = message.split('\n\n')
    message_by_olympiad = {}
    for message in messages:
        olympiad = message.split('\n')[0][:-1]
        text = '\n'.join(message.split('\n')[1:])
        message_by_olympiad[olympiad] = text
    return message_by_olympiad


def parsing_by_subject(message):
    messages = message.split('\n\n')
    message_by_subject = {}
    for message in messages:
        subject = message.split('\n')[0][:-1]
        text = '\n'.join(message.split('\n')[1:])
        message_by_subject[subject] = text
    return message_by_subject
