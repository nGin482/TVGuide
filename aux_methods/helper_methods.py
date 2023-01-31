from __future__ import annotations
from datetime import date, datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

def format_time(time):
    """
    format a show's start time to 24 hour time
    :param time: show start_time to format that will be passed as string
    :return: the formatted time string
    """

    idx = time.find(':')

    if " " in time:
        time = time[1:7]
    if len(time) == 6:
        time = '0' + time
    if 'pm' in time:
        time = time[:-2]
        if time[:idx] != '12':
            hour = int(time[:idx]) + 12
            time = str(hour) + time[idx:]
    if 'am' in time:
        time = time[:-2]
        if time[:idx] == '12':
            hour = int(time[:idx]) - 12
            time = str(hour) + '0' + time[idx:]

    return time


def remove_doubles(shows_list: list[GuideShow]):

    idx_1 = 0
    if len(shows_list) > 1:
        while idx_1 < len(shows_list)-1:
            show_1 = shows_list[idx_1]
            idx_2 = idx_1 + 1
            while idx_2 < len(shows_list):
                show_2 = shows_list[idx_2]
                if show_1.channel == show_2.channel and show_1.time == show_2.time:
                    shows_list.remove(show_2)
                idx_2 += 1
            idx_1 += 1


def format_title(title: str):
    """
    Format a show's given title into a more reader-friendly appearance
    """

    if ', The' in title:
        idx_the = title.find(', The')
        title = f'The {title[0:idx_the]}'
    if ', A' in title:
        idx_a = title.find(', A')
        title = f'A {title[0:idx_a]}'

    return title

def show_list_message(shows_list: list[str]):
    """Return a message-friendly version of the shows being searched for"""
    return '\n'.join(shows_list)

def check_show_titles(show):
    if type(show) is str:
        if 'Maigret' in show:
            return 'Maigret'
        if 'Death in Paradise' in show:
            return 'Death In Paradise'
        if 'Revenge Of The Fallen' in show or 'Dark Of The Moon' in show \
                or 'Age of Extinction' in show or 'The Last Knight' in show:
            return 'Transformers'
        elif show == 'Transformers':
            return 'Transformers'
        else:
            title = show
            if ':' in title:
                idx = title.rfind(':')
                title = title[:idx] + title[idx+1:]
            return title
    else:
        if 'Maigret' in show['title']:
            return 'Maigret'
        if 'Death in Paradise' in show['title']:
            return 'Death In Paradise'
        if 'Revenge Of The Fallen' in show['title'] or 'Dark Of The Moon' in show['title'] \
                or 'Age of Extinction' in show['title'] or 'The Last Knight' in show['title']:
            return 'Transformers'
        elif show['title'] == 'Transformers':
            return 'Transformers'
        else:
            title: str = show['title']
            if ':' in title:
                idx = title.rfind(':')
                title = title[:idx] + title[idx+1:]
            return title

def valid_reminder_fields():
    """
    Returns the fields only valid for a reminder document
    """
    return ['show', 'reminder time', 'interval']

def get_today_date(return_type):
    if return_type == 'string':
        return date.today().strftime('%d-%m-%Y')
    else:
        return date.today()

def get_today_date_for_logging():
    return date.today().strftime('%d-%m-%y')

def convert_date_string_to_object(given_date):
    return datetime.strptime(given_date, '%d-%m-%y')

def get_current_time(return_type):
    if return_type == 'string':
        return datetime.now().strftime('%H:%M')

def show_string(show: dict):
    message = '{time}: {title} is on {channel}'.format(**show)
    if 'series_num' in show.keys() and 'episode_title' in show.keys():
        message = message + ' (Season {series_num}, Episode {episode_num}: {episode_title})'.format(**show)
    else:
        if 'series_num' in show.keys():
            message = message + ' (Season {series_num}, Episode {episode_num})'.format(**show)
        if 'episode_title' in show.keys():
            message = message + ' ({episode_title})'.format(**show)
    if show['repeat']:
        message = message + '(Repeat)'
    message = message + '\n\n'

    return message