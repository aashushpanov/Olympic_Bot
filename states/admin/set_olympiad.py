import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd

from filters import IsAdmin, TimeAccess
from states.admin.admin_menu import set_olympiads_call, set_subjects_call
from utils.db.add import add_olympiads


class SetOlympiads(StatesGroup):
    load_file = State()


class SetSubjects(StatesGroup):
    load_file = State()


def set_olympiads_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_subjects_call.filter(), IsAdmin(), TimeAccess(), state='*')
    dp.register_message_handler(load_subj_file, state=SetSubjects.load_file, content_types=types.ContentTypes.DOCUMENT)
    dp.register_callback_query_handler(start, set_olympiads_call.filter(), IsAdmin(), TimeAccess(), state='*')
    dp.register_message_handler(load_ol_file, state=SetOlympiads.load_file, content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    await callback.message.answer('Загрузите файл')
    if callback.data == 'set_subjects':
        await SetSubjects.load_file.set()
    else:
        await SetOlympiads.load_file.set()


async def read_file(file_path, document):
    await document.download(
        destination_file=file_path,
    )
    file = pd.read_csv(file_path, sep=';')
    if len(file.columns) == 1:
        file = pd.read_csv(file_path, sep=',')
    return file


async def load_ol_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_data.csv'
        olympiads = await read_file(file_path, document)
        add, existing, subject_not_existing = await add_olympiads(olympiads=olympiads)
        if existing:
            await message.answer('Олимпиады с этими кодами уже существуют:\n {}'.format(', '.join(existing)))
        if subject_not_existing:
            await message.answer('Следующих предметов нет в списке:\n {}'.format(', '.join(subject_not_existing)))
        if add:
            await message.answer('Следующие олимпиады успешно добавлены:\n {}'.format(', '.join(add)))
        else:
            await message.answer('Произошла ошибка')
        os.remove(file_path)
        await state.finish()


async def load_subj_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/subject_data.csv'
        subjects = await read_file(file_path, document)
        add, existing, _ = await add_olympiads(subjects=subjects)
        if existing:
            await message.answer('Предметы с этими кодами уже существуют:\n {}'.format(', '.join(existing)))
        if add:
            await message.answer('Следующие предметы успешно добавлены:\n {}'.format(', '.join(add)))
        else:
            await message.answer('Произошла ошибка')
        os.remove(file_path)
    await state.finish()

