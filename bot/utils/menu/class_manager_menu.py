from aiogram.utils.callback_data import CallbackData

from ...utils.menu.MenuNode import MenuNode, NodeGenerator
from ...utils.menu.admin_menu import set_excel_format_call, set_google_doc_format_call, change_email_call
from ...utils.menu.generator_functions import get_download_options
from ...utils.menu.user_menu import change_notify_time_call, show_personal_data_call

get_cm_status_file_call = CallbackData('get_cm_status_file')
get_cm_users_file_call = CallbackData('get_cm_status_file_call')
migrate_call = CallbackData('migrate')


def set_class_manager_menu():
    class_manager_menu = MenuNode(id='cm_menu')

    class_manager_menu.set_childs([
        MenuNode('Личные данные'),
        NodeGenerator('Данные по классу', func=get_download_options),
        MenuNode('Перейти на новую версию', migrate_call.new())
    ])
    class_manager_menu.child(text='Данные по классу').add_blind_node('cm_dl_opt')

    class_manager_menu.child(text='Личные данные').set_childs([
        MenuNode('Личные данные', callback=show_personal_data_call.new()),
        MenuNode('Установить время для уведомлений', callback=change_notify_time_call.new()),
        MenuNode('Изменить почту', callback=change_email_call.new()),
        MenuNode('Формат выгружаемых данных')
    ])

    class_manager_menu.child(text='Личные данные').child(text='Формат выгружаемых данных').set_childs([
        MenuNode('Excel', callback=set_excel_format_call.new()),
        MenuNode('Google таблицы', callback=set_google_doc_format_call.new()),
    ])

    # class_manager_menu.child(text='Данные по классу').set_childs([
    #     MenuNode('Список учеников', callback=get_cm_users_file_call.new()),
    #     MenuNode('Статусы олимпиад', callback=get_cm_status_file_call.new()),
    # ])

    return class_manager_menu


