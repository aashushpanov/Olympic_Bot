from .set_admin import set_admin_handlers


def register_admin(dp):
    set_admin_handlers(dp)