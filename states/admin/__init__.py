from .set_keys import set_key_handlers
from .set_olympiad import set_olympiads_handlers


def register_admin_states(dp):
    set_olympiads_handlers(dp)
    set_key_handlers(dp)
