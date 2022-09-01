import pygsheets

gc = pygsheets.authorize(service_file='./bot/service_files/olympicbot1210-c81dc6c184cb.json')
sheet_list = gc.spreadsheet_titles()
for sheet in sheet_list:
    spread_sheet = gc.open(sheet)
    print('open')
    spread_sheet.delete()
    print('delete')

print('clean')
