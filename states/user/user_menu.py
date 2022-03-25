from handlers.MenuNode import MenuNode


def set_user_menu(main_node=None):
    user_menu = MenuNode(text="Меню ученика", id='0_1')
    if main_node:
        main_node.set_child(user_menu)

    user_menu.set_childs([
        MenuNode('user_0'),
        MenuNode('user_1'),
        MenuNode('user_2')
    ])

    user_menu.child(child_id='0_0').set_childs([
        MenuNode('user_0_0'),
        MenuNode('user_0_1'),
        MenuNode('user_0_1')
    ])

    user_menu.child(child_id='0_1').set_childs([
        MenuNode('user_1_0'),
        MenuNode('user_1_1'),
        MenuNode('user_1_2')
    ])

    user_menu.child(child_id='0_2').set_childs([
        MenuNode('user_2_0'),
        MenuNode('user_2_1'),
        MenuNode('user_2_2')
    ])

    # all_childs = user_menu.all_childs()

    return user_menu

