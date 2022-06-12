from aiogram import Dispatcher
from aiogram import types

from data import config
from filters import IsExist
from loader import bot
from utils.db.add import admin_migrate, remove_admin_access, change_users_files
from utils.db.get import get_admins
from utils.files.tables import file_alias, create_google_file
from utils.menu.admin_menu import set_admins_call


def set_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(set_admin, set_admins_call.filter(), IsExist(1), chat_type=types.ChatType.GROUP,
                                       is_chat_admin=True, chat_id=config.ADMIN_GROUP_ID)


async def set_admin(callback: types.CallbackQuery):
    await callback.answer()
    await update_admins()
    admins = get_admins()
    text = "Текущие администраторы:\n{}".format('\n'.join(
        [row['last_name'] + ' ' + row['first_name'] + '\n' for _, row in admins.iterrows()]))
    await bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=text)
    for _, admin in admins.iterrows():
        await bot.send_message(chat_id=admin['admin_id'], text="Вы администратор")


async def update_admins():
    new_admins = await bot.get_chat_administrators(config.ADMIN_GROUP_ID)
    new_admins = set([admin['user']['id'] for admin in new_admins if not admin['user']['is_bot']])
    current_admins = set(get_admins()['admin_id'].to_list())
    admins_to_delete = current_admins - new_admins
    admins_to_add = new_admins - current_admins
    if admins_to_add:
        admin_migrate(list(admins_to_add))
        change_users_files(user_id=None, file_types=['users_file'])
        for admin_id in admins_to_add:
            create_google_file(admin_id, file_alias.keys())
    if admins_to_delete:
        remove_admin_access(list(admins_to_delete))

