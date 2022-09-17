from aiogram import Dispatcher, types


def register_help_handlers(dp: Dispatcher):
    from states.user.add_new_olympiad import AddOlympiad
    from states.user.change_interests import AddNewInterests
    from states.user.feedback import AddQuestion
    from states.user.registration import Registration
    from utils.menu.generator_functions import add_olympiad_help_call
    from utils.menu.generator_functions import get_key_help_call
    dp.register_message_handler(registration_help, commands=['help'], state=Registration.all_states)
    dp.register_message_handler(add_olympiad_help, commands=['help'], state=AddOlympiad.all_states)
    dp.register_message_handler(change_interests_help, commands=['help'], state=AddNewInterests.all_states)
    dp.register_message_handler(admin_message_help, commands=['help'], state=AddQuestion.all_states)
    dp.register_message_handler(menu_help, commands=['help'])
    dp.register_callback_query_handler(how_add_olympiad, add_olympiad_help_call.filter())
    dp.register_callback_query_handler(how_get_key, get_key_help_call.filter())


async def menu_help(message: types.Message):
    text = "Здесь собраны все функции данного бота." \
           "\n\n" \
           "В разделе 'Личные данные' можно добавить и удалить предметы, по которым бот автоматически будет " \
           "отслеживать все олимпиады за ваш класс, а также в этом разделе можно поменять время, в которое вам будут " \
           "приходить напоминания." \
           "\n\n" \
           "В разделе 'Олимпиады' вы можете посмотреть, за какими олимпиадами в данный момент происходит " \
           "отслеживание. Нажав на название олимпиады, можно получить информацию о ней, перейти на связанные сайты, " \
           "отметиться о прохождении, регистрации или получить ключ. Подменю 'Добавить новые олимпиады' позволит " \
           "выбрать любую олимпиаду за интересующий вас класс и добавить ее к себе." \
           "\n\n" \
           "В разделе 'Обратная связь' можно задать вопрос руководителю олимпиадного движения. Его увидят сразу, " \
           "и, как только будет получен ответ, вам придет уведомление." \
           "\n\n" \
           "Важно: на момент прохождения олимпиады мы не всегда можем получить точную информацию от оргкомитета.\n " \
           "<b>НЕ ПОДТВЕРЖДАЙТЕ</b> регистрацию или выполнение без фактической регистрации или выполнения олимпиады.\n"\
           "Спустя некоторое время после прохождения олимпиады школе доступа полная информация об " \
           "участниках, и данная функция лишь помогает нам оперативно анализировать текущую ситуацию." \
           "\n\n" \
           "Надеемся на ваше понимание."
    await message.answer(text=text, parse_mode='HTML')


async def registration_help(message: types.Message):
    text = "Это вступительный этап при работе с данным ботом. Вам необходимо будет ввести свое имя, фамилию, " \
           "информацию о классе." \
           "\n\n" \
           "Далее надо выбрать какими предметами вы интересуетесь. Это нужно для того, " \
           "чтобы бот сам добавлял олимпиады в раздел отслеживаемых. Для выбора предмета просто нажмите на него, " \
           "в верхней части экрана появиться фраза 'запомним'. Чтобы продвинуться дальше, нажмите 'готово'." \
           "Потом эти предметы можно изменить в меню 'Личные данные'." \
           "\n\n" \
           "Время уведомления \U00002014 это промежуток, в который вам будет присылаться уведомления о начале и " \
           "окончании выбранных олимпиад. "
    await message.answer(text=text)


async def change_interests_help(message: types.Message):
    text = "Добавьте предметы, которыми интересуетесь. Для выбора предмета просто нажмите на него. В верхней части " \
           "экрана появится фраза 'запомним'. Когда закончите, нажмите 'готово'. "
    await message.answer(text=text)


async def add_olympiad_help(message: types.Message):
    text = "Чтобы добавить олимпиаду сначала выберите предмет: нажмите на нужный, а после \U00002014 'готово'. Вам " \
           "будет предложен список доступных олимпиад по выбранному предмету. Нажав на нужную олимпиаду выберите " \
           "класс, за который хотите ее писать."
    await message.answer(text=text)


async def admin_message_help(message: types.Message):
    text = "Наберите сообщение на клавиатуре, тогда ваш вопрос будет зарегистрирован, о чем вам сообщит бот. " \
           "Администраторы сразу увидят ваше обращение и ответят на него."
    await message.answer(text=text)


async def how_add_olympiad(callback: types.CallbackQuery):
    text = "Зайдите в меню 'Олимпиады' -> 'Добавить отдельные олимпиады'. Переключая страницы, выберите из предложенного " \
           "списка нужную олимпиаду, а также класс (свой или выше)."
    await callback.answer()
    await callback.message.answer(text=text)


async def how_get_key(callback: types.CallbackQuery):
    text = "Взять ключ можно из главного меню, выбрав 'Получить ключ' и затем нажать на нужную олимпиаду. " \
           "Также эта возможность есть в меню 'Олимпиады' -> 'Мои олимпиады' -> (Нужная олимпиада)."
    await callback.answer()
    await callback.message.answer(text=text)
