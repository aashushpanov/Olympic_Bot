from aiogram.utils.callback_data import CallbackData

from utils.menu.MenuNode import MenuNode, move
from utils.menu.MenuNode import NodeGenerator
from utils.db.get import get_olympiad_status

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

def set_interest_menu():
    # меню выбора олимпиад
    # --------------------------------------------------------------------------------------------------------
    olympiad_interest_menu = MenuNode(text='Выбор предметов', id='o_interest')
    olympiad_interest_menu.set_childs([
        MenuNode(text='Естественные науки'),
        MenuNode(text='Гуманитарные науки'),
        MenuNode(text='Общественные науки'),
        MenuNode(text='Математика', callback=add_interest_call.new(data='math')),
        MenuNode(text='Готово', callback=confirm.new())
    ])

    olympiad_interest_menu.child(text='Естественные науки').set_childs([
        MenuNode(text='Физика', callback=add_interest_call.new(data='phys')),
        MenuNode(text='Химия', callback=add_interest_call.new(data='chem')),
        MenuNode(text='Биология', callback=add_interest_call.new(data='bio')),
        MenuNode(text='География', callback=add_interest_call.new(data='geo')),
        MenuNode(text='Экология', callback=add_interest_call.new(data='ecol'))
    ])

    olympiad_interest_menu.child(text='Гуманитарные науки').set_childs([
        MenuNode(text='Русский язык', callback=add_interest_call.new(data='rus')),
        MenuNode(text='Английский язык', callback=add_interest_call.new(data='eng')),
        MenuNode(text='Испанский язык', callback=add_interest_call.new(data='spain')),
        MenuNode(text='Французский язык', callback=add_interest_call.new(data='french')),
        MenuNode(text='Лингвистика', callback=add_interest_call.new(data='ling'))
    ])

    olympiad_interest_menu.child(text='Общественные науки').set_childs([
        MenuNode(text='Обществознание', callback=add_interest_call.new(data='social')),
        MenuNode(text='Право', callback=add_interest_call.new(data='low')),
        MenuNode(text='Экономика', callback=add_interest_call.new(data='econ')),
    ])

    return olympiad_interest_menu
