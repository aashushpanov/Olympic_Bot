from cancel import register_cancel_handlers
from menus import main_menu_handlers
from errors import register_errors_handlers
from start import register_start_handler


def register_handlers(dp):
    register_errors_handlers(dp)
    register_cancel_handlers(dp)
    main_menu_handlers(dp)
    register_start_handler(dp)

