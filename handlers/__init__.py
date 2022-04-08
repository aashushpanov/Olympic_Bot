from .menus import main_menu_handlers
from .errors import register_errors_handlers


def register_handlers(dp):
    main_menu_handlers(dp)
    register_errors_handlers(dp)
