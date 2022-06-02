from .add_new_olympiad import register_add_new_olympiad_handlers
from .change_interests import register_add_interests_handlers
from .change_personal_data import register_personal_data_handlers
from .feedback import register_questions_handlers
from .registration import register_registration_handlers


def register_user_states(dp):
    register_registration_handlers(dp)
    register_add_interests_handlers(dp)
    register_add_new_olympiad_handlers(dp)
    register_questions_handlers(dp)
    register_personal_data_handlers(dp)
