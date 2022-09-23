from __future__ import annotations
from datetime import datetime
from pymongo import ReturnDocument
from pymongo.errors import OperationFailure
from database.mongo import database, recorded_shows_collection
from exceptions.DatabaseError import DatabaseError
import json
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .GuideShow import GuideShow

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


    def mark_as_repeat(self, guide_show: 'GuideShow') -> dict:
        self.repeat = True

        season_number = 'Unknown' if guide_show.season_number == '' else guide_show.season_number
        if 'Unknown' in season_number:
            episode_map = {'episode.episode title': guide_show.episode_title}
        else:
            episode_map = {'episode.episode number': guide_show.episode_number}
        
        updated_show = recorded_shows_collection().find_one_and_update(
            {'show': guide_show.title},
            {'$set': {'seasons.$[season].episodes.$[episode].repeat': True}},
            upsert = False,
            array_filters = [
                {'season.season number': season_number},
                episode_map
            ],
            return_document = ReturnDocument.AFTER
        )

        if len(updated_show.keys()) == 0:
            raise DatabaseError('The episode in the `RecordedShows` collection was not updated')
        return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': self.to_dict()}
    
    def update_latest_air_date(self):
        self.latest_air_date = datetime.today().strftime('%d/%m/%Y')

    def add_channel(self, channel: str):
        """Add the given channel to the episode's channel list.\n
        If the channel is `ABC1`, `ABCHD` will also be added.\n
        If the channel is `TEN`, `TENHD` will also be added."""
        self.channels.append(channel)
        if 'ABC1' in channel:
            self.channels.append('ABCHD')
            return f'{channel} and ABCHD have been added to the channel list.'
        elif 'TEN' in channel or '10' in channel:
            self.channels.append('TENHD')
            return f'{channel} and TENHD have been added to the channel list.'
        else:
            return f'{channel} has been added to the channel list.'
        
    def update_episode_in_database(self, show_title: str, season_number: str):
        try:
            recorded_shows_collection().find_one_and_update(
            {'show': show_title},
            {'$set': {'seasons.$[season].episodes.$[episode]': self.to_dict()}},
            array_filters = [
                {'season.season_number': season_number},
                {'episode.episode_number': self.episode_number}
            ],
            return_document = ReturnDocument.AFTER
        )
        except OperationFailure as err:
            raise DatabaseError(f"An error occurred when trying to update this episode of {show_title}. Error: {str(err)}")
        return True

    def remove_unknown_episode(self, show_title: str):
        """
        Rollback the `RecordedShows` collection to a point before the TVGuide has interacted with the DB for the current day
        """
        
        recorded_shows_collection().find_one_and_update(
            {'show': show_title},
            {'$pull': {'seasons.$[season].episodes': {'episode_title': self.episode_title}}},
            array_filters = [
                {'season.season_number': 'Unknown'}
            ],
            return_document=ReturnDocument.AFTER
        )

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
            return None
        else:
            if episode_number != 0:
                results = list(filter(lambda episode_obj: str(episode_obj.episode_number) == str(episode_number), self.episodes))
            else:
                results = list(filter(lambda episode_obj: episode_obj.episode_title == episode_title, self.episodes))
            if len(results) > 0:
                return results[0]
            return None

    def add_episode_to_season(self, show_title: str, episode: Episode):
        """Add the new given `Episode` to the document's collection"""
        recorded_shows_collection().find_one_and_update(
            {'show': show_title},
            {'$push': {'seasons.$[season].episodes': episode.to_dict()}},
            array_filters=[
                {'season.season_number': self.season_number}
            ],
            return_document=ReturnDocument.AFTER
        )
    
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
    recorded_shows_collection = database().get_collection('RecordedShows')
    
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
    
    @staticmethod
    def get_all_recorded_shows():
        try:
            collection = recorded_shows_collection().find()
            return [recorded_show for recorded_show in collection]
        except AttributeError:
            return []

    @staticmethod
    def get_one_recorded_show(show_title) -> dict:
        return recorded_shows_collection().find_one({'show': show_title})
    
    def find_season(self, season_number) -> Season:
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

    def insert_new_recorded_show_document(self):
        document = self.to_dict()
        insert_result = recorded_shows_collection().insert_one(document)
        if not insert_result.inserted_id:
            raise DatabaseError('The show was not able to be recorded.')
        else:
            return 'The show is now being recorded.'

    def add_season(self, season: Season):
        """
        Appends the given `Season` object to the list of seasons. Also inserts the `Season` document into the MongoDB collection.\n
        Raises an `exceptions.DatabaseError` if inserting the document fails.
        """
        self.seasons.append(season)

        inserted_season: dict = recorded_shows_collection().find_one_and_update(
            {'show': self.title},
            {'$push': {'seasons': season.to_dict()}},
            return_document=ReturnDocument.AFTER
        )

        if len(inserted_season.keys()) == 0:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection')
        return 'The season was successfully inserted'

    def find_number_of_unknown_episodes(self):
        unknown_season = self.find_season('Unknown')
        if unknown_season:
            return len(unknown_season.episodes)
        return 0
    
    def find_episode_by_episode_title(self, episode_title: str):
        for season in self.seasons:
            for episode in season.episodes:
                if episode.episode_title == episode_title:
                    if season.season_number != "Unknown":
                        return season.season_number, episode.episode_number
    
    @staticmethod
    def backup_recorded_shows():
        """
        Create a local backup of the `RecordedShows` collection by storing data locally in JSON files
        """
        
        all_recorded_shows = RecordedShow.get_all_recorded_shows()

        for recorded_show in all_recorded_shows:
            del recorded_show['_id']
            show_name: str = recorded_show['show']
            if os.path.isdir('database/backups/recorded_shows'):
                with open(f'database/backups/recorded_shows/{show_name}.json', 'w+') as fd:
                    json.dump(recorded_show, fd, indent='\t')
            else:
                os.mkdir('database/backups/recorded_shows')
                with open(f'database/backups/recorded_shows/{show_name}.json', 'w+') as fd:
                    json.dump(recorded_show, fd, indent='\t')
    
    @staticmethod
    def rollback_recorded_shows_collection():
        """
        Rollback the `RecordedShows` collection to a point before the TVGuide has interacted with the DB for the current day
        """
        
        for recorded_show in os.listdir('database/backups/recorded_shows'):
            print(recorded_show)
            with open(f'database/backups/recorded_shows/{recorded_show}') as fd:
                show_data = json.load(fd)
            show_name: str = show_data['show']
            recorded_shows_collection().find_one_and_update(
                {'show': show_name},
                {'$set': {'seasons': show_data['seasons']}},
                return_document=ReturnDocument.AFTER
            )
            # how to notify that this is done
        pass
    
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