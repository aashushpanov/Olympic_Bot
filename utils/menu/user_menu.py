from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode, move, NodeGenerator
from utils.db.get import get_olympiads_by_status, get_subjects, get_user, get_olympiads, get_olympiad, \
    get_olympiad_status, get_tracked_olympiads

call = CallbackData('2', 'data')
add_interest_call = CallbackData('add_olympiad', 'data')
add_new_interests_call = CallbackData('add_new_interest')
confirm = CallbackData('confirm')
del_interest_call = CallbackData('del_subj', 'data')
get_key_call = CallbackData('get_key', 'data')
get_dates_call = CallbackData('get_time', 'data')
add_new_olympiad_call = CallbackData('add_new_olympiad')
confirm_registration_question_call = CallbackData('confirm_registration_qw', 'data')
confirm_execution_question_call = CallbackData('confirm_execution_qw', 'data')


async def get_olympiad_registrations(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    user_olympiads = list(get_olympiads_by_status(user_id=user_id, status='reg')['olympiad_code'].values)
    olympiads = get_olympiads()
    olympiads = olympiads[olympiads['code'].isin(user_olympiads)]
    for olympiad in olympiads.iterrows():
        next_node = node.blind_node.id
        yield MenuNode(text=olympiad['name'], callback=move.new(action='d', node=next_node, data=olympiad['code']))


async def get_interests(_, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    subjects = get_subjects()
    user_interests = list(get_user(user_id)['interest'].item())
    interests_df = subjects[subjects['code'].isin(user_interests)]
    for _, interest in interests_df.iterrows():
        yield MenuNode(text=interest['subject_name'], callback=del_interest_call.new(data=interest['code']))


async def get_my_olympiads(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    my_olympiads_codes = get_tracked_olympiads(user_id)['olympiad_code'].values
    user_grade = get_user(user_id)['grade'].item()
    olympiads = get_olympiads()
    olympiads = olympiads[olympiads['code'].isin(my_olympiads_codes)]
    for _, olympiad in olympiads.iterrows():
        next_node = node.blind_node.id
        olympiad_grade = olympiad['grade']
        if user_grade != olympiad_grade:
            text = olympiad['name'] + ' (за {} класс)'.format(olympiad_grade)
        else:
            text = olympiad['name']
        yield MenuNode(text=text, callback=move.new(action='d', node=next_node, data=olympiad['code'], width=1))


async def register_olympiads_options(_, **kwargs):
    callback = kwargs.get('callback')
    olympiad_code = kwargs.get('data')
    olympiad = get_olympiad(olympiad_code)
    stage = olympiad['stage'].item()
    olympiad_status = get_olympiad_status(callback.from_user.id, olympiad_code, stage)
    reg_url = olympiad['urls'].item().get('reg_url')
    site_url = olympiad['urls'].item().get('site_url')
    nodes = []
    if olympiad['pre_registration'].item() and olympiad_status['status'] == 'idle' and reg_url:
        nodes.append(MenuNode(text='Зарегистрироваться', callback=reg_url))
    if site_url:
        nodes.append(MenuNode(text='Сайт олимпиады', callback=site_url))
    if olympiad['key_needed'].item():
        nodes.append(MenuNode(text='Получить ключ', callback=get_key_call.new(data=olympiad_code)))
    if olympiad['pre_registration'].item() and olympiad_status['status'] == 'idle':
        nodes.append(MenuNode(text='Подтвердить регистрацию', callback=confirm_registration_question_call.new(data=olympiad_code)))
    if olympiad_status['status'] == 'reg':
        nodes.append(MenuNode(text='Подтвердить участие', callback=confirm_execution_question_call.new(data=olympiad_code)))
    nodes.append(MenuNode(text='Узнать даты проведения', callback=get_dates_call.new(data=olympiad_code)))
    for node in nodes:
        yield node


def set_user_menu(main_node=None, root_id='0.1'):
    # главное меню
    # -------------------------------------------------------
    user_menu = MenuNode(text="Меню ученика", id=root_id)
    if main_node:
        main_node.set_child(user_menu)

    user_menu.set_childs([
        MenuNode('Личные данные'),
        MenuNode('Олимпиады'),
        MenuNode('user_2')
    ])

    user_menu.child(text='Личные данные').set_childs([
        MenuNode('Добавить предметы', callback=add_new_interests_call.new()),
        NodeGenerator('Удалить предметы', func=get_interests),
        MenuNode('user_0_1')
    ])

    user_menu.child(text='Личные данные').child(text='Удалить предметы').add_blind_node('del_subj')

    user_menu.child(text='Олимпиады').set_childs([
        NodeGenerator(text='Список моих олимпиад', func=get_my_olympiads),
        MenuNode('Добавить отдельные олимпиады', callback=add_new_olympiad_call.new()),
        NodeGenerator('Регистрации', func=get_olympiad_registrations)
    ])

    user_menu.child(text='Олимпиады').child(text='Список моих олимпиад').add_blind_node('list_olymp', type='generator',
                                                                                        func=register_olympiads_options)
    user_menu.child(text='Олимпиады').child(text='Список моих олимпиад').blind_node.add_blind_node('ol_opt')

    user_menu.child(text='Олимпиады').child(text='Регистрации').add_blind_node('reg_olymp')
    user_menu.child(text='Олимпиады').child(text='Регистрации').set_sub_childs([
        MenuNode('Выполнить', callback=call.new(data='')),
        MenuNode('Забыть', callback=call.new(data=''))
    ])

    user_menu.child(text='user_2').set_childs([
        MenuNode('user_2_0'),
        MenuNode('user_2_1'),
        MenuNode('user_2_2')
    ])
    return user_menu


def set_interest_menu(root_node=None):
    # меню выбора предметов
    # --------------------------------------------------------------------------------------------------------
    if root_node is None:
        olympiad_interest_menu = MenuNode(text='Выбор предметов', id='o_interest')
    else:
        olympiad_interest_menu = root_node

    subjects = get_subjects()
    for _, subject in subjects.iterrows():
        if subject['section'] == 'Базовый':
            olympiad_interest_menu.set_child(MenuNode(text=subject['subject_name'],
                                                      callback=add_interest_call.new(data=subject['code'])))
    for section in subjects[subjects['section'].notna()].groupby(['section']).groups.keys():
        if section != 'Базовый':
            olympiad_interest_menu.set_child(MenuNode(text=section))
    olympiad_interest_menu.set_child(MenuNode(text='\U00002705 Готово', callback=confirm.new()))

    for _, child in olympiad_interest_menu.childs().items():
        section_subjects = subjects[subjects['section'] == child.text]
        for _, subject in section_subjects.iterrows():
            child.set_child(MenuNode(text=subject['subject_name'],
                                     callback=add_interest_call.new(data=subject['code'])))

    return olympiad_interest_menu
