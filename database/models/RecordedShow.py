from __future__ import annotations
from datetime import datetime
from pymongo import ReturnDocument
from database.mongo import recorded_shows_collection
from data_validation.validation import Validation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Episode:
    
    def __init__(
            self,
            episode_number: int,
            episode_title: str,
            alternative_titles: list[str],
            summary: str,
            channels: list[str],
            air_dates: list[datetime]
        ) -> None:
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.alternative_titles = alternative_titles
        self.summary = summary
        self.channels = channels
        self.air_dates = air_dates

    @classmethod
    def from_guide_show(cls, guide_show: 'GuideShow'):
        """
        Used when adding a new `Episode` to a `Season`
        """
        channels = [guide_show.channel]
        if 'ABC1' in channels:
            channels.append('ABCHD')
        if 'TEN' in channels:
            channels.append('TENHD')
        date = Validation.get_current_date()
        return cls(guide_show.episode_number, guide_show.episode_title, [], "", channels, [date])

    @classmethod
    def from_database(cls, recorded_episode: dict):
        """
        Used when retrieving a `RecordedShow` document from the MongoDB collection
        """
        episode_number = int(recorded_episode['episode_number'])
        episode_title: str = recorded_episode['episode_title']
        alternative_titles: list[str] = recorded_episode['alternative_titles']
        summary: str = recorded_episode['summary'] if recorded_episode['summary'] is not None else ""
        channels: list[str] = recorded_episode['channels']
        air_dates = [datetime.strptime(air_date, '%d/%m/%Y') for air_date in recorded_episode['air_dates']]

        return cls(episode_number, episode_title, alternative_titles, summary, channels, air_dates)

    def add_channel(self, channel: str):
        """Add the given channel to the episode's channel list.\n
        If the channel is `ABC1`, `ABCHD` will also be added.\n
        If the channel is `TEN`, `TENHD` will also be added.\n
        If the channel is `SBS`, `SBSHD` will also be added.\n"""
        if channel not in self.channels:
            self.channels.append(channel)
        if 'ABC1' in channel or ('ABC1' in self.channels and 'ABCHD' not in self.channels):
            self.channels.append('ABCHD')
            return f'{channel} and ABCHD have been added to the channel list.'
        elif ('TEN' in channel or '10' in channel) or ('10' in self.channels and 'TENHD' not in self.channels):
            self.channels.append('TENHD')
            return f'{channel} and TENHD have been added to the channel list.'
        elif 'SBS' in channel or ('SBS' in self.channels and 'SBSHD' not in self.channels):
            self.channels.append('SBSHD')
            return f'{channel} and SBSHD have been added to the channel list.'
        else:
            return f'{channel} has been added to the channel list.'

    def channel_check(self, channel: str):
        """Check that the given episode is present in the episode's channel list. Return True if present, False if not.\n
        If `ABC1` is present, also check `ABCHD`.\n
        If `SBS` is present, also check `SBSHD`.\n
        If `10` is present, also check `TENHD`.\n"""

        if 'ABC1' in self.channels and 'ABCHD' not in self.channels:
            return False
        if 'SBS' in self.channels and 'SBSHD' not in self.channels:
            return False
        if '10' in self.channels and 'TENHD' not in self.channels:
            return False
        if channel not in self.channels:
            return False
        return True
    
    def is_repeat(self):
        return len(self.air_dates) >= 2
        
    def remove_unknown_episode(self, show_title: str):
        """
        Remove this episode from the given show's Unknown season
        """

        if show_title == 'NCIS':
            show = dict(recorded_shows_collection().find_one(
                {'show': show_title}
            ))
            unknown_season = dict([season for season in show['seasons'] if season['season_number'] == 'Unknown'][0])
            print(len(unknown_season['episodes']))
        
        recorded_shows_collection().find_one_and_update(
            {'show': show_title},
            {'$pull': {'seasons.$[season].episodes': {'episode_title': self.episode_title}}},
            array_filters = [
                {'season.season_number': 'Unknown'}
            ],
            return_document=ReturnDocument.AFTER
        )
        if show_title == 'NCIS':
            show = dict(recorded_shows_collection().find_one(
                {'show': show_title}
            ))
            unknown_season = dict([season for season in show['seasons'] if season['season_number'] == 'Unknown'][0])
            print(len(unknown_season['episodes']))

    def to_dict(self):
        return {
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'alternative_titles': self.alternative_titles,
            'summary': self.summary,
            'channels': self.channels,
            'air_dates': [datetime.strftime(date, '%d/%m/%Y') for date in self.air_dates]
        }

    def message_format(self):
        episode_message = f'Episode: {self.episode_number} - Episode Title: {self.episode_title} - Channels: {",".join(self.channels)} - '
        episode_message += f'First Airing: {self.air_dates[0].strftime("%d/%m/%Y")} - Latest Airing: {self.air_dates[-1].strftime("%d/%m/%Y")} - '
        if self.is_repeat():
            episode_message += 'Repeat'
        return episode_message

    def __repr__(self) -> str:
        return f"Episode [Episode Number: {self.episode_number}, Episode Title: {self.episode_title}, Channels: {self.channels}, Repeat: {self.is_repeat()}]"


