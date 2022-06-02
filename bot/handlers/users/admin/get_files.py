from aiogram import Dispatcher, types
from aiogram.types import InputFile

from filters.filters import IsAdmin
from states.admin.set_olympiad import SetOlympiads, make_subjects_template, make_olympiads_template
from utils.db.add import set_file_ids
from utils.db.get import get_file
from utils.files.data_files import make_olympiads_status_file, make_olympiads_with_dates_file, make_answers_file, \
    make_users_file, make_class_managers_file
from utils.files.templates import make_olympiads_dates_template, make_subjects_file
from utils.menu.generator_functions import get_file_call


def register_get_files_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_file, get_file_call.filter(), IsAdmin(), state='*')


async def send_file(callback: types.CallbackQuery, callback_data: dict):
    file_type = callback_data.get('type')
    file_status = get_file(file_type)
    if file_status['changed']:
        match file_type:
            case 'users_file':
                file_path, _ = make_users_file()
            case 'cm_file':
                file_path, _ = make_class_managers_file()
            case 'status_file':
                file_path, _ = make_olympiads_status_file()
            case 'olympiads_file':
                file_path, _ = make_olympiads_with_dates_file()
            case 'olympiads_template':
                file_path, _ = make_olympiads_template()
                await SetOlympiads.received_olympiads_template.set()
            case 'dates_template':
                file_path, _ = make_olympiads_dates_template()
                await SetOlympiads.received_dates_template.set()
            case 'subjects_file':
                file_path, _ = make_subjects_file()
            case 'subjects_template':
                file_path, _ = make_subjects_template()
                await SetOlympiads.received_subject_template.set()
            case 'answers_file':
                file_path, _ = make_answers_file()
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

