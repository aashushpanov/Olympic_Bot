from aiogram.utils.callback_data import CallbackData

from fone_tasks.updates import show_admin_question_call
from utils.menu.MenuNode import MenuNode, NodeGenerator
from utils.menu.generator_functions import get_download_options, get_file_call
from utils.menu.user_menu import change_notify_time_call

set_olympiads_call = CallbackData('set_olympiads')
set_subjects_call = CallbackData('set_subjects')
set_olympiads_dates_call = CallbackData('set_olympiads_dates')
set_keys_call = CallbackData('set_keys')
set_admins_call = CallbackData('set_admins')
get_olympiads_file_call = CallbackData('get_olympiads_file')
get_subjects_file_call = CallbackData('get_subjects_file')
get_status_file_call = CallbackData('get_status_file')
get_users_file_call = CallbackData('get_users')
get_cm_file_call = CallbackData('get_cm_file')
get_answer_file_call = CallbackData('get_answer_file')
delete_subjects_call = CallbackData('delete_subjects')
delete_olympiads_call = CallbackData('delete_olympiads')
announcement_call = CallbackData('announcement')
grade_announcement_call = CallbackData('grade_announcement')
olympiad_announcement_call = CallbackData('olympiad_announcement')
subject_announcement_call = CallbackData('subject_announcement')
cm_announcement_call = CallbackData('cm_announcement')
set_excel_format_call = CallbackData('set_excel_format')
set_google_doc_format_call = CallbackData('set_google_doc_format')
change_email_call = CallbackData('change_email')


def set_admin_menu(main_node):
    admin_menu = MenuNode("Меню администратора")
    if main_node:
        main_node.set_child(admin_menu)

    admin_menu.set_childs([
        MenuNode('Личные данные'),
        MenuNode('Данные олимпиад'),
        NodeGenerator('Выгрузки', func=get_download_options),
        MenuNode('Объявление')
    ])
    admin_menu.child(text='Выгрузки').add_blind_node('dl_opt')

    admin_menu.child(text='Личные данные').set_childs([
        MenuNode('Установить время для уведомлений', callback=change_notify_time_call.new()),
        MenuNode('Изменить email', callback=change_email_call.new()),
        MenuNode('Формат выгружаемых данных')
    ])

    admin_menu.child(text='Личные данные').child(text='Формат выгружаемых данных').set_childs([
        MenuNode('Excel', callback=set_excel_format_call.new()),
        MenuNode('Google таблицы', callback=set_google_doc_format_call.new()),
    ])

    admin_menu.child(text='Данные олимпиад').set_childs([
        MenuNode('Добавить предметы', callback=set_subjects_call.new()),
        MenuNode('Добавить олимпиады', callback=set_olympiads_call.new()),
        MenuNode('Установить даты этапов', callback=set_olympiads_dates_call.new()),
        MenuNode('Загрузить ключи ВСОШ', callback=set_keys_call.new()),
        MenuNode('Удалить предметы', callback=delete_subjects_call.new()),
        MenuNode('Удалить олимпиады', callback=delete_olympiads_call.new()),
    ])

    # admin_menu.child(text='Выгрузки').set_childs([
    #     MenuNode('Список учащихся', callback=get_users_file_call.new()),
    #     MenuNode('Список классных руководителей', callback=get_cm_file_call.new()),
    #     MenuNode('Список предметов', callback=get_subjects_file_call.new()),
    #     MenuNode('Список олимпиад', callback=get_olympiads_file_call.new()),
    #     MenuNode('Результаты прохождения олимпиад', callback=get_status_file_call.new())
    # ])

    admin_menu.child(text='Объявление').set_childs([
        MenuNode('Всем', callback=announcement_call.new()),
        MenuNode('По классу', callback=grade_announcement_call.new()),
        MenuNode('По олимпиаде', callback=olympiad_announcement_call.new()),
        MenuNode('По предмету', callback=subject_announcement_call.new()),
        MenuNode('Классным руководителям', callback=cm_announcement_call.new())
    ])

    # all_childs = admin_menu.all_childs()

    return admin_menu


def set_group_admin_menu():
    group_admin_menu = MenuNode('Меню', id='group_menu')

    group_admin_menu.set_childs([
        MenuNode(text='Установить администраторов', callback=set_admins_call.new()),
        MenuNode(text='Вопросы от учеников', callback=show_admin_question_call.new()),
        MenuNode(text='Выгрузка ответов', callback=get_file_call.new(type='answers_file'))
    ])

    return group_admin_menu
