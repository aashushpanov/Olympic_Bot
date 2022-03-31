from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode

set_olympiads_call = CallbackData('set_olympiads')
set_olympiads_dates_call = CallbackData('set_olympiads_dates')


def set_admin_menu(main_node):
    admin_menu = MenuNode("Меню администратора")
    if main_node:
        main_node.set_child(admin_menu)

    admin_menu.set_childs([
        MenuNode('Данные олимпиад'),
        MenuNode('admin_1'),
        MenuNode('admin_2')
    ])

    admin_menu.child(text='Обновить данные').set_childs([
        MenuNode('Добавить олимпиады', callback=set_olympiads_call.new()),
        MenuNode('Установить даты этапов', callback=set_olympiads_dates_call.new()),
        MenuNode('admin_0_1')
    ])

    admin_menu.child(text='admin_1').set_childs([
        MenuNode('admin_1_0'),
        MenuNode('admin_1_1'),
        MenuNode('admin_1_2')
    ])

    admin_menu.child(text='admin_2').set_childs([
        MenuNode('admin_2_0'),
        MenuNode('admin_2_1'),
        MenuNode('admin_2_2')
    ])

    # all_childs = admin_menu.all_childs()

    return admin_menu

