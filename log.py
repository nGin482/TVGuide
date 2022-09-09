from __future__ import annotations
from datetime import datetime
from backups import write_to_backup_file
from repeat_handler import tear_down
from aux_methods.helper_methods import get_current_time, convert_date_string_to_object, get_today_date_for_logging
from database.recorded_shows_collection import rollback_recorded_shows_collection
import logging
import json
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow


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
    if date.day != datetime.today().day:
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

def status_setting_repeats(result: dict):
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

def log_guide_information(fta_shows: list['GuideShow'], bbc_shows: list['GuideShow']):
    """
    Organise the guide into a JSON format and write this to the current day's guide and to the BackUp directory
    """

    # Remove previous day's guide
    if not os.path.isdir('today_guide'):
        os.mkdir('today_guide')
    else:
        for filename in os.listdir('today_guide'):
            if os.path.exists(f'today_guide/{filename}'):
                os.remove(f'today_guide/{filename}')

    fta_list = [show.to_dict() for show in fta_shows]
    bbc_list = [show.to_dict() for show in bbc_shows]
    
    today_guide = {'FTA': fta_list, 'BBC': bbc_list}
    with open(f'today_guide/{datetime.today().strftime("%d-%m-%Y")}.json', 'w+', encoding='utf-8') as fd:
        json.dump(today_guide, fd, ensure_ascii=False, indent=4)
    
    # guide = organise_guide(fta_shows, bbc_shows)
    write_to_backup_file(today_guide)

def log_guide(fta_shows: list['GuideShow'], bbc_shows: list['GuideShow']):

    log_guide_information(fta_shows, bbc_shows)
    
    clear_events_log()
    for show in fta_shows:
        if 'HD' not in show.channel and show.episode_info:
            log_event = show.capture_db_event()
            status_setting_repeats(log_event)
    for show in bbc_shows:
        log_event = show.capture_db_event()
        status_setting_repeats(log_event)
    tear_down()

def revert_tvguide():
    """
    Revert TVGuide to a state before the current day's message was sent
    """

    delete_latest_entry()
    rollback_recorded_shows_collection()

def log_discord_message_too_long(message_length, fta_length):

    today_date = datetime.today().strftime("%d-%m-%Y")
    log_message = f'{today_date}\nDiscord tried sending the TVGuide message.\nThe maximum character length of a Discord message is 2000.\n \
        The length of this message is {message_length} and the length of the Free to Air portion is {fta_length}.\n \
            As a result, the message was split into the Free to Air and BBC portions and on the AM/PM portions of Free to Air.' 

    try:
        with open('log/message_logging.txt') as fd:
            current_log_contents = fd.read()
    except FileNotFoundError:
        current_log_contents = ''
            
    with open('log/message_logging.txt', 'w', encoding='utf-8') as fd:
        fd.write(f'{current_log_contents}\n\n\n{log_message}')

def log_imdb_api_results(show: dict, imdb_results: dict):
    """
    Write the results from the IMDB API request to a JSON file
    """

    try:
        with open('log/imdb_api_results.json') as fd:
            results:list = json.load(fd)
    except FileNotFoundError:
        results: list[dict] = []

    results.append({'show': show, 'api_results': imdb_results})

    with open('log/imdb_api_results.json', 'w+') as fd:
        json.dump(results, fd, indent='\t')

def clear_imdb_api_results():
    """
    Remove existing results from IMDB API searches
    """

    with open('log/imdb_api_results.json', 'w+') as fd:
        json.dump([], fd)

def logging_app(log_info: str, level = logging.DEBUG):
    logging.basicConfig(filename='tvguide.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if level == logging.DEBUG:
        logging.debug(f"{log_info}\n")
    elif level == logging.INFO:
        logging.info(f"{log_info}\n")
    elif level == logging.WARNING:
        logging.warning(f"{log_info}\n")
    elif level == logging.ERROR:
        logging.error(f"{log_info}\n")
    elif level == logging.CRITICAL:
        logging.critical(f"{log_info}\n")