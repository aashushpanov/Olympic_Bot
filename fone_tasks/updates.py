import pandas as pd
import datetime as dt

from loader import bot
from utils.db.add import set_inactive, add_olympiads_to_track
from utils.db.get import get_olympiads, get_users, get_tracked_olympiads


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


def update_olympiads_status():
    pass
