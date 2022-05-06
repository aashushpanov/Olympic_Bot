from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode

get_cm_status_file_call = CallbackData('get_cm_status_file')
get_cm_users_file_call = CallbackData('get_cm_status_file_call')
change_email_call = CallbackData('change_email')


def set_class_manager_menu():
    class_manager_menu = MenuNode(id='cm_menu')

    class_manager_menu.set_childs([
        MenuNode('Личные данные'),
        MenuNode('Данные по классу')
    ])

    class_manager_menu.child(text='Личные данные').set_childs([
        MenuNode('Изменить почту', callback=change_email_call.new()),
    ])

    class_manager_menu.child(text='Данные по классу').set_childs([
        MenuNode('Список учеников', callback=get_cm_users_file_call.new()),
        MenuNode('Статусы олимпиад', callback=get_cm_status_file_call.new()),
    ])

    return class_manager_menu


