from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.keyboards import olympiads_keyboard, olympiad_call, available_grades_keyboard, grade_call
from utils.db.add import add_olympiads_to_track
from utils.db.get import get_olympiads, get_user, get_tracked_olympiads
from utils.menu.menu_structure import list_menu, interest_menu
from utils.menu.user_menu import add_new_olympiad_call, add_interest_call, confirm


class AddOlympiad(StatesGroup):
    choose_subject = State()
    choose_olympiad = State()
    choose_grade = State()


def register_add_new_olympiad_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, add_new_olympiad_call.filter(), state='*')
    dp.register_callback_query_handler(get_subject, add_interest_call.filter(), state=AddOlympiad.choose_subject)
    dp.register_callback_query_handler(get_olympiad, confirm.filter(), state=AddOlympiad.choose_subject)
    dp.register_callback_query_handler(get_grade, olympiad_call.filter(), state=AddOlympiad.choose_olympiad)
    dp.register_callback_query_handler(add_new_olympiad, grade_call.filter(), state=AddOlympiad.choose_grade)


async def start(callback: types.CallbackQuery, state: FSMContext):
    await AddOlympiad.choose_subject.set()
    message = callback.message
    await message.delete()
    await list_menu(message, menu=interest_menu, title='Выберете предмет. Будет учитываться последний выбранный вами '
                                                       'предмет')


async def get_subject(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data(subject=callback_data.get('data'))
    await callback.answer('Выбрано')


async def get_olympiad(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data('subject')
    subject = data['subject']
    if subject is None:
        return
    await AddOlympiad.choose_olympiad.set()
    await callback.message.delete()
    await callback.message.answer('Выберете олимпиаду', reply_markup=olympiads_keyboard(subject))


async def get_grade(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    olympiad_name = callback_data.get('data')
    olympiads = get_olympiads()
    user_grade = get_user(callback.from_user.id)['grade'].item()
    available_grades = set(olympiads[(olympiads['name'] == olympiad_name) & (olympiads['grade'] >= user_grade)]['grade']
                           .values)
    if available_grades:
        await state.update_data(olympiad=olympiad_name)
        await AddOlympiad.choose_grade.set()
        await callback.message.delete()
        await callback.message.answer('Выберете класс участия',
                                      reply_markup=available_grades_keyboard(available_grades))
    else:
        await callback.answer('Нет доступных классов')


async def add_new_olympiad(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = callback.from_user.id
    user_tracked = get_tracked_olympiads(user_id)['olympiad_code'].values
    await callback.message.delete()
    grade = int(callback_data.get('data'))
    data = await state.get_data()
    olympiad_name = data['olympiad']
    olympiads = get_olympiads()
    olympiads = olympiads[(olympiads['name'] == olympiad_name) & (olympiads['grade'] == grade)
                          & (~olympiads['code'].isin(user_tracked))].iloc[:1]
    if not olympiads.empty:
        add_olympiads_to_track(olympiads, user_id)
        await callback.message.answer('Добавлена в отслеживаемые {} за {} класс'.format(olympiads.iloc[0]['name'],
                                                                                        olympiads.iloc[0]['grade']))
    else:
        await callback.message.answer('Ничего добавить не удалось, возможно она уже есть')
    await state.finish()
