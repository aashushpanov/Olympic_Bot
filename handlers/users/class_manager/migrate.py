from aiogram import types
from aiogram.dispatcher import Dispatcher

from states.class_manager.registration import create_class_managers_files
from utils.db.add import class_manager_migrate
from utils.db.get import get_admin
from utils.google_sheets.create import user_files_update
from utils.menu.class_manager_menu import migrate_call


def register_migrate_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(migration, migrate_call.filter())


async def migration(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    admin = get_admin(user_id)
    if admin.dropna().empty:
        class_manager_migrate(user_id)
        await callback.message.answer('Создание файлов. Подождите немного.')
        create_class_managers_files(user_id)
        user_files_update(user_id)
        await callback.message.answer('Обновление прошло. Теперь в меню Личные данные можно выбрать формат выгружаемых'
                                      ' файлов и привязать почту')
    else:
        await callback.message.answer('Вы уже перешли на новую версию')

