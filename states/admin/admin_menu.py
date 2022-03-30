from utils.menu.MenuNode import MenuNode


def set_admin_menu(main_node):
    admin_menu = MenuNode("Меню администратора")
    if main_node:
        main_node.set_child(admin_menu)

    admin_menu.set_childs([
        MenuNode('admin_0'),
        MenuNode('admin_1'),
        MenuNode('admin_2')
    ])

    admin_menu.child(text='admin_0').set_childs([
        MenuNode('admin_0_0'),
        MenuNode('admin_0_1'),
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

