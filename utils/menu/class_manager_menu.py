from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode




def set_class_manager_menu():
    class_manager_menu = MenuNode(id='cm_menu')

    class_manager_menu.set_childs([
        MenuNode('Личные данные'),
        MenuNode('Данные по классу')
    ])

    class_manager_menu.child('Данные по классу').set_childs([
        MenuNode('Список учеников'),
        MenuNode('Статусы олимпиад')
    ])

    return class_manager_menu


