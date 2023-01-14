from datetime import date, timedelta
import calendar
import json
import os


def create_monthly_folder():
    today = date.today()
    if today.day == 1:
        new_path = os.path.join("BackUps", str(today.strftime("%B-%Y")))

        if not os.path.exists(new_path):
            os.mkdir(new_path)

    if today.day == 1 and today.month == 1:
        prev_year = today - timedelta(days=1)
        new_path = os.path.join('BackUps', prev_year.strftime('%Y'))

        if not os.path.exists(new_path):
            os.mkdir(new_path)


def move_month_files():
    if date.today().day == 1:
        create_monthly_folder()
        prev_month = date.today() - timedelta(days=1)
        previous_month_folder = f'BackUps/{prev_month.strftime("%B-%Y")}'
        for i in range(16, calendar.monthrange(prev_month.year, prev_month.month)[1]):
            day = str(i)
            file = f'{day}-{date.strftime(prev_month, "%m-%Y")}.json'
            original_path = os.path.join('BackUps', file)
            if os.path.exists(original_path) and os.path.exists(previous_month_folder):
                os.rename(original_path, os.path.join(previous_month_folder, file))

    if date.today().day == 16:
        for i in range(1, 16):
            day = str(i) if i >= 10 else f'0{str(i)}'
            file = f'{day}-{date.strftime(date.today(), "%m-%Y")}.json'
            original_path = os.path.join('BackUps', file)
            new_path = f'BackUps/{date.strftime(date.today(), "%B-%Y")}'
            if os.path.exists(original_path) and os.path.exists(new_path):
                os.rename(original_path, os.path.join(new_path, file))

    if date.today().day == 1 and date.today().month == 1:
        create_monthly_folder()
        prev_year = str(date.today().year - 1)
        for directory in os.listdir('BackUps'):
            if prev_year in directory:
                new_directory = f'BackUps/{prev_year}/{directory}'
                os.rename(f'BackUps/{directory}', new_directory)
    print(calendar.month_name[0:])


def write_to_backup_file(backup_guide):

    move_month_files()
    filename = f'BackUps/{date.strftime(date.today(), "%d-%m-%Y")}.json'
    with open(filename, 'w', encoding='utf-8') as fd:
        json.dump(backup_guide, fd, ensure_ascii=False, indent=4)
