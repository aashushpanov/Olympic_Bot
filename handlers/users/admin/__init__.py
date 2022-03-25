from handlers.main_menu import admin_menu_handlers
from .set_admin import set_admin_handlers


def register_admin(dp):
    set_admin_handlers(dp)
    admin_menu_handlers(dp)