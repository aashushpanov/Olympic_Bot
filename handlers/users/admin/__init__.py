from .get_files import register_get_files_handlers
from .help import register_help_handlers
from .questions_answer import register_questions_answer_handlers
from .set_admin import set_admin_handlers


def register_admin_handlers(dp):
    set_admin_handlers(dp)
    register_get_files_handlers(dp)
    register_questions_answer_handlers(dp)
    register_help_handlers(dp)
