from datetime import datetime
import pytz

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

def parse_datetime(date_time: str, format: str):
    """
    Parses a given `date_time` string using a given `format`.\n
    Returns a timezone aware object
    """
    parsed_datetime = datetime.strptime(date_time, format)
    parsed_datetime = pytz.timezone("Australia/Sydney").localize(parsed_datetime)
    return parsed_datetime