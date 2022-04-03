from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode, move, NodeGenerator
from utils.db.get import get_olympiad_status, get_subjects

call = CallbackData('2', 'data')
add_interest_call = CallbackData('add_olympiad', 'data')
confirm = CallbackData('confirm')


async def get_olympiad_registrations(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    olympiads = await get_olympiad_status(user_id=user_id, status='reg')
    for olympiad in olympiads:
        next_node = node.blind_node.id
        yield MenuNode(text=olympiad[0], callback=move.new(action='d', node=next_node, data=olympiad[0]))


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
        MenuNode('user_0_0'),
        MenuNode('user_0_1'),
        MenuNode('user_0_1')
    ])

    user_menu.child(text='Олимпиады').set_childs([
        NodeGenerator(text='Регистрации', func=get_olympiad_registrations),
        MenuNode('user_1_1'),
        MenuNode('user_1_2')
    ])

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
    # меню выбора олимпиад
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
    olympiad_interest_menu.set_child(MenuNode(text='Готово', callback=confirm.new()))

    for _, child in olympiad_interest_menu.childs().items():
        section_subjects = subjects[subjects['section'] == child.text]
        for _, subject in section_subjects.iterrows():
            child.set_child(MenuNode(text=subject['subject_name'],
                                     callback=add_interest_call.new(data=subject['code'])))

    return olympiad_interest_menu

