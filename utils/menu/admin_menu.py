from aiogram.utils.callback_data import CallbackData

from fone_tasks.updates import show_admin_question_call
from utils.menu.MenuNode import MenuNode, NodeGenerator

set_olympiads_call = CallbackData('set_olympiads')
set_subjects_call = CallbackData('set_subjects')
set_olympiads_dates_call = CallbackData('set_olympiads_dates')
set_keys_call = CallbackData('set_keys')
set_admins_call = CallbackData('set_admins')
get_olympiads_file_call = CallbackData('get_olympiads_file')
get_subjects_file_call = CallbackData('get_subjects_file')
get_status_file_call = CallbackData('get_status_file')
get_users_file_call = CallbackData('get_users')
get_answer_file_call = CallbackData('get_answer_file')
delete_subjects_call = CallbackData('delete_subjects')
delete_olympiads_call = CallbackData('delete_olympiads')


def set_admin_menu(main_node):
    admin_menu = MenuNode("Меню администратора")
    if main_node:
        main_node.set_child(admin_menu)

    admin_menu.set_childs([
        MenuNode('Данные олимпиад'),
        MenuNode('Выгрузки'),
        # MenuNode('admin_2')
    ])

    admin_menu.child(text='Данные олимпиад').set_childs([
        MenuNode('Добавить предметы', callback=set_subjects_call.new()),
        MenuNode('Добавить олимпиады', callback=set_olympiads_call.new()),
        MenuNode('Установить даты этапов', callback=set_olympiads_dates_call.new()),
        MenuNode('Загрузить ключи ВСОШ', callback=set_keys_call.new()),
        MenuNode('Удалить предметы', callback=delete_subjects_call.new()),
        MenuNode('Удалить олимпиады', callback=delete_olympiads_call.new()),
    ])

    admin_menu.child(text='Выгрузки').set_childs([
        MenuNode('Список пользователей', callback=get_users_file_call.new()),
        MenuNode('Список предметов', callback=get_subjects_file_call.new()),
        MenuNode('Список олимпиад', callback=get_olympiads_file_call.new()),
        MenuNode('Результаты прохождения олимпиад', callback=get_status_file_call.new())
    ])

    # admin_menu.child(text='admin_2').set_childs([
    #     MenuNode('admin_2_0'),
    #     MenuNode('admin_2_1'),
    #     MenuNode('admin_2_2')
    # ])

    # all_childs = admin_menu.all_childs()

    return admin_menu


def set_group_admin_menu():
    group_admin_menu = MenuNode('Меню', id='group_menu')

    group_admin_menu.set_childs([
        MenuNode(text='Установить администраторов', callback=set_admins_call.new()),
        MenuNode(text='Вопросы от учеников', callback=show_admin_question_call.new()),
        MenuNode(text='Выгрузка ответов', callback=get_answer_file_call.new())
    ])

    return group_admin_menu
