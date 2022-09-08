from __future__ import annotations
from datetime import datetime
from pymongo import ReturnDocument
from database.mongo import database
from exceptions.DatabaseError import DatabaseError
from ..recorded_shows_collection import recorded_shows_collection
import json

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
        Used when creating a new `RecordedShow` object
        """
        return cls(guide_show.episode_number, guide_show.episode_title, [guide_show.channel], datetime.today().strftime('%d/%m/%Y'), datetime.today().strftime('%d/%m/%Y'), guide_show.repeat)

    @classmethod
    def from_database(cls, recorded_episode: dict):
        """
        Used when retrieving a `RecordedShow` document from the MongoDB collection
        """
        if 'episode number' in recorded_episode.keys():
            episode_number = recorded_episode['episode number']
        else:
            episode_number = recorded_episode['episode_number']
        if 'episode title' in recorded_episode.keys():
            episode_title = recorded_episode['episode title']
        else:
            episode_title = recorded_episode['episode_title']
        if 'first air date' in recorded_episode.keys():
            first_air_date = recorded_episode['first air date']
        else:
            first_air_date = recorded_episode['first_air_date']
        if 'latest air date' in recorded_episode.keys():
            latest_air_date = recorded_episode['latest air date']
        elif 'latest_air_date' in recorded_episode.keys():
            latest_air_date = recorded_episode['latest_air_date']
        else:
            latest_air_date = datetime.today().strftime('%d/%m/%Y')
        
        if episode_number == '':
            episode_number = 0
        return cls(int(episode_number), episode_title, recorded_episode['channels'], first_air_date, latest_air_date, recorded_episode['repeat'])


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

    def add_channel(self, guide_show: GuideShow):
        self.channels.append(guide_show.channel)

        season_number = 'Unknown' if guide_show.season_number == '' else guide_show.season_number
        if 'Unknown' in season_number:
            episode_map = {'episode.episode title': guide_show.episode_title}
        else:
            episode_map = {'episode.episode number': guide_show.episode_number}
        
        updated_show = recorded_shows_collection().find_one_and_update(
            {'show': guide_show.title},
            {'$push': {'seasons.$[season].episodes.$[episode].channels': guide_show.channel}},
            upsert = True,
            array_filters = [
                {'season.season number': season_number},
                episode_map
            ],
            return_document = ReturnDocument.AFTER
        )

        if len(updated_show.keys()) == 0:
            raise DatabaseError('The episode in the `RecordedShows` collection was not updated')
        return {'status': True, 'message': f'{guide_show.channel} has been added to the channel list.', 'episode': self.to_dict()}

    def to_dict(self):
        if type(self.first_air_date) is not str:
            first_air_date = self.first_air_date.strftime('%d/%m/%Y')
        else:
            first_air_date = self.first_air_date
        if type(self.latest_air_date) is not str:
            latest_air_date = self.latest_air_date.strftime('%d/%m/%Y')
        else:
            latest_air_date = self.latest_air_date
        
        return {
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'channels': self.channels,
            'first_air_date': first_air_date,
            'latest_air_date': latest_air_date,
            'repeat': self.repeat
        }

    def __repr__(self) -> str:
        return f"Episode [Episode Number: {self.episode_number}, Episode Title: {self.episode_title}, Channels: {self.channels}, Repeat: {self.repeat}"


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

    def add_episode(self, episode: Episode):
        self.episodes.append(episode)
    
    def to_dict(self):
        season_dict = {
            'season number': self.season_number,
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
        Raises a `exceptions.DatabaseError` if inserting the document fails.
        """
        self.seasons.append(season)

        inserted_season: dict = recorded_shows_collection().find_one_and_update(
            {'show': self.title},
            {'$push': {'seasons': season.to_dict()}},
            return_document=ReturnDocument.AFTER
        )

        update_file_result = self.update_JSON_file()

        if len(inserted_season.keys()) == 0 and not update_file_result:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection and the JSON file was not updated')
        elif len(inserted_season.keys()) == 0 and update_file_result:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection')
        elif len(inserted_season.keys()) > 0 and not update_file_result:
            raise DatabaseError('The JSON file was not updated with the given season')
        return 'The season was successfully inserted'

    def find_number_of_unknown_episodes(self):
        unknown_season = self.find_season('Unknown')
        if unknown_season:
            return len(unknown_season.episodes)
        return 0
    
    def add_episode_to_document(self, guide_show: 'GuideShow') -> bool:
        new_episode = Episode.from_guide_show(guide_show)
        if guide_show.season_number == '':
            season_number = 'Unknown'
            new_episode.episode_number = self.find_number_of_unknown_episodes() + 1
        else:
            season_number = guide_show.season_number
        
        if 'ABC1' in guide_show.channel:
            new_episode.channels.append('ABCHD')
        if '10' in guide_show.channel or 'TEN' in guide_show.channel:
            new_episode.channels.append('TENHD')
        
        self.find_season(season_number).add_episode(new_episode)
        update_file_result = self.update_JSON_file()
        
        inserted_episode: dict = recorded_shows_collection().find_one_and_update(
            {'show': self.title},
            {'$push': {'seasons.$[season].episodes': new_episode.to_dict()}},
            array_filters = [
                {'season.season number': season_number},
            ],
            return_document=ReturnDocument.AFTER
        )

        if len(inserted_episode.keys()) == 0 and not update_file_result:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection and the JSON file was not updated')
        elif len(inserted_episode.keys()) == 0 and update_file_result:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection')
        elif len(inserted_episode.keys()) > 0 and not update_file_result:
            raise DatabaseError('The JSON file was not updated with the given season')
        return 'The episode was successfully inserted'

    def create_JSON_file(self):
        try:
            with open(f'shows/{self.title}.json', 'w+') as fd:
                json.dump(self.to_dict(), fd, indent='\t')
            return True
        except FileExistsError:
            return False

    def update_JSON_file(self):
        try:
            with open(f'shows/{self.title}.json', 'w') as fd:
                json.dump(self.to_dict(), fd, indent='\t')
            return True
        except FileNotFoundError:
            return False
    
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