from __future__ import annotations
from datetime import datetime, timedelta
import re

from utils.types import ShowData
import utils



def build_episode(
    show_title: str,
    channel: str, 
    start_time: datetime,
    end_time: datetime,
    season_number: int,
    episode_number: int,
    episode_title: str
):
    show_title, season_number, episode_number, episode_title = utils.parse_show(
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
                'episode_title': utils.format_episode_title(episode.title())
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
            'episode_title': utils.format_episode_title(episode_title)
        })
    return episodes

def sbs_episode_format(show_title: str, episode: str):
    search = re.match(rf"{show_title} Series \d+ Ep \d+", episode)
    if search:
        numbers = tuple(int(number) for number in re.findall(r"\d+", episode))
        return numbers
    else:
        return episode



def show_data_to_file(shows: list[ShowData]):
    import copy
    import json
    import os
    from services.hermes.hermes import hermes

    shows_copy = copy.deepcopy(shows)
    for show in shows_copy:
        show['start_time'] = datetime.strftime(show['start_time'], "%d-%m-%Y %H:%M")
        show['end_time'] = datetime.strftime(show['end_time'], "%d-%m-%Y %H:%M")

    if not os.path.isdir("backup"):
        os.mkdir("backup")
    with open("backup/shows.json", "w+") as fd:
        json.dump(shows_copy, fd, indent="\t")

    hermes.dispatch("shows_collected")