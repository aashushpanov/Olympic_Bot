import asyncio

import pandas as pd
import datetime as dt

from aiogram.utils.callback_data import CallbackData

from data import config
from handlers.users.user.olympiad_options import confirm_execution_call, confirm_registration_call
from keyboards.keyboards import callbacks_keyboard, delete_keyboard_call
from loader import bot
from utils.db.add import set_inactive, add_olympiads_to_track, set_missed, add_notifications
from utils.db.get import get_olympiads, get_users, get_tracked_olympiads, get_all_olympiads_status, \
    get_questions_counts, get_admins

show_admin_question_call = CallbackData('show_admin_question')


async def greeting():
    users = get_users()
    for _, user in users.iterrows():
        user_id = user['user_id']
        await bot.send_message(user_id, text='hi')


def update_olympiads_activity():
    olympiads = get_olympiads()
    inactive_olympiads = pd.DataFrame(columns=olympiads.columns)
    for _, olympiad in olympiads[olympiads['active'] == 1].iterrows():
        if dt.date.today() > olympiad['finish_date']:
            olympiad = pd.DataFrame([olympiad])
            inactive_olympiads = pd.concat([inactive_olympiads, olympiad], ignore_index=True)
    if not inactive_olympiads.empty:
        _ = set_inactive(inactive_olympiads)


def update_olympiads_to_track():
    users = get_users()
    olympiads = get_olympiads()
    for _, user in users.iterrows():
        tracked = list(get_tracked_olympiads(user['user_id'])['olympiad_code'].values)
        new_olympiads = olympiads[(olympiads['subject_code'].isin(user['interest'])) &
                                  (olympiads['grade'] == int(user['grade'])) &
                                  (olympiads['active'] == 1) & (~olympiads['code'].isin(tracked))]
        _ = add_olympiads_to_track(new_olympiads, user['user_id'])


def update_missed_olympiads():
    olympiads = get_olympiads()
    olympiads_status = get_all_olympiads_status()
    olympiads_status = olympiads_status.join(olympiads.set_index('code'), on='olympiad_code', rsuffix='_real')
    missed_olympiads = olympiads_status[((olympiads_status['status'] == 'reg') | (olympiads_status['status'] == 'idle'))
                                        & ((olympiads_status['active'] == 0) | (olympiads_status['stage'] !=
                                                                                olympiads_status['stage_real']))]
    columns = ['code', 'stage']
    missed_olympiads_to_update = pd.DataFrame(columns=columns)
    for name, _ in missed_olympiads.groupby(['olympiad_code', 'stage']):
        olympiad = pd.DataFrame([name], columns=columns)
        missed_olympiads_to_update = pd.concat([missed_olympiads_to_update, olympiad])
    if not missed_olympiads_to_update.empty:
        _ = set_missed(missed_olympiads_to_update)


