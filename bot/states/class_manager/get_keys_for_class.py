import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from filters.filters import delete_message
from keyboards.keyboards import pages_keyboard, available_grades_keyboard, page_move_call, pages_keyboard_call, \
    grade_call, callbacks_keyboard
from loader import bot
from utils.db.add import get_keys_to_cm, add_key_label, change_users_files
from utils.db.get import get_olympiads, get_class_managers_grades, get_cm_keys_limit, get_access, get_admin_keys_limit
from utils.menu.admin_menu import get_keys_to_admin_call
from utils.menu.class_manager_menu import get_key_for_class_call


give_labels_call = CallbackData('give_labels')
skip_labels_call = CallbackData('skip_labels')


class GetKeysForClass (StatesGroup):
    choose_olympiad = State()
    choose_grade = State()
    chose_keys_quantity = State()
    get_keys = State()


def register_get_keys_for_class_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, get_key_for_class_call.filter())
    dp.register_callback_query_handler(start, get_keys_to_admin_call.filter())
    dp.register_callback_query_handler(turn_page, page_move_call.filter(), state=GetKeysForClass.choose_olympiad)
    dp.register_callback_query_handler(get_olympiad, pages_keyboard_call.filter(), state=GetKeysForClass.choose_olympiad)
    dp.register_callback_query_handler(get_grade, grade_call.filter(), state=GetKeysForClass.choose_grade)
    dp.register_message_handler(get_quantity, state=GetKeysForClass.chose_keys_quantity)
    dp.register_callback_query_handler(send_keys, skip_labels_call.filter(), state=GetKeysForClass.get_keys)
    dp.register_callback_query_handler(send_key, give_labels_call.filter(), state=GetKeysForClass.get_keys)
    dp.register_message_handler(send_key, state=GetKeysForClass.get_keys)


async def start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await GetKeysForClass.choose_olympiad.set()
    olympiads = get_olympiads().dropna()
    olympiads = olympiads[olympiads['is_active'] == 1]
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


async def get_olympiad(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    olympiad_name = callback_data.get('data')
    olympiads = get_olympiads()
    access = get_access(callback.from_user.id)
    if access == 2:
        cm_grades = get_class_managers_grades(callback.from_user.id)['grade_num'].to_list()
        cm_grades = cm_grades + [grade for grade in range(max(cm_grades) + 1, max(cm_grades) + 4)]
        available_grades = set(olympiads[(olympiads['name'] == olympiad_name) & (olympiads['grade'].isin(cm_grades))]['grade']
                               .values)
    elif access == 3:
        available_grades = set(olympiads[olympiads['name'] == olympiad_name]['grade'].values)
    else:
        available_grades = []
    if available_grades:
        await state.update_data(olympiad=olympiad_name)
        await GetKeysForClass.choose_grade.set()
        await callback.message.delete()
        await callback.message.answer('Выберите класс',
                                      reply_markup=available_grades_keyboard(available_grades))
    else:
        await callback.answer('Нет доступных классов', show_alert=True)


async def get_grade(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    data = await state.get_data()
    access = get_access(callback.from_user.id)
    if access == 2:
        key_limit, olympiad_id = get_cm_keys_limit(callback.from_user.id, data['olympiad'], callback_data.get('data'))
    elif access == 3:
        key_limit, olympiad_id = get_admin_keys_limit(data['olympiad'], callback_data.get('data'))
    else:
        key_limit = 0
        olympiad_id = 1
    if key_limit == 0:
        await callback.answer('Нет возможности взять ключ для данного класса. Возможно закончились ключи, либо Вы '
                              'исчерпали лимит.', show_alert=True)
        await state.finish()
        await delete_message(callback.message)
        return
    await state.update_data(key_limit=key_limit, olympiad_id=olympiad_id)
    await callback.message.answer('Вам доступно не более {} ключей. Введите количество ключей, которое надо выдать'.format(key_limit))
    await GetKeysForClass.chose_keys_quantity.set()


async def get_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key_limit = data.get('key_limit')
    try:
        key_needed = int(message.text)
    except ValueError:
        await message.answer('Неверный формат для количества ключей')
        return
    if key_limit < key_needed:
        await message.answer('Вы выбрали больше ключей, чем доступно ({}). Введите корректное количество ключей'.format(key_limit))
        return
    await state.update_data(key_needed=key_needed)
    texts = ['Дать метки', 'Просто получить ключи']
    callbacks = [give_labels_call.new(), skip_labels_call.new()]
    markup = callbacks_keyboard(texts, callbacks)
    await message.answer('Ходите дать выданным ключам имена? (Например, чтобы не забыть, кому будет выдан каждый ключ).',
                         reply_markup=markup)
    await GetKeysForClass.get_keys.set()


async def send_key(callback: types.CallbackQuery | types.Message, state: FSMContext):
    data = await state.get_data()
    olympiad_id = data.get('olympiad_id')
    key_needed = data.get('key_needed', 0)
    match callback:
        case types.CallbackQuery():
            message = callback.message
            await delete_message(message)
        case _:
            message = callback
            current_key_id = data.get('current_key_id')
            label = message.text
            status = add_key_label(message.from_user.id, current_key_id, label)
            if not status:
                await message.answer('Не удалось добавить метку.')
    if key_needed == 0:
        change_users_files(callback.from_user.id, ['cm_key_file'])
        change_users_files(None, ['all_cm_key_file'])
        await message.answer("Вы можете посмотреть все взятые ключи в файле 'Список ключей'.")
        await state.finish()
        return
    keys, key_ids, status = get_keys_to_cm(callback.from_user.id, olympiad_id, 1)
    if status:
        await state.update_data(current_key_id=key_ids[0], key_needed=key_needed-1)
        texts = ['Пропустить метки']
        callbacks = [skip_labels_call.new()]
        markup = callbacks_keyboard(texts, callbacks)
        await message.answer(keys[0])
        await message.answer('Введите метку для этого ключа', reply_markup=markup)


async def send_keys(callback: types.CallbackQuery, state: FSMContext):
    await delete_message(callback.message)
    data = await state.get_data()
    key_needed = data.get('key_needed')
    olympiad_id = data.get('olympiad_id')
    keys, _, status = get_keys_to_cm(callback.from_user.id, olympiad_id, key_needed)
    if status:
        for key in keys:
            await bot.send_message(chat_id=callback.from_user.id, text=key)
            await asyncio.sleep(0.04)
        await callback.message.answer("Вы можете посмотреть все взятые ключи в меню 'Взятые ключи'.")
    else:
        await callback.message.answer('Что-то пошло не так.')
    change_users_files(callback.from_user.id, ['cm_key_file'])
    change_users_files(None, ['all_cm_key_file'])
    await state.finish()




