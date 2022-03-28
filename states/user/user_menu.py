from aiogram.utils.callback_data import CallbackData

from handlers.MenuNode import MenuNode, move
from handlers.MenuNode import NodeGenerator
from utils.db.get import get_olympiad_status


call = CallbackData('2', 'data')


async def get_olympiad_registrations(node, **kwargs):
    user_id = kwargs.get('callback').message.chat.id
    olympiads = await get_olympiad_status(user_id=user_id, status='reg')
    for olympiad in olympiads:
        next_node = node.blind_node.id
        yield MenuNode(text=olympiad[0], callback=move.new(action='d', node=next_node, data=olympiad[0]))


def set_user_menu(main_node=None, root_id='0.1'):
    user_menu = MenuNode(text="Меню ученика", id=root_id)
    if main_node:
        main_node.set_child(user_menu)

    user_menu.set_childs([
        MenuNode('Регистрация'),
        MenuNode('Олимпиады'),
        MenuNode('user_2')
    ])

    user_menu.child(text='Регистрация').set_childs([
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

    # all_childs = user_menu.all_childs()

    return user_menu
