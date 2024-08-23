from __future__ import annotations
from datetime import date, datetime, timedelta
import pytz
import re

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow
    from database.models.SearchItem import SearchItem

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

def show_list_message(search_list: list[SearchItem]):
    """Return a message-friendly version of the shows being searched for"""
    return '\n'.join([search_item.show for search_item in search_list])

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

def parse_date_from_command(date: str):
    if re.search(r'\d{1,2}(-|\/)\d{1,2}(-|\/)\d{2,4}', date) is not None:
        if '-' in date:
            try:
                return datetime.strptime(date, '%d-%m-%Y')
            except ValueError:
                date_values = date.split('-')
                date_formatted = f'{date_values[0]}-{date_values[1]}-20{date_values[2]}'
                return datetime.strptime(date_formatted, '%d-%m-%Y')
        else:
            try:
                return datetime.strptime(date, '%d/%m/%Y')
            except ValueError:
                date_values = date.split('/')
                date_formatted = f'{date_values[0]}/{date_values[1]}/20{date_values[2]}'
                return datetime.strptime(date_formatted, '%d/%m/%Y')
    else:
        date_search = re.search(r'\d{1,2}(-|\/| )(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)(-|\/| )\d{2,4}', date)
        print(date_search)
        if date_search is not None:
            if '-' in date:
                date_values = date_search.group().split('-')
            elif '/' in date:
                date_values = date_search.group().split('/')
            else:
                date_values = date_search.group().split(' ')
            if len(date_values[1]) == 3:
                month = datetime.strptime(date_values[1], '%b').month
            else:
                month = datetime.strptime(date_values[1], '%B').month
            if len(date_values[2]) == 2:
                year = f'20{date_values[2]}'
            else:
                year = date_values[2]
            return datetime(int(year), month, int(date_values[0]))
        else:
            raise ValueError('The date provided was not in a valid format.')

def convert_utc_to_local(utc_timestamp: datetime):
    utc_timestamp = utc_timestamp.replace(tzinfo=pytz.utc)
    local_time = utc_timestamp.astimezone(pytz.timezone('Australia/Sydney'))
    return local_time

def build_episode(show_title: str, channel: str, start_time: datetime, end_time: datetime, season_number: str, episode_number: int, episode_title: str):
    from data_validation.validation import Validation
    episodes = []
    if 'Cyberverse' in show_title and '/' in episode_title:
        episode_titles = episode_title.split('/')
        for idx, episode in enumerate(episode_titles):
            episodes.append({
                'title': show_title,
                'channel': channel,
                'time': start_time + timedelta(minutes=14) if idx == 1 else start_time,
                'season_number': season_number,
                'episode_number': episode_number,
                'episode_title': Validation.format_episode_title(episode.title())
            })
    else:
        if 'SBS' in channel:
            sbs_format = sbs_episode_format(show_title, episode_title)
            if isinstance(sbs_format, tuple):
                season_number, episode_number = sbs_format
        episodes.append({
            'title': show_title,
            'channel': channel,
            'start_time': start_time,
            'end_time': end_time,
            'season_number': season_number,
            'episode_number': episode_number,
            'episode_title': Validation.format_episode_title(episode_title)
        })
    return episodes

def split_message_by_time(message: str):
    """
    Use regex to search for any show starting between 12:00 and 13:00 in the given `message`.
    Split the given message into two substrings:\n
    all shows from 00:00 to 12:59\n
    all shows from 13:00 to 23:59.
    """

    am_index = re.search(r"12:[0-5][0-9]", message).start()
    am_message = message[0:am_index]
    pm_message = message[am_index:]

    return am_message, pm_message

def sbs_episode_format(show_title: str, episode: str):
    search = re.match(rf"{show_title} Series \d+ Ep \d+", episode)
    if search:
        numbers = tuple(int(number) for number in re.findall(r"\d+", episode))
        return numbers
    else:
        return episode
