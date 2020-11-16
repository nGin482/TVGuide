from datetime import date, timedelta
import calendar
import json
import os


def get_data(obj_list):
    json_list = []

    for obj in obj_list:
        obj_dict = obj.to_dict()
        json_list.append(obj_dict)

    return json_list


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
        i = 16
        prev_month = date.today() - timedelta(days=1)
        previous_month_folder = 'BackUps/' + prev_month.strftime('%B-%Y')
        day_range = calendar.monthrange(prev_month.year, prev_month.month)[1]
        while i <= day_range:
            day = str(i)
            file = day + '-' + date.strftime(prev_month, '%m-%Y') + '.json'
            original_path = os.path.join('BackUps', file)
            if os.path.exists(original_path) and os.path.exists(previous_month_folder):
                os.rename(original_path, os.path.join(previous_month_folder, file))
            i += 1

    if date.today().day == 16:
        i = 1
        while i < 16:
            day = str(i)
            if len(day) == 1:
                day = '0' + day
            file = day + '-' + date.strftime(date.today(), '%m-%Y') + '.json'
            original_path = os.path.join('BackUps', file)
            new_path = 'BackUps/' + date.strftime(date.today(), '%B-%Y')
            if os.path.exists(original_path) and os.path.exists(new_path):
                os.rename(original_path, os.path.join(new_path, file))
            i += 1

    if date.today().day == 1 and date.today().month == 1:
        create_monthly_folder()
        prev_year = date((date.today() - timedelta(days=1)).year, 1, 1)
        for month in calendar.month_name:
            if month != '':  # first element is empty string
                original_directory = 'BackUps/' + month + '-' + str(prev_year.year)
                new_directory = 'BackUps/' + prev_year.strftime('%Y') + '/' + month + '-' + str(prev_year.year)
                os.rename(original_directory, new_directory)
                print(original_directory)
    print(calendar.month_name[0:])


def write_to_backup_file(obj_list):

    move_month_files()
    data = get_data(obj_list)
    filename = 'BackUps/' + date.strftime(date.today(), '%d-%m-%Y') + '.json'
    with open(filename, 'w', encoding='utf-8') as fd:
        json.dump(data, fd, ensure_ascii=False, indent=4)
