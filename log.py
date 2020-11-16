from datetime import datetime
import os


def get_log_file():
    log_file = os.path.join('C:\\Users', 'Nicholas', 'PycharmProjects', 'emails.txt')

    return log_file


def get_date_from_latest_email():

    file = get_log_file()

    arr = []
    with open(file) as f:
        for line in f:
            if 'TVGuide' in line:
                if '\n' in line:
                    arr.append(line[:-1])
                else:
                    arr.append(line)

    latest_email = arr[-1]
    print(latest_email)

    idx_front = latest_email.find('on ')
    idx_back = latest_email.find(' at ')
    date = latest_email[idx_front + 3:idx_back]
    time = latest_email[idx_back + 4:].split(':')
    date_parsed = datetime.strptime(date, '%d-%m-%y')
    new_date_parsed = date_parsed.replace(hour=int(time[0]), minute=int(time[1]))

    print(new_date_parsed)
    return new_date_parsed


def compare_dates():

    date = get_date_from_latest_email()
    if date.day != datetime.today().day:
        return True
    else:
        return False


def read_log_file():

    file = get_log_file()

    with open(file) as f:
        content = f.read()

    return content


def write_to_log_file():

    file = get_log_file()
    message = read_log_file() + 'TVGuide was sent on ' + datetime.strftime(datetime.today(), '%d-%m-%y') + ' at ' + \
        datetime.strftime(datetime.today(), '%H:%M')
    with open(file, 'w') as fd:
        fd.write(message + '\n')


def delete_latest_entry():

    contents = read_log_file()
    lines = contents.splitlines(True)
    lines.pop(-1)
    log_string = ''
    for line in lines:
        log_string = log_string + line

    with open(get_log_file(), 'w') as fd:
        fd.write(log_string)
