from datetime import datetime as dt


def get_date_from_latest_email():

    arr = []
    
    with open('log/emails.txt') as f:
        for line in f:
            if '\n' in line:
                arr.append(line[:-1])
            else:
                arr.append(line)

    latest_email = arr[-1]
    idx_front = latest_email.find('on ')
    idx_back = latest_email.find(' at ')
    date = latest_email[idx_front+3:idx_back]
    time = latest_email[idx_back+4:].split(':')
    date_parsed = dt.strptime(date, '%d-%m-%y')
    new_date_parsed = date_parsed.replace(hour=int(time[0]), minute=int(time[1]))

    print(new_date_parsed)
    return new_date_parsed


def compare_dates():

    date = get_date_from_latest_email()
    if date.day != dt.today().day:
        return True
    else:
        if date.hour <= 6:
            return True
        else:
            return False


def read_file():

    with open('log/emails.txt') as fd:
        data = fd.read()

    return data


def write_to_backup():
    contents = read_file()

    with open('log/backup_log.txt', 'w') as fd:
        fd.write(contents)


def write_to_log_file():

    write_to_backup()
    
    contents = read_file().splitlines(True)
    if len(contents) > 1:
        new_log = [contents[1]]
    new_log.append('\nTVGuide was sent on ' + dt.strftime(dt.today(), '%d-%m-%y') + ' at ' + dt.strftime(dt.today(), '%H:%M'))
    
    with open('log/emails.txt', 'w') as fd:
        for line in new_log:
            fd.write(line)


def delete_latest_entry():
    with open('log/backup_log.txt') as fd:
        backup = fd.read()

    with open('log/emails.txt', 'w') as fd:
        fd.write(backup)
