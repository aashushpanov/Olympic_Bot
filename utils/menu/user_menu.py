from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode, NodeGenerator
from utils.db.get import get_subjects
from utils.menu.generator_functions import get_interests, get_my_olympiads, register_olympiads_options


add_interest_call = CallbackData('add_olympiad', 'data')
add_new_interests_call = CallbackData('add_new_interest')
confirm = CallbackData('confirm')
add_new_olympiad_call = CallbackData('add_new_olympiad')
question_to_admin_call = CallbackData('question_to_admin')
change_notify_time_call = CallbackData('change_notify_time')
get_nearest_olympiads_call = CallbackData('get_nearest_olympiads')
show_personal_data_call = CallbackData('show_personal_data')
change_name_call = CallbackData('change_personal_data')


def set_user_menu(main_node=None, root_id='0.1'):
    # главное меню
    # -------------------------------------------------------
    user_menu = MenuNode(text="Меню ученика", id=root_id)
    if main_node:
        main_node.set_child(user_menu)

    user_menu.set_childs([
        MenuNode('Личные данные'),
        MenuNode('Олимпиады'),
        MenuNode('Обратная связь')
    ])

    user_menu.child(text='Личные данные').set_childs([
        MenuNode('Личные данные', callback=show_personal_data_call.new()),
        MenuNode('Изменить данные', callback=change_name_call.new()),
        MenuNode('Добавить предметы', callback=add_new_interests_call.new()),
        NodeGenerator('Удалить предметы', func=get_interests),
        MenuNode('Изменить время уведомлений', callback=change_notify_time_call.new())
    ])

    user_menu.child(text='Личные данные').child(text='Удалить предметы').add_blind_node('del_subj')

    user_menu.child(text='Олимпиады').set_childs([
        NodeGenerator(text='Список моих олимпиад', func=get_my_olympiads),
        MenuNode('Добавить отдельные олимпиады', callback=add_new_olympiad_call.new()),
        MenuNode('Ближайшие олимпиады', callback=get_nearest_olympiads_call.new())
    ])

    user_menu.child(text='Олимпиады').child(text='Список моих олимпиад').add_blind_node('list_olymp', type='generator',
                                                                                        func=register_olympiads_options)
    user_menu.child(text='Олимпиады').child(text='Список моих олимпиад').blind_node.add_blind_node('ol_opt')

    # user_menu.child(text='Олимпиады').child(text='Регистрации').add_blind_node('reg_olymp')
    # user_menu.child(text='Олимпиады').child(text='Регистрации').set_sub_childs([
    #     MenuNode('Выполнить', callback=call.new(data='')),
    #     MenuNode('Забыть', callback=call.new(data=''))
    # ])

    user_menu.child(text='Обратная связь').set_childs([
        MenuNode('Задать вопрос про олимпиады', callback=question_to_admin_call.new()),
        MenuNode('Ошибка работы бота')
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
