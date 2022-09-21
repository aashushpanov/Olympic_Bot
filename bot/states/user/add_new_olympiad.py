from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from filters.filters import delete_message
from keyboards.keyboards import olympiads_keyboard, olympiad_call, available_grades_keyboard, grade_call, \
    pages_keyboard, page_move_call, pages_keyboard_call
from utils.db.add import add_olympiads_to_track, change_users_files
from utils.db.get import get_olympiads, get_user, get_tracked_olympiads
from utils.menu.menu_structure import list_menu, interest_menu, interest_menu_no_confirm
from utils.menu.user_menu import add_new_olympiad_call, add_interest_call, confirm


class AddOlympiad(StatesGroup):
    choose_subject = State()
    choose_olympiad = State()
    choose_grade = State()


def register_add_new_olympiad_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, add_new_olympiad_call.filter(), state='*')
    dp.register_callback_query_handler(turn_page, page_move_call.filter(), state=AddOlympiad.choose_olympiad)
    dp.register_callback_query_handler(get_olympiad, add_interest_call.filter(), state=AddOlympiad.choose_subject)
    # dp.register_callback_query_handler(get_olympiad, confirm.filter(), state=AddOlympiad.choose_subject)
    dp.register_callback_query_handler(get_grade, olympiad_call.filter(), state=AddOlympiad.choose_olympiad)
    dp.register_callback_query_handler(get_grade, pages_keyboard_call.filter(), state=AddOlympiad.choose_olympiad)
    dp.register_callback_query_handler(add_new_olympiad, grade_call.filter(), state=AddOlympiad.choose_grade)


async def start(callback: types.CallbackQuery, state: FSMContext):
    await AddOlympiad.choose_olympiad.set()
    olympiads = get_olympiads().dropna()
    user_grade = get_user(callback.from_user.id)['grade']
    olympiads = olympiads[(olympiads['is_active'] == 1) & (olympiads['grade'] >= user_grade)]
    if olympiads.empty:
        await callback.answer('Для вашего класса нет доступных олимпиад', show_alert=True)
        await state.finish()
        return
    olympiads_groups = olympiads.sort_values(by=['start_date']).groupby('name', sort=False).first()
    olympiads_groups['name'] = olympiads_groups.index
    olympiads_groups['text'] = olympiads_groups.apply(lambda row: "{} с {}".format(row['name'], row['start_date'].strftime('%d.%m')), axis=1)
    await state.update_data(olympiads=olympiads_groups, page=0)
    message = callback.message
    await delete_message(message)
    markup = pages_keyboard(olympiads_groups, 'name', 'text', 0)
    await message.answer('Выберите олимпиаду', reply_markup=markup)


async def turn_page(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    direction = callback_data.get('data')
    data = await state.get_data()
    page = data['page']
    if direction == 'incr':
        page += 1
    else:
        page -= 1
    await state.update_data(page=page)
    olympiads = data['olympiads']
    markup = pages_keyboard(olympiads, 'name', 'text', page)
    await callback.message.edit_reply_markup(markup)


async def get_subject(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data(subject=callback_data.get('data'))
    await callback.answer('Выбрано')


async def get_olympiad(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    subject = int(callback_data.get('data'))
    await state.update_data(subject=subject)
    await callback.message.delete()
    markup = olympiads_keyboard(subject)
    if len(markup.inline_keyboard):
        await AddOlympiad.choose_olympiad.set()
        await callback.message.answer('Выберете олимпиаду', reply_markup=markup)
    else:
        await callback.message.answer('Олимпиад за этот предмет уже нет.')
        await state.finish()


async def get_grade(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    olympiad_name = callback_data.get('data')
    olympiads = get_olympiads()
    user_grade = get_user(callback.from_user.id)['grade']
    available_grades = set(olympiads[(olympiads['name'] == olympiad_name) & (olympiads['grade'] >= user_grade) &
                                     (olympiads['is_active'] == 1)]['grade'].values)
    if available_grades:
        await state.update_data(olympiad=olympiad_name)
        await AddOlympiad.choose_grade.set()
        await callback.message.delete()
        await callback.message.answer('Выберите класс участия',
                                      reply_markup=available_grades_keyboard(available_grades))
    else:
        await callback.answer('Нет доступных классов', show_alert=True)


async def add_new_olympiad(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = callback.from_user.id
    user = get_user(user_id)
    user_tracked = get_tracked_olympiads(user_id)['olympiad_id'].values
    await callback.message.delete()
    grade = int(callback_data.get('data'))
    data = await state.get_data()
    olympiad_name = data['olympiad']
    olympiads = get_olympiads()
    olympiads = olympiads[(olympiads['name'] == olympiad_name) & (olympiads['grade'] == grade)
                          & (~olympiads['id'].isin(user_tracked))].iloc[:1]
    if not olympiads.empty:
        status = add_olympiads_to_track(olympiads, user_id)
        if status:
            await callback.message.answer('Добавлена в отслеживаемые\n{} за {} класс'.format(olympiads.iloc[0]['name'],
                                                                                             olympiads.iloc[0]['grade']))
            change_users_files(user_id, ['status_file'])
        else:
            await callback.message.answer('При добавлении олимпиад произошла ошибка.')
    else:
        await callback.message.answer('Ничего добавить не удалось, возможно она уже есть')
    await state.finish()
