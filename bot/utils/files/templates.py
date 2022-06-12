import pandas as pd

from utils.db.get import get_subjects, get_olympiads


def make_subjects_file():
    file_path = 'bot/data/files/to_send/subjects.xlsx'
    subjects = get_subjects()
    columns_rename = {'code': 'Код предмета', 'name': 'Предмет', 'section': 'Раздел'}
    subjects.rename(columns=columns_rename, inplace=True)
    subjects.drop(columns=['id'], inplace=True)
    subjects.to_excel(file_path, index=False)
    return file_path, subjects


def make_olympiads_dates_template():
    file_path = 'bot/data/files/to_send/dates_template.xlsx'
    olympiads = get_olympiads()
    olympiads_list = list(olympiads.groupby('name').groups.keys())
    columns = ['Название', 'мл. класс', 'ст. класс', 'дата начала', 'дата окончания',
               'этап', 'предварительная регистрация', 'ключ']
    olympiads_file = pd.DataFrame([[x, '', '', '', '', '', '', ''] for x in olympiads_list], columns=columns)
    olympiads_file.to_excel(file_path, index=False)
    return file_path, olympiads_file


def make_subjects_template(subjects=None):
    if subjects is None:
        subjects = []
    file_path = 'bot/data/files/to_send/subjects_template.xlsx'
    columns = ['Предмет', 'Код предмета', 'Раздел']
    subjects_template = pd.DataFrame([[x, '', ''] for x in subjects], columns=columns)
    subjects_template.to_excel(file_path, index=False)
    return file_path, subjects_template


def make_olympiads_template(olympiads=None):
    if olympiads is None:
        olympiads = []
    file_path = 'bot/data/files/to_send/olympiads_template.xlsx'
    subjects = get_subjects()
    subjects_list = list(subjects['name'].values)
    ol_subj_list = merge_lists(olympiads, subjects_list)
    columns = ['Префикс', 'Название', 'Предмет', 'мл. класс', 'ст. класс', 'ссылка на регистрацию',
               'ссылка на сайт олимпиады', 'Доступные предметы']
    olympiads_template = pd.DataFrame([['', ol, '', '', '', '', '', subj] for ol, subj in ol_subj_list],
                                      columns=columns)
    olympiads_template.to_excel(file_path, index=False)
    return file_path, olympiads_template


def merge_lists(list1, list2):
    res = []
    i = 0
    while i <= len(list1) or i <= len(list2):
        if i < len(list1):
            item1 = list1[i]
        else:
            item1 = ''
        if i < len(list2):
            item2 = list2[i]
        else:
            item2 = ''
        res.append((item1, item2))
        i += 1
    return res
