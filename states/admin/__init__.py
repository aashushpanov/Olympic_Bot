from .announceements import register_announcement_handlers
from .delete_data import delete_data_handlers
from .registration import register_registration_handlers
from .set_keys import set_key_handlers
from .set_olympiad import set_olympiads_handlers


def register_admin_states(dp):
    set_olympiads_handlers(dp)
    set_key_handlers(dp)
    delete_data_handlers(dp)
    register_announcement_handlers(dp)
    register_registration_handlers(dp)