class Season:
    
    def __init__(self, season_number: int, episodes: list['Episode']) -> None:
        self.season_number = season_number
        self.episodes = episodes

    @classmethod
    def from_guide_show(cls, guide_show: GuideShow):
        """
        Used when creating a new `Season` object from a `GuideShow` object
        """
        return cls(guide_show.season_number, [Episode.from_guide_show(guide_show)])

    @classmethod
    def from_database(cls, recorded_season: dict):
        """
        Used when creating a `Season` object from the existing values stored in a `RecordedShow`'s subdocument stored in the MongoDB collection
        """
        # print(recorded_season['season_number'])
        return cls(recorded_season['season_number'], [Episode.from_database(episode) for episode in recorded_season['episodes']])

    def find_episode(self, episode_number = 0, episode_title = ''):
        if episode_number == 0 and episode_title == '':
            raise ValueError('Please provide a value to either the episode_number or episode_title')
        else:
            if episode_title != "":
                episode = next((ep for ep in self.episodes if ep.episode_title.lower() == episode_title.lower()), None)
                if episode is None:
                    episode = next((ep for ep in self.episodes if episode_title in ep.alternative_titles), None)
            else:
                episode = next((ep for ep in self.episodes if ep.episode_number == episode_number), None)
            return episode

    def to_dict(self):
        season_dict: dict[str, str|list[Episode]] = {
            'season_number': self.season_number,
            'episodes': [episode.to_dict() for episode in self.episodes]
        }
        return season_dict

    def message_format(self):
        episodes = ''
        for episode in self.episodes:
            episodes += f'\t{episode.message_format()}\n'
        return f'Season: {self.season_number}\n{episodes}'

    def __repr__(self) -> str:
        return f'Season [Season Number: {self.season_number}, episodes: {self.episodes}]'

class RecordedShow:
    
    def __init__(self, show_title: str, seasons: list[Season], tvmaze_id: str) -> None:
        # self._id = recorded_show_details['_id']
        self.title = show_title
        self.seasons = seasons
        self.tvmaze_id = tvmaze_id

    @classmethod
    def from_guide_show(cls, guide_show: 'GuideShow'):
        """
        Used when creating a new `RecordedShow` object
        """

        return cls(guide_show.title, [Season.from_guide_show(guide_show)], '')

    @classmethod
    def from_database(cls, recorded_show_details: dict):
        """
        Used when creating a `RecordedShow` object from the existing document in the MongoDB collection
        """
        title: str = recorded_show_details['show']
        seasons = [Season.from_database(season) for season in recorded_show_details['seasons']]
        imdb_id = recorded_show_details['tvmaze_id'] if 'tvmaze_id' in recorded_show_details.keys() else ''
        return cls(title, seasons, imdb_id)
    
    def find_season(self, season_number: str):
        return next((season for season in self.seasons if str(season.season_number) == str(season_number)), None)
    
    def find_latest_season(self):
        if 'Doctor Who' in self.title:
            list_of_seasons = [season for season in self.seasons if season.season_number != 'Tennant Specials' and season.season_number != 'Smith Specials']
        else:
            list_of_seasons = self.seasons
        latest_season_number = max(int(season.season_number) for season in list_of_seasons)
        return self.find_season(str(latest_season_number))
    
    def get_unknown_episodes_count(self):
        unknown_season = self.find_season('Unknown')
        if unknown_season is not None:
            return max(episode.episode_number for episode in unknown_season.episodes)
        return 0

    def find_episode_instances(self, episode_title: str):
        """Search all seasons and return all instances where the given `episode_title` has been stored.\n
        Return as a list of tuples containing the `season_number` and `episode_number`
        """
        season_num = 0
        episode = None
        for season in self.seasons:
            episode_search = season.find_episode(episode_title=episode_title)
            if episode_search is not None:
                season_num = season.season_number
                episode = episode_search
        if season_num == 0 or episode is None:
            return None
        return season_num, episode
    
    def to_dict(self) -> dict:
        show_dict: dict[str, str|list] = {
            # '_id': self._id,
            'show': self.title,
            'seasons': [season.to_dict() for season in self.seasons],
            'tvmaze_id': self.tvmaze_id
        }

        return show_dict

    def message_format(self):
        seasons = ''
        for season in self.seasons:
            seasons = f'{seasons}\nSeason {season.season_number}: {len(season.episodes)} episodes'
        return f'{self.title}\nSeasons:\n{seasons}'

    def __repr__(self) -> str:
        return f"RecordedShow [Title: {self.title}, Seasons: {self.seasons}]"

    def __eq__(self, other: RecordedShow) -> bool:
        return self.title == other.title and len(self.seasons) == len(other.seasons)

    def __hash__(self) -> int:
        return hash((self.title, len(self.seasons)))