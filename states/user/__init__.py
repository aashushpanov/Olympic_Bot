from .change_interests import register_add_interests_handlers
from .registration import register_registration_handlers


def register_user_states(dp):
    register_registration_handlers(dp)
    register_add_interests_handlers(dp)
