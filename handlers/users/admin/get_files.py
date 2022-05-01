from aiogram import Dispatcher, types
from aiogram.types import InputFile

from states.admin.set_olympiad import get_dates_template_file_call, SetOlympiads, get_olympiads_template_file_call, \
    get_subjects_template_file_call, make_subjects_template, make_olympiads_template
from utils.db.add import set_file_ids
from utils.db.get import get_file
from utils.files.data_files import make_olympiads_status_file, make_olympiads_with_dates_file, make_answers_file, \
    make_users_file
from utils.files.templates import make_olympiads_dates_template, make_subjects_file
from utils.menu.admin_menu import get_olympiads_file_call, get_subjects_file_call, get_status_file_call, \
    get_answer_file_call, get_users_file_call, get_cm_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_status_file, get_status_file_call.filter())
    dp.register_callback_query_handler(send_users_file, get_users_file_call.filter())
    dp.register_callback_query_handler(send_cm_file, get_cm_file_call.filter())
    dp.register_callback_query_handler(send_olympiads_with_dates_file, get_olympiads_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_subjects_file, get_subjects_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_olympiads_template_file, get_olympiads_template_file_call.filter(),
                                       state='*')
    dp.register_callback_query_handler(send_dates_template_file, get_dates_template_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_subjects_template_file, get_subjects_template_file_call.filter(), state='*')
    dp.register_callback_query_handler(send_answers_file, get_answer_file_call.filter(), state='*')


async def send_users_file(callback: types.CallbackQuery):
    await send_file(callback, 'users_file')


async def send_cm_file(callback: types.CallbackQuery):
    await send_file(callback, 'cm_file')


async def send_olympiads_with_dates_file(callback: types.CallbackQuery):
    await send_file(callback, 'olympiads_file')


async def send_olympiads_template_file(callback: types.CallbackQuery):
    await send_file(callback, 'olympiads_template')


async def send_subjects_file(callback: types.CallbackQuery):
    await send_file(callback, 'subjects_file')


async def send_subjects_template_file(callback: types.CallbackQuery):
    await send_file(callback, 'subjects_template')


async def send_dates_template_file(callback: types.CallbackQuery):
    await send_file(callback, 'dates_template')


async def send_status_file(callback: types.CallbackQuery):
    await send_file(callback, 'status_file')


async def send_answers_file(callback: types.CallbackQuery):
    await send_file(callback, 'answers_file')


async def send_file(callback, file_type):
    file_status = get_file(file_type)
    if file_status['changed']:
        match file_type:
            case 'users_file':
                file_path = make_users_file()
            case 'cm_file':
                file_path = make_users_file(users_type='class_manager')
            case 'status_file':
                file_path = make_olympiads_status_file()
            case 'olympiads_file':
                file_path = make_olympiads_with_dates_file()
            case 'olympiads_template':
                file_path = make_olympiads_template()
                await SetOlympiads.received_olympiads_template.set()
            case 'dates_template':
                file_path = make_olympiads_dates_template()
                await SetOlympiads.received_dates_template.set()
            case 'subjects_file':
                file_path = make_subjects_file()
            case 'subjects_template':
                file_path = make_subjects_template()
                await SetOlympiads.received_subject_template.set()
            case 'answers_file':
                file_path = make_answers_file()
            case _:
                raise KeyError
        file = InputFile(file_path)
        message = await callback.message.answer_document(file)
        file_id = message.document.file_id
        file_unique_id = message.document.file_unique_id
        set_file_ids(file_type, file_id, file_unique_id)
    else:
        await callback.message.answer_document(file_status['file_id'])
    await callback.answer()

