from aiogram.utils.callback_data import CallbackData

from data.aliases import file_alias
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
set_olympiad_inactive_call = CallbackData('ol_inactive', 'data')
add_olympiad_help_call = CallbackData('add_olympiad_help')
get_key_help_call = CallbackData('get_key_help')


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
            yield MenuNode(file_alias[file['file_type']], callback=get_file_call.new(type=file['file_type']))


def make_get_files_menu(files):
    nodes = []
    for _, file in files.iterrows():
        if file['is_changed']:
            callback = update_file_call.new(type=file['file_type'])
        else:
            callback = file['url']
        nodes.append(MenuNode(file_alias[file['file_type']], callback=callback))
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


# async def get_my_olympiads(node, **kwargs):
#     user_id = kwargs.get('callback').message.chat.id
#     my_olympiads_ids = get_tracked_olympiads(user_id)['olympiad_id'].values
#     user_grade = get_user(user_id)['grade']
#     olympiads = get_olympiads()
#     olympiads = olympiads[olympiads['id'].isin(my_olympiads_ids) & olympiads['is_active'] == 1]
#     if not olympiads.empty:
#         for _, olympiad in olympiads.iterrows():
#             next_node = node.blind_node.id
#             olympiad_grade = olympiad['grade']
#             text = olympiad['name']
#             if user_grade != olympiad_grade:
#                 text += ' (за {} класс)'.format(olympiad_grade)
#             # if olympiad['is_active'] == 0:
#             #     text += ' (прошла)'
#             yield MenuNode(text=text, callback=move.new(action='d', node=next_node, data=olympiad['id'], width=1))
#     else:
#         yield MenuNode('Как добавить олимпиаду', callback=add_olympiad_help_call.new())
#
#
# async def get_my_past_olympiads(node, **kwargs):
#     user_id = kwargs.get('callback').message.chat.id
#     my_olympiads_ids = get_tracked_olympiads(user_id)['olympiad_id'].values
#     user_grade = get_user(user_id)['grade']
#     olympiads = get_olympiads()
#     olympiads = olympiads[olympiads['id'].isin(my_olympiads_ids) & olympiads['is_active'] == 0]
#     if not olympiads.empty:
#         for _, olympiad in olympiads.iterrows():
#             next_node = node.blind_node.id
#             olympiad_grade = olympiad['grade']
#             text = olympiad['name']
#             if user_grade != olympiad_grade:
#                 text += ' (за {} класс)'.format(olympiad_grade)
#             # if olympiad['is_active'] == 0:
#             #     text += ' (прошла)'
#             yield MenuNode(text=text, callback=move.new(action='d', node=next_node, data=olympiad['id'], width=1))
#
#
# async def get_my_olympiads_with_keys(node, **kwargs):
#     user_id = kwargs.get('callback').message.chat.id
#     my_olympiads_ids = get_tracked_olympiads(user_id)['olympiad_id'].values
#     user_grade = get_user(user_id)['grade']
#     olympiads = get_olympiads()
#     olympiads = olympiads[olympiads['id'].isin(my_olympiads_ids) & olympiads['key_needed'] == 1]
#     if not olympiads.empty:
#         for _, olympiad in olympiads.iterrows():
#             olympiad_grade = olympiad['grade']
#             text = olympiad['name']
#             if user_grade != olympiad_grade:
#                 text += ' (за {} класс)'.format(olympiad_grade)
#             if olympiad['is_active'] == 0:
#                 text += ' (прошла)'
#             yield MenuNode(text=text, callback=get_key_call.new(data=olympiad['id']))
#     else:
#         yield MenuNode('Как добавить олимпиаду', callback=add_olympiad_help_call.new())


def get_my_olympiads(list_type):

    def get_callback(call_type, node, olympiad_id):
        if call_type == 'move':
            next_node = node.blind_node.id
            return move.new(action='d', node=next_node, data=olympiad_id, width=1)
        if call_type == 'key':
            return get_key_call.new(data=olympiad_id)

    match list_type:
        case 'current':
            with_inactive = False
            key_needed = -1
            is_active = 1
            call_type = 'move'
        case 'forgotten':
            with_inactive = True
            key_needed = -1
            is_active = 1
            call_type = 'move'
        case 'past':
            with_inactive = False
            key_needed = -1
            is_active = 0
            call_type = 'move'
        case 'with_keys':
            with_inactive = True
            key_needed = 0
            is_active = 1
            call_type = 'key'

    async def list_func(node, **kwargs):
        user_id = kwargs.get('callback').message.chat.id
        my_olympiads_ids = get_tracked_olympiads(user_id, with_inactive=with_inactive)['olympiad_id'].to_list()
        user_grade = get_user(user_id)['grade']
        olympiads = get_olympiads()
        olympiads = olympiads[(olympiads['id'].isin(my_olympiads_ids)) & (olympiads['key_needed'] > key_needed)
                              & (olympiads['is_active'] == is_active)]
        if not olympiads.empty:
            for _, olympiad in olympiads.iterrows():
                olympiad_grade = olympiad['grade']
                olympiad_id = olympiad['id']
                text = olympiad['name']
                if user_grade != olympiad_grade:
                    text += ' (за {} класс)'.format(olympiad_grade)
                if olympiad['is_active'] == 0:
                    text += ' (прошла)'
                yield MenuNode(text=text, callback=get_callback(call_type, node, olympiad_id))
        else:
            yield MenuNode('Как добавить олимпиаду', callback=add_olympiad_help_call.new())
    return list_func


async def register_olympiads_options(node, **kwargs):
    callback = kwargs.get('callback')
    olympiad_id = kwargs.get('data')
    olympiad = get_olympiad(olympiad_id)
    node.text = olympiad['name']
    stage = olympiad['stage']
    olympiad_status = get_olympiad_status(callback.from_user.id, olympiad_id, stage)
    reg_url = olympiad['urls'].get('reg_url')
    site_url = olympiad['urls'].get('site_url')
    ol_url = olympiad['urls'].get('ol_url')
    nodes = []
    if olympiad['pre_registration'] and olympiad_status['status_code'] == 0 and reg_url and olympiad['is_active']:
        nodes.append(MenuNode(text='Зарегистрироваться', callback=reg_url))
    if site_url:
        nodes.append(MenuNode(text='Сайт олимпиады', callback=site_url))
    if ol_url and olympiad['is_active']:
        nodes.append(MenuNode(text='Пройти олимпиаду', callback=ol_url))
    if olympiad['key_needed'] and olympiad['keys_count'] and olympiad['is_active']:
        nodes.append(MenuNode(text='Получить ключ', callback=get_key_call.new(data=olympiad_id)))
    if olympiad['pre_registration'] and olympiad_status['status_code'] == 0 and olympiad['is_active']:
        nodes.append(MenuNode(text='Подтвердить регистрацию',
                              callback=confirm_registration_question_call.new(data=olympiad_id)))
    if olympiad_status['status_code'] == 1 and olympiad['is_active']:
        nodes.append(MenuNode(text='Подтвердить участие',
                              callback=confirm_execution_question_call.new(data=olympiad_id)))
    nodes.append(MenuNode(text='Узнать даты проведения', callback=get_dates_call.new(data=olympiad_id)))
    if olympiad_status['is_active'] == 1:
        nodes.append(MenuNode('Забыть эту олимпиаду', callback=set_olympiad_inactive_call.new(data=olympiad_id)))
    for node in nodes:
        yield node

