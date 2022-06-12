from aiogram.utils.callback_data import CallbackData

from utils.db.get import get_admin, get_olympiads_by_status, get_olympiads, get_subjects, get_user, \
    get_tracked_olympiads, get_olympiad, get_olympiad_status, get_user_google_files, get_user_excel_files
from utils.menu.MenuNode import MenuNode, move

get_key_call = CallbackData('get_key', 'data')
get_dates_call = CallbackData('get_time', 'data')
confirm_registration_question_call = CallbackData('confirm_registration_qw', 'data')
confirm_execution_question_call = CallbackData('confirm_execution_qw', 'data')
del_interest_call = CallbackData('del_subj', 'data')
get_file_call = CallbackData('get_file', 'type')
update_file_call = CallbackData('update_file', 'type')

files_alias = {'users_file': 'Список учеников', 'status_file': 'Статус прохождения олимпиад',
               'subjects_file': 'Список предметов', 'olympiads_file': 'Список олимпиад',
               'class_managers_file': 'Список классных руководителей', 'answers_file': 'Список вопросов'}


async def get_download_options(_, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    admin = get_admin(user_id)
    if admin['to_google_sheets']:
        files = get_user_google_files(user_id)
        nodes = make_get_files_menu(files)
        for node in nodes:
            yield node
    else:
        files = get_user_excel_files(user_id)
        for _, file in files.iterrows():
            yield MenuNode(files_alias[file['file_type']], callback=get_file_call.new(type=file['file_type']))


def make_get_files_menu(files):
    nodes = []
    for _, file in files.iterrows():
        if file['is_changed']:
            callback = update_file_call.new(type=file['file_type'])
        else:
            callback = file['url']
        nodes.append(MenuNode(files_alias[file['file_type']], callback=callback))
    return nodes


async def get_olympiad_registrations(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    user_olympiads = list(get_olympiads_by_status(user_id=user_id, status_code='reg')['olympiad_code'].values)
    olympiads = get_olympiads()
    olympiads = olympiads[olympiads['code'].isin(user_olympiads)]
    for olympiad in olympiads.iterrows():
        next_node = node.blind_node.id
        yield MenuNode(text=olympiad['name'], callback=move.new(action='d', node=next_node, data=olympiad['id']))


async def get_interests(_, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    subjects = get_subjects()
    user_interests = list(get_user(user_id)['interest'])
    interests_df = subjects[subjects['id'].isin(user_interests)]
    for _, interest in interests_df.iterrows():
        yield MenuNode(text=interest['subject_name'], callback=del_interest_call.new(data=interest['id']))


async def get_my_olympiads(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    my_olympiads_ids = get_tracked_olympiads(user_id)['olympiad_id'].values
    user_grade = get_user(user_id)['grade']
    olympiads = get_olympiads()
    olympiads = olympiads[olympiads['id'].isin(my_olympiads_ids)]
    if not olympiads.empty:
        for _, olympiad in olympiads.iterrows():
            next_node = node.blind_node.id
            olympiad_grade = olympiad['grade']
            text = olympiad['name']
            if user_grade != olympiad_grade:
                text += ' (за {} класс)'.format(olympiad_grade)
            if olympiad['is_active'] == 0:
                text += ' (прошла)'
            yield MenuNode(text=text, callback=move.new(action='d', node=next_node, data=olympiad['id'], width=1))


async def register_olympiads_options(_, **kwargs):
    callback = kwargs.get('callback')
    olympiad_id = kwargs.get('data')
    olympiad = get_olympiad(olympiad_id)
    stage = olympiad['stage']
    olympiad_status = get_olympiad_status(callback.from_user.id, olympiad_id, stage)
    reg_url = olympiad['urls'].get('reg_url')
    site_url = olympiad['urls'].get('site_url')
    nodes = []
    if olympiad['pre_registration'] and olympiad_status['status'] == 'idle' and reg_url and olympiad['active']:
        nodes.append(MenuNode(text='Зарегистрироваться', callback=reg_url))
    if site_url:
        nodes.append(MenuNode(text='Сайт олимпиады', callback=site_url))
    if olympiad['key_needed'] and olympiad['keys_count'] and olympiad['active']:
        nodes.append(MenuNode(text='Получить ключ', callback=get_key_call.new(data=olympiad_id)))
    if olympiad['pre_registration'] and olympiad_status['status'] == 'idle' and olympiad['active']:
        nodes.append(MenuNode(text='Подтвердить регистрацию',
                              callback=confirm_registration_question_call.new(data=olympiad_id)))
    if olympiad_status['status'] == 'reg' and olympiad['active']:
        nodes.append(MenuNode(text='Подтвердить участие',
                              callback=confirm_execution_question_call.new(data=olympiad_id)))
    nodes.append(MenuNode(text='Узнать даты проведения', callback=get_dates_call.new(data=olympiad_id)))
    for node in nodes:
        yield node
