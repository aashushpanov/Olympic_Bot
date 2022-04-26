from aiogram import Dispatcher, types

from filters import IsAdmin


def register_help_handlers(dp: Dispatcher):
    from states.admin.delete_data import DeleteData
    from states.admin.set_keys import AddKeys
    from states.admin.set_olympiad import SetOlympiads
    dp.register_message_handler(menu_help, IsAdmin(), commands=['help'])
    dp.register_message_handler(set_olympiads_help, commands=['help'], state=SetOlympiads.all_states)
    dp.register_message_handler(delete_olympiads, commands=['help'], state=DeleteData.all_states)
    dp.register_message_handler(set_keys_help, commands=['help'], state=AddKeys.all_states)


async def menu_help(message: types.Message):
    text = "Здесь собраны основные функции данного бота." \
           "\n\n" \
           "Меню 'Данные олимпиад' позволяет добавлять и удалять предметы, олимпиады, даты этапов и ключи этапов." \
           "\n\n" \
           "В меню 'Выгрузки' у вас есть возможность получить данные о текущем состоянии предметов, олимпиад и " \
           "результатах прохождения."
    await message.answer(text=text)


async def set_olympiads_help(message: types.Message):
    text = "Отправьте сюда csv-файл в кодировке UTF-8, для удобства можно скачать шаблон. Пример заполнения доступен " \
           "по ссылке выше. "
    await message.answer(text=text)


async def delete_olympiads(message: types.Message):
    text = "Отправьте сюда csv-файл в кодировке UTF-8, для удобства можно скачать шаблон. Пример заполнения доступен " \
           "по ссылке выше. " \
           "\n\n" \
           "Будте осторожны, при удалении предметов или олимпиад удалиться также вся статистика их прохождения."
    await message.answer(text=text)


async def set_keys_help(message: types.Message):
    text = "Выберите класс и отправьте сюда csv-файл с ключами ВСОШ, скачанный с СтатГрада. Этот файл не нужно " \
           "изменять. "
    await message.answer(text=text)