from datetime import datetime
import sys
from data_validation.validation import Validation
from database.models.GuideShowCases import TransformersGuideShow, DoctorWho, MorseGuideShow, RedElection, SilentWitness
from database.models.RecordedShow import RecordedShow
from exceptions.DatabaseError import EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError
from log import log_imdb_api_results, logging_app
import requests
import logging
import os

from services.imdb_api import search_for_episode_title, search_for_season_number

class GuideShow:
    
    def __init__(self, title: str, channel: str, time: datetime, season_number: str, episode_number: int, episode_title: str, recorded_show: RecordedShow) -> None:
        title = Validation.check_show_titles(title)
        episode_title = Validation.format_episode_title(episode_title)
        repeat = False
        self._episode_checked = False
        
        self.recorded_show = recorded_show
        
        # check show handlers
        episode_data = GuideShow.get_show(title, season_number, episode_title)
        if isinstance(episode_data, tuple) and len(episode_data) > 1:
            title, season_number, episode_number, episode_title = episode_data
            self._episode_checked = True
        if not self._episode_checked:
            # check database
            check_existing_episode = GuideShow.find_episode(title, season_number, episode_number, episode_title, recorded_show)
            if check_existing_episode:
                season_number, episode_number, episode_title, repeat = check_existing_episode
                self._episode_checked = True
            else:
                if season_number == 'Unknown' and self.recorded_show is not None:
                    if self.recorded_show.find_season('Unknown') is not None:
                        episode_number = max(episode.episode_number for episode in self.recorded_show.find_season('Unknown').episodes) + 1
                    else:
                        episode_number = 1
        
        self.title = title
        self.channel = channel
        self.time = time
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.repeat = repeat

    @staticmethod
    def get_show(title: str, season_number, episode_title) -> tuple:
        if 'Transformers' in title or 'Bumblebee' in title:
            return TransformersGuideShow.handle(title)
        elif 'Doctor Who' in title:
            return DoctorWho.handle(title)
        elif 'Morse' in title:
            return MorseGuideShow.handle(title)
        elif 'Red Election' in title:
            return RedElection.handle(title, season_number, episode_title)
        elif 'Silent Witness' in title:
            return SilentWitness.handle(season_number, episode_title)
        else:
            return Validation.check_show_titles(title)

    @staticmethod
    def find_episode(show_title: str, season_number: str, episode_number: int, episode_title: str, recorded_show: 'RecordedShow'):
        
        if (season_number == 'Unknown' and episode_number == 0 and episode_title == '') or recorded_show is None:
            return False
        
        repeat = False
        if episode_title != '' and season_number == 'Unknown':
            search_by_title = GuideShow.check_database_for_episode(episode_title, recorded_show)
            if search_by_title is not None:
                season_number, episode_number = search_by_title
                repeat = True
            if season_number == 'Unknown':
                imdb_search = search_for_season_number(show_title, episode_title)
                if imdb_search is not None:
                    season_number, episode_number = imdb_search

            return season_number, episode_number, episode_title, repeat
        else:
            season = recorded_show.find_season(season_number)
            if season:
                episode = season.find_episode(episode_number, episode_title)
                if episode:
                    repeat = True
            else:
                # remove from unknown season
                episode_title = search_for_episode_title(show_title, season_number, episode_number, recorded_show.imdb_id)
                if episode_title is None:
                    episode_title = ''
            return season_number, episode_number, episode_title, repeat

    @staticmethod
    def check_database_for_episode(episode_title: str, recorded_show: 'RecordedShow'):
        """Given an `episode_title`, search the database for every episode that contains this title.\n
        Use `RecordedShow.find_episode_instances(episode_title)`, which will return a list of tuples containing the `season_numbers` and `episode_numbers`.\n
        If the `episode_title` appears more than once, prioritise returning the episode that is not contained within the `Unknown` season.
        If that can be done, delete the episode from the `Unknown` season.
        If this is not possible, return the earliest episode occurrence.\n
        If it appears once, return this tuple\n
        If it does not appear, return `None`"""
        if recorded_show is None:
            return None
        instances = recorded_show.find_episode_instances(episode_title)
        if len(instances) > 2:
            print(f"Episode {episode_title} appears too many times in {recorded_show.title}'s document")
            print(instances)
        if len(instances) == 0:
            return None
        elif len(instances) == 1:
            return instances[0]
        else:
            known_instance = next((instance for instance in instances if instance[0] != 'Unknown'), None)
            if known_instance:
                unknown_season = recorded_show.find_season('Unknown')
                if unknown_season:
                    print(f'{recorded_show.title} Unknown season found')
                    episode_in_unknown_season = unknown_season.find_episode(episode_title=episode_title)
                    if episode_in_unknown_season:
                        print(f'{recorded_show.title} episode found')
                        episode_in_unknown_season.remove_unknown_episode(recorded_show.title)
                        unknown_season.episodes.remove(episode_in_unknown_season)
            return known_instance

    def update_episode_number_with_guide_list(self, shows_list: list['GuideShow']):
        """
        Update the `episode_number`, taking into account the number of shows matching the `title` with `season_number == 'Unknown'`
        Takes a filtered list of `GuideShow` objects based on the show's title and if `season_number == 'Unknown'`
        """
        if self._episode_checked:
            return
        index = None
        for idx, guide_show in enumerate(shows_list):
            if self.episode_title == guide_show.episode_title:
                index = idx
                break
        self.episode_number = self.recorded_show.find_number_of_unknown_episodes() + index + 1

    def find_recorded_episode(self):
        """
        Checks the local files in the `shows` directory for information about a `GuideShow`'s information\n
        Raises `EpisodeNotFoundError` if the episode can't be found in the database.\n
        Raises `SeasonNotFoundError` if the season can't be found in the database.\n
        Raises `ShowNotFoundError` if the show can't be found in the database.
        """
        # check_show = get_one_recorded_show(show['title'])
        if self.recorded_show:
            season = self.recorded_show.find_season(self.season_number)
            if season:
                episode = season.find_episode(episode_number=self.episode_number, episode_title=self.episode_title)
                if episode:
                    return episode
                else:
                    raise EpisodeNotFoundError
            else:
                raise SeasonNotFoundError
        else:
            raise ShowNotFoundError

    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel}'
        message += f' (Season {self.season_number}, Episode {self.episode_number}'
        if self.episode_title != '':
            message += f': {self.episode_title}'
        message += ')'
        if self.repeat:
            message = f'{message} (Repeat)'

        return f'{message}\n'

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'channel': self.channel,
            'time': self.time.strftime('%H:%M'),
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat
        }

    def __repr__(self) -> str:
        return self.message_string()[:-1]

    def __eq__(self, other: 'GuideShow') -> bool:
        return self.title == other.title and self.channel == other.channel and self.time == self.time

    def __hash__(self) -> int:
        return hash((self.title, self.channel, self.time))

