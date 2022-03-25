from handlers.tree_menu import MenuNode


def set_admin_menu():
    admin_menu = MenuNode()

    admin_menu.set_childs([
        MenuNode('option 1'),
        MenuNode('option 2'),
        MenuNode('option 3')
    ])

    admin_menu.child(child_id='0_0').set_childs([
        MenuNode('option 4'),
        MenuNode('option 5'),
        MenuNode('option 6')
    ])

    admin_menu.child(child_id='0_1').set_childs([
        MenuNode('option 7'),
        MenuNode('option 8'),
        MenuNode('option 9')
    ])

    admin_menu.child(child_id='0_2').set_childs([
        MenuNode('option 10'),
        MenuNode('option 11'),
        MenuNode('option 12')
    ])

    all_childs = admin_menu.all_childs()

    return admin_menu, all_childs

