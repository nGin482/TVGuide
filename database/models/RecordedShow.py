from __future__ import annotations
from datetime import datetime
from pymongo import ReturnDocument
from database.mongo import recorded_shows_collection

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Episode:
    
    def __init__(self, episode_number: int, episode_title: str, channels: list[str], first_air_date: datetime, latest_air_date: datetime, repeat: bool) -> None:
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.channels = channels
        self.first_air_date = first_air_date
        self.latest_air_date = latest_air_date
        self.repeat = repeat

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
        return cls(guide_show.episode_number, guide_show.episode_title, channels, datetime.today(), datetime.today(), False)

    @classmethod
    def from_database(cls, recorded_episode: dict):
        """
        Used when retrieving a `RecordedShow` document from the MongoDB collection
        """
        episode_number = int(recorded_episode['episode_number'])
        episode_title: str = recorded_episode['episode_title']
        channels: list[str] = recorded_episode['channels']
        first_air_date: str = recorded_episode['first_air_date']
        if 'latest_air_date' in recorded_episode.keys():
            latest_air_date = str(recorded_episode['latest_air_date'])
            if '-' in latest_air_date:
                latest_air_date = latest_air_date.replace('-', '/')
            latest_air_date = datetime.strptime(latest_air_date, '%d/%m/%Y')
        else:
            latest_air_date = datetime.today()
        repeat: bool = recorded_episode['repeat']

        if '-' in first_air_date:
            first_air_date = first_air_date.replace('-', '/')
        first_air_date: datetime = datetime.strptime(first_air_date, '%d/%m/%Y')

        return cls(episode_number, episode_title, channels, first_air_date, latest_air_date, repeat)

    def add_channel(self, channel: str):
        """Add the given channel to the episode's channel list.\n
        If the channel is `ABC1`, `ABCHD` will also be added.\n
        If the channel is `TEN`, `TENHD` will also be added.
        If the channel is `SBS`, `SBSHD` will also be added.\n"""
        self.channels.append(channel)
        if 'ABC1' in channel:
            self.channels.append('ABCHD')
            return f'{channel} and ABCHD have been added to the channel list.'
        elif 'TEN' in channel or '10' in channel:
            self.channels.append('TENHD')
            return f'{channel} and TENHD have been added to the channel list.'
        elif 'SBS' in channel:
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
            'channels': self.channels,
            'first_air_date': self.first_air_date.strftime('%d/%m/%Y'),
            'latest_air_date': self.latest_air_date.strftime('%d/%m/%Y'),
            'repeat': self.repeat
        }

    def __repr__(self) -> str:
        return f"Episode [Episode Number: {self.episode_number}, Episode Title: {self.episode_title}, Channels: {self.channels}, Repeat: {self.repeat}]"


class Season:
    
    def __init__(self, season_number: str, episodes: list['Episode']) -> None:
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
        try:
            season_number = recorded_season['season_number']
        except KeyError:
            season_number = recorded_season['season number']
        return cls(season_number, [Episode.from_database(episode) for episode in recorded_season['episodes']])

    def find_episode(self, episode_number = 0, episode_title = '') -> Episode:
        if episode_number == 0 and episode_title == '':
            raise ValueError('Please provide a value to either the episode_number or episode_title')
        else:
            if self.season_number == 'Unknown':
                episode = next((ep for ep in self.episodes if ep.episode_title == episode_title), None)
            else:
                episode = next((ep for ep in self.episodes if ep.episode_number == episode_number), None)
            return episode

    def to_dict(self):
        season_dict = {
            'season_number': self.season_number,
            'episodes': []
        }
        for episode in self.episodes:
            season_dict['episodes'].append(episode.to_dict())
        
        return season_dict

    def __repr__(self) -> str:
        return f'Season [Season Number: {self.season_number}, episodes: {self.episodes}]'

class RecordedShow:
    
    def __init__(self, show_title: str, seasons: list[Season], imdb_id: str) -> None:
        # self._id = recorded_show_details['_id']
        self.title = show_title
        self.seasons = seasons
        self.imdb_id = imdb_id

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
        imdb_id = recorded_show_details['imdb_id'] if 'imdb_id' in recorded_show_details.keys() else ''
        return cls(title, seasons, imdb_id)
    
    def find_season(self, season_number: str) -> Season:
        results = list(filter(lambda season_obj: season_obj.season_number == season_number, self.seasons))
        if len(results) > 0:
            return results[0]
        return None
    
    def find_latest_season(self):
        if 'Doctor Who' in self.title:
            list_of_seasons = list(filter(lambda season: season.season_number != 'Tennant Specials' and season.season_number != 'Smith Specials', self.seasons))
        else:
            list_of_seasons = self.seasons
        latest_season_number = max(int(season.season_number) for season in list_of_seasons)
        return self.find_season(str(latest_season_number))

    def find_number_of_unknown_episodes(self):
        unknown_season = self.find_season('Unknown')
        if unknown_season:
            return len(unknown_season.episodes)
        return 0

    def find_episode_instances(self, episode_title: str) -> list[tuple[str, int]]:
        """Search all seasons and return all instances where the given `episode_title` has been stored.\n
        Return as a list of tuples containing the `season_number` and `episode_number`
        """
        instances: list[tuple] = []
        for season in self.seasons:
            for episode in season.episodes:
                if episode.episode_title == episode_title:
                    instances.append((season.season_number, episode.episode_number))
        return instances
    
    def to_dict(self) -> dict:
        show_dict = {
            # '_id': self._id,
            'show': self.title,
            'seasons': []
        }
        season: Season
        for season in self.seasons:
            show_dict['seasons'].append(season.to_dict())

        return show_dict

    def __repr__(self) -> str:
        return f"RecordedShow [Title: {self.title}, Seasons: {self.seasons}]"

    def __eq__(self, other: RecordedShow) -> bool:
        return self.title == other.title and len(self.seasons) == len(other.seasons)

    def __hash__(self) -> int:
        return hash((self.title, len(self.seasons)))