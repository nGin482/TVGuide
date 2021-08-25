from backups import write_to_backup_file
from repeat_handler import flag_repeats, tear_down
from guide import organise_guide
from aux_methods import get_today_date, get_current_time, convert_date_string_to_object, get_today_date_for_logging
import json
import os


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
    date_parsed = convert_date_string_to_object(date)
    new_date_parsed = date_parsed.replace(hour=int(time[0]), minute=int(time[1]))

    print(new_date_parsed)
    return new_date_parsed


def compare_dates():

    date = get_date_from_latest_email()
    if date.day != get_today_date('object').day:
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


def log_message_sent():

    write_to_backup()
    
    contents = read_file().splitlines(True)
    if len(contents) > 1:
        new_log = [contents[1]]
    new_log.append('\nTVGuide was sent on ' + get_today_date_for_logging() + ' at ' + get_current_time('string'))
    
    with open('log/emails.txt', 'w') as fd:
        for line in new_log:
            fd.write(line)


def delete_latest_entry():
    with open('log/backup_log.txt') as fd:
        backup = fd.read()

    with open('log/emails.txt', 'w') as fd:
        fd.write(backup)

def read_events():
    try:
        with open('log/events.json') as fd:
            events = json.load(fd)
        return events
    except FileNotFoundError:
        return []

def status_setting_repeats(result):
    events = read_events()
    
    events.append(result)

    with open('log/events.json', 'w+') as fd:
        json.dump(events, fd, indent='\t')


def clear_events_log():
    try:
        with open('log/events.json', 'w') as fd:
            json.dump([], fd)
    except FileNotFoundError:
        return

def log_guide_information(fta_shows, bbc_shows):
    """
    Organise the guide into a JSON format and write this to the current day's guide and to the BackUp directory
    """

    # Remove previous day's guide
    if not os.path.isdir('today_guide'):
        os.mkdir('today_guide')
    else:
        for filename in os.listdir('today_guide'):
            if os.path.exists('today_guide/' + filename):
                os.remove('today_guide/' + filename)

    for show in fta_shows:
        show['time'] = show['time'].strftime('%H:%M')
    for show in bbc_shows:
        show['time'] = show['time'].strftime('%H:%M')
    
    today_guide = {'FTA': fta_shows, 'BBC': bbc_shows}
    filename = 'today_guide/' + get_today_date('string') + '.json'
    with open(filename, 'w+', encoding='utf-8') as fd:
        json.dump(today_guide, fd, ensure_ascii=False, indent=4)
    
    guide = organise_guide(fta_shows, bbc_shows)
    write_to_backup_file(guide)

def log_guide(fta_shows, bbc_shows):

    # log_guide_information(fta_shows, bbc_shows)
    
    clear_events_log()
    for show in fta_shows:
        if 'HD' not in show['channel'] and 'GEM' not in show['channel'] and show['episode_info']:
            log_repeats = flag_repeats(show)
            status_setting_repeats(log_repeats)
    for show in bbc_shows:
        log_repeats = flag_repeats(show)
        status_setting_repeats(log_repeats)
    tear_down()
