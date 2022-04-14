import pandas as pd
import datetime as dt

from loader import bot
from utils.db.add import set_inactive, add_olympiads_to_track, set_missed
from utils.db.get import get_olympiads, get_users, get_tracked_olympiads, get_all_olympiads_status


async def greeting():
    users = get_users()
    for _, user in users.iterrows():
        user_id = user['user_id']
        await bot.send_message(user_id, text='hi')


def update_olympiads_activity():
    olympiads = get_olympiads()
    inactive_olympiads = pd.DataFrame(columns=olympiads.columns)
    for _, olympiad in olympiads.iterrows():
        if dt.date.today() > olympiad['finish_date']:
            inactive_olympiads = pd.concat([inactive_olympiads, olympiad])
    set_inactive(inactive_olympiads)


def update_olympiads_to_track():
    users = get_users()
    olympiads = get_olympiads()
    for _, user in users.iterrows():
        tracked = list(get_tracked_olympiads(user['user_id'])['olympiad_code'].values)
        new_olympiads = olympiads[(olympiads['subject_code'].isin(user['interest'])) &
                                  (olympiads['grade'] == int(user['grade'])) &
                                  (olympiads['active'] == 1) & (~olympiads['code'].isin(tracked))]
        add_olympiads_to_track(new_olympiads, user['user_id'])


def update_missed_olympiads():
    olympiads = get_olympiads()
    olympiads_status = get_all_olympiads_status()
    olympiads_status.join(olympiads.set_index('code'), on='olympiad_code', rsuffix='real')
    missed_olympiads = olympiads_status[((olympiads_status['status'] == 'reg') | (olympiads_status['status'] == 'idle'))
                                        & ((olympiads_status['active'] == 0) | (olympiads_status['stage'] !=
                                                                                olympiads_status['stage_real']))]
    columns = ['code', 'stage']
    missed_olympiads_to_update = pd.DataFrame(columns=columns)
    for name, _ in missed_olympiads.groupby(['olympiad_code', 'stage']):
        olympiad = pd.DataFrame([name], columns=columns)
        missed_olympiads_to_update = pd.concat([missed_olympiads_to_update, olympiad])
    if not missed_olympiads_to_update.empty:
        set_missed(missed_olympiads_to_update)
# TODO: доделать обновление статусов
