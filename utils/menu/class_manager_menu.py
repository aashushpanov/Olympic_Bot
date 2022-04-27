from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode


class_manager_registration_call = CallbackData('class_manager_registration')


def set_class_manager_menu():
    class_manager_menu = MenuNode()

    class_manager_menu.set_childs([
        MenuNode('Регистрация', callback=class_manager_registration_call.new()),
        MenuNode('Данные по классу')
    ])

    return class_manager_menu


