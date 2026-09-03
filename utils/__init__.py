from datetime import datetime, timedelta
import pytz
import re

from utils.types import ShowData

def get_current_date():
    return datetime.now(pytz.timezone('Australia/Sydney'))

def parse_show(title: str, season_number: int, episode_number: int, episode_title: str):
    from utils import transformers_handler

    if 'Transformers' in title or 'Bumblebee' in title:
        handle_result = transformers_handler.handle_transformers_shows(title)
        if isinstance(handle_result, str):
            return handle_result, season_number, episode_number, episode_title
        return handle_result
    if ': ' in title and episode_title == "":
        title, episode_title = title.split(': ')
    if ' - ' in title and episode_title == "":
        title, episode_title = title.split(' - ')
    if f'{title} - ' in episode_title:
        episode_title = episode_title.split(' - ')[1]
    return check_show_titles(title), season_number, episode_number, episode_title

def check_show_titles(show_title: str):
    if 'Maigret' in show_title:
        return 'Maigret'
    elif 'Death in Paradise' in show_title:
        return 'Death In Paradise'
    elif 'Grantchester Christmas Special' in show_title:
        return 'Grantchester'
    elif 'NCIS Encore' in show_title:
        return 'NCIS'
    # if 'Christmas Special' in show_title and 'Christmas Special' not in episode_title:
    #     split_title = show_title.split('Christmas Special')
    #     episode_title += 'Christmas Special'
    return show_title


def format_episode_title(episode_title: str):
    """
    Format a show's episode title into a more reader-friendly appearance
    """

    if ', The' in episode_title:
        idx_the = episode_title.find(', The')
        if episode_title[idx_the:] == ", The":
            episode_title = 'The ' + episode_title[0:idx_the]
    if ', A' in episode_title and episode_title != 'Kolcheck, A.':
        idx_a = episode_title.find(', A')
        if episode_title[idx_a:] == ", A":
            episode_title = 'A ' + episode_title[0:idx_a]
    return episode_title

def parse_datetime(date_object: datetime, date_string: str = "", format: str = ""):
    """
    Parses a given `date_time` string using a given `format`.\n
    Returns a timezone aware object
    """
    if not date_object:
        if not (date_string and format) or (date_string == "" and format == ""):
            raise TypeError("A date string and format must be provided")
        parsed_datetime = datetime.strptime(date_string, format)
    else:
        parsed_datetime = date_object
    return pytz.timezone("Australia/Sydney").localize(parsed_datetime)

def build_episode(
    show_title: str,
    channel: str, 
    start_time: datetime,
    end_time: datetime,
    season_number: int,
    episode_number: int,
    episode_title: str
):
    show_title, season_number, episode_number, episode_title = parse_show(
        show_title,
        season_number,
        episode_number,
        episode_title
    )

    episodes: list[ShowData] = []
    if 'Cyberverse' in show_title and '/' in episode_title:
        episode_titles = episode_title.split('/')
        for idx, episode in enumerate(episode_titles):
            episodes.append({
                'title': show_title,
                'channel': channel,
                'start_time': start_time + timedelta(minutes=14) if idx == 1 else start_time,
                'end_time': end_time,
                'season_number': season_number,
                'episode_number': episode_number,
                'episode_title': format_episode_title(episode.title())
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
            'episode_title': format_episode_title(episode_title)
        })
    return episodes

def sbs_episode_format(show_title: str, episode: str):
    search = re.match(rf"{show_title} Series \d+ Ep \d+", episode)
    if search:
        numbers = tuple(int(number) for number in re.findall(r"\d+", episode))
        return numbers
    else:
        return episode

def show_data_to_file(shows: list[ShowData], filename="shows.json"):
    import copy
    import json
    import os

    shows_copy = copy.deepcopy(shows)
    for show in shows_copy:
        show['start_time'] = datetime.strftime(show['start_time'], "%d-%m-%Y %H:%M")
        show['end_time'] = datetime.strftime(show['end_time'], "%d-%m-%Y %H:%M")

    folder_name = "shows_snapshots"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    file_path = os.path.join(folder_name, filename)
    with open(file_path, "w+") as fd:
        json.dump(shows_copy, fd, indent="\t")

    return file_path