import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import pandas as pd

from filters import IsAdmin, TimeAccess
from states.admin.admin_menu import set_olympiads_call
from utils.db.add import add_olympiads


class SetOlympiads(StatesGroup):
    load_file = State()


def set_olympiads_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start, set_olympiads_call.filter(), IsAdmin(), TimeAccess(), state='*')
    dp.register_message_handler(load_file, state=SetOlympiads.load_file, content_types=types.ContentTypes.DOCUMENT)


async def start(callback: types.CallbackQuery):
    await callback.message.answer('Загрузите файл')
    await SetOlympiads.load_file.set()


async def load_file(message: types.Message, state: FSMContext):
    if document := message.document:
        file_path = 'data/files/from_admin/olympiads_data.csv'
        await document.download(
            destination_file=file_path,
        )
        olympiads = pd.read_csv(file_path, sep=';')
        existing = await add_olympiads(olympiads)
        await message.answer('Олимпиады с этими кодами уже существуют:\n {}'.format(', '.join(existing)))
        os.remove(file_path)