def create_notifications():
    olympiads_status = get_all_olympiads_status()
    olympiads = get_olympiads()
    olympiads_status = olympiads_status.join(olympiads.set_index('code'), on='olympiad_code', rsuffix='_real')
    columns = ['user_id', 'olympiad_code', 'message', 'type']
    notifications = pd.DataFrame(columns=columns)
    for _, status in olympiads_status[olympiads_status['status'] == 'idle'].iterrows():
        if (status['start_date'] - dt.date.today()).days < 2 or (
                status['finish_date'] >= dt.date.today() >= status['start_date']):
            user_id = status['user_id']
            olympiad_code = status['olympiad_code']
            if 2 >= (status['start_date'] - dt.date.today()).days > 0:
                message_prefix = 'Скоро начнется '
            elif status['finish_date'] >= dt.date.today() >= status['start_date']:
                message_prefix = 'Скоро закончится '
            else:
                message_prefix = ''
            message = message_prefix + status['name'] + ", а вы еще не зарегистрировались. Если уже сделали это, " \
                                                        "нажмите 'Зарегистрировался'"
            notify_type = 'reg_notify'
            notification = pd.DataFrame([[user_id, olympiad_code, message, notify_type]], columns=columns)
            notifications = pd.concat([notifications, notification], axis=0)
    for _, status in olympiads_status[olympiads_status['status'] == 'reg'].iterrows():
        user_id = status['user_id']
        olympiad_code = status['olympiad_code']
        if status['finish_date'] >= dt.date.today() >= status['start_date']:
            message = "Скоро закончится {}, а вы еще не прошли ее. Если уже сделали это, нажмите 'Пройдена'".\
                format(status['name'])
            notify_type = 'done_notify'
            notification = pd.DataFrame([[user_id, olympiad_code, message, notify_type]], columns=columns)
            notifications = pd.concat([notifications, notification], axis=0)
        elif (status['start_date'] - dt.date.today()).days < 2:
            message = "Скоро будет {}, постарайтесь не забыть".format(status['name'])
            notify_type = 'soon_notify'
            notification = pd.DataFrame([[user_id, olympiad_code, message, notify_type]], columns=columns)
            notifications = pd.concat([notifications, notification], axis=0)
    if not notifications.empty:
        _ = add_notifications(notifications)


def create_question_notifications():
    try:
        olympiad_code = get_olympiads().iloc[0, :]['code']
    except IndexError:
        olympiad_code = ''
    questions_counts = get_questions_counts()
    if questions_counts:
        admins = get_admins()
        columns = ['user_id', 'olympiad_code', 'message', 'type']
        message = 'У вас есть неотвеченные вопросы ({})'.format(questions_counts)
        notify_type = 'admin_question'
        notifications = pd.DataFrame(columns=columns)
        for _, admin in admins.iterrows():
            notification = pd.DataFrame([[admin['admin_id'], olympiad_code, message, notify_type]], columns=columns)
            notifications = pd.concat([notifications, notification], axis=0)
        if not notifications.empty:
            _ = add_notifications(notifications)


async def send_notifications(notifications):
    olympiads = get_olympiads()
    for _, notification in notifications.iterrows():
        text = notification['message']
        olympiad_code = notification['olympiad_code']
        stage = int(olympiads[olympiads['code'] == olympiad_code]['stage'].item())
        if notification['type'] == 'reg_notify':
            reg_url = olympiads[olympiads['code'] == olympiad_code]['urls'].iloc[0].get('reg_url')
            reg_url = reg_url if reg_url else 'https://olimpiada.ru/'
            reply_markup = callbacks_keyboard(texts=['Ссылка на регистрацию', 'Зарегистрировался', 'Скрыть'],
                                              callbacks=[reg_url, confirm_registration_call.new(data=olympiad_code,
                                                                                                stage=stage),
                                                         delete_keyboard_call.new()])
            try:
                await bot.send_message(chat_id=notification['user_id'], text=text, reply_markup=reply_markup)
            except Exception as error:
                print(error)
        elif notification['type'] == 'done_notify':
            reply_markup = callbacks_keyboard(texts=['Пройдена', 'Скрыть'],
                                              callbacks=[confirm_execution_call.new(data=olympiad_code, stage=stage),
                                                         delete_keyboard_call.new()])
            try:
                await bot.send_message(chat_id=notification['user_id'], text=text, reply_markup=reply_markup)
            except Exception as error:
                print(error)
        elif notification['type'] == 'done_notify':
            try:
                await bot.send_message(notification['user_id'], text=text)
            except Exception as error:
                print(error)
        elif notification['type'] == 'admin_question':
            reply_markup = callbacks_keyboard(texts=['Показать', 'Скрыть'],
                                              callbacks=[show_admin_question_call.new(), delete_keyboard_call.new()])
            try:
                await bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=text, reply_markup=reply_markup)
            except Exception as error:
                print(error)
        await asyncio.sleep(0.04)

