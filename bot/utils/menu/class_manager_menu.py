from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode, NodeGenerator
from utils.menu.admin_menu import set_excel_format_call, set_google_doc_format_call, change_email_call
from utils.menu.generator_functions import get_download_options, get_file_call
from utils.menu.user_menu import change_notify_time_call, show_personal_data_call, delete_yourself_call

get_cm_status_file_call = CallbackData('get_cm_status_file')
get_cm_users_file_call = CallbackData('get_cm_status_file_call')
migrate_call = CallbackData('migrate')
get_key_for_class_call = CallbackData('get_key_for_class')
taken_keys_call = CallbackData('taken_keys')


def set_class_manager_menu():
    class_manager_menu = MenuNode(id='cm_menu', text='Меню')

    class_manager_menu.set_childs([
        MenuNode('Личные данные'),
        NodeGenerator('Данные учеников', func=get_download_options),
        MenuNode('Взять ключи ВСОШ', callback=get_key_for_class_call.new())
    ])
    class_manager_menu.child(text='Данные учеников').add_blind_node('cm_dl_opt')

    class_manager_menu.child(text='Личные данные').set_childs([
        MenuNode('Личные данные', callback=show_personal_data_call.new()),
        MenuNode('Установить время для уведомлений', callback=change_notify_time_call.new()),
        MenuNode('Изменить почту', callback=change_email_call.new()),
        MenuNode('Формат выгружаемых данных'),
        MenuNode('Удалить себя из системы', callback=delete_yourself_call.new())
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


