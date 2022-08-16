from __future__ import annotations
from datetime import datetime
from pymongo import ReturnDocument
from exceptions.DatabaseError import DatabaseError
from ..recorded_shows_collection import recorded_shows_collection
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .GuideShow import GuideShow

class Episode:
    episode_number: int
    episode_title: str
    channels: list[str]
    first_air_date: datetime
    latest_air_date: datetime
    repeat: bool

    def __init__(self, episode_subdocument: dict = {}, show: 'GuideShow' = None) -> None:
        if (len(episode_subdocument.keys()) != 0 or episode_subdocument) and show is None:
            if 'episode number' in episode_subdocument.keys():
                episode_number = episode_subdocument['episode number']
            else:
                episode_number = episode_subdocument['episode_number']
            if 'episode number' in episode_subdocument.keys():
                episode_title = episode_subdocument['episode title']
            else:
                episode_title = episode_subdocument['episode_title']
            if 'first air date' in episode_subdocument.keys():
                first_air_date = episode_subdocument['first air date']
            else:
                first_air_date = episode_subdocument['first_air_date']
            if 'latest air date' in episode_subdocument.keys():
                latest_air_date = episode_subdocument['latest air date']
            elif 'latest_air_date' in episode_subdocument.keys():
                latest_air_date = episode_subdocument['latest_air_date']
            else:
                latest_air_date = datetime.today().strftime('%d/%M/%Y')
            
            
            self.episode_number = episode_number
            self.episode_title = episode_title
            self.channels = episode_subdocument['channels']
            self.first_air_date = first_air_date
            self.latest_air_date = latest_air_date
            self.repeat = episode_subdocument['repeat']
        elif len(episode_subdocument.keys()) == 0 and show is not None:
            self.episode_number = show.episode_number
            self.episode_title = show.episode_title
            self.channels = [show.channel]
            self.first_air_date = datetime.today().strftime('%d/%M/%Y')
            self.latest_air_date = datetime.today().strftime('%d/%M/%Y')
            self.repeat = show.repeat
        else:
            raise ValueError('Please provide details about the episode recorded')

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

        # update_file_result = self.update_JSON_file(guide_show.title, season_number, 'repeat', True)

        # if len(updated_show.keys()) == 0 and not update_file_result:
            # raise DatabaseError('The season was not inserted into the `RecordedShows` collection and the JSON file was not updated')
        # elif len(updated_show.keys()) == 0 and update_file_result:
        if len(updated_show.keys()) == 0:
            raise DatabaseError('The episode in the `RecordedShows` collection was not updated')
        # elif len(updated_show.keys()) > 0:
        #     raise DatabaseError('The episode was not marked as a repeat in the JSON file')
        return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': self.to_dict()}
    
    def update_latest_air_date(self):
        self.latest_air_date = datetime.today().strftime('%d/%M/%Y')

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
        return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': self.to_dict()}

    # def update_JSON_file(self, show_title: str, season_number: str, field: str, new_data):
    #     if field == '' and (new_data == '' or new_data is None or len(new_data) == 0):
    #         raise ValueError('Please provide new information to update the file with')
        
    #     try:
    #         with open(f'shows/{show_title}.json') as fd:
    #             file_data: dict = json.load(fd)
    #         seasons: list[dict] = file_data['seasons']
    #         updated_season: dict = list(filter(lambda season: season['season number'] == season_number, seasons))[0]
    #         updated_episode: dict = list(filter(lambda episode: episode['episode number'] == self.episode_number, updated_season['episodes']))[0]
    #         if len(updated_episode.keys) == 0:
    #             updated_episode: dict = list(filter(lambda episode: episode['episode title'] == self.episode_title, updated_season['episodes']))[0]
    #         updated_episode[field] = new_data

    #         with open(f'shows/{show_title}.json', 'w') as fd:
    #             file_data: dict = json.dump({'show': file_data['show'], 'seasons': seasons}, fd)
    #         return True
    #     except FileNotFoundError:
    #         return False
    
    def to_dict(self):
        if type(self.first_air_date) is not str:
            first_air_date = self.first_air_date.strftime('%d/%M/%Y')
        else:
            first_air_date = self.first_air_date
        if type(self.latest_air_date) is not str:
            latest_air_date = self.latest_air_date.strftime('%d/%M/%Y')
        else:
            latest_air_date = self.latest_air_date
        
        return {
            'episode number': self.episode_number,
            'episode title': self.episode_title,
            'channels': self.channels,
            'first_air_date': first_air_date,
            'latest_air_date': latest_air_date,
            'repeat': self.repeat
        }


class Season:
    season_number: int
    episodes: list[Episode]

    def __init__(self, season_subdocument: dict = {}, show: 'GuideShow' = None) -> None:
        if len(season_subdocument.keys()) != 0 and show is None:
            self.season_number = season_subdocument['season number']
            self.episodes = [Episode(episode_subdocument=episode) for episode in season_subdocument['episodes']]
        elif len(season_subdocument.keys()) == 0 and show is not None:
            self.season_number = show.season_number
            self.episodes = [Episode(show=show)]
        else:
            raise ValueError('Please provide information about the season')

    def find_episode(self, episode_number: int, episode_title: str) -> Episode:
        if episode_number != 0:
            results = list(filter(lambda episode_obj: episode_obj.episode_number == str(episode_number), self.episodes))
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
        episode: Episode
        for episode in self.episodes:
            season_dict['episodes'].append(episode.to_dict())
        
        return season_dict




class RecordedShow:
    title: str
    seasons: list[Season]

    def __init__(self, recorded_show_details: dict = {}, guide_show: 'GuideShow' = None) -> None:
        # self._id = recorded_show_details['_id']
        if guide_show is None and len(recorded_show_details.keys()) != 0:
            self.title = recorded_show_details['show']
            self.seasons = [Season(season) for season in recorded_show_details['seasons']]
        elif guide_show and len(recorded_show_details.keys()) == 0:
            self.title = guide_show.title
            self.seasons = [Season(show=guide_show)]
        else:
            raise ValueError('Please provide details about the show recorded')

    @staticmethod
    def get_all_recorded_shows():
        try:
            return [recorded_show for recorded_show in recorded_shows_collection().find()]
        except AttributeError:
            return []
    
    def find_season(self, season_number) -> Season:
        results = list(filter(lambda season_obj: season_obj.season_number == season_number, self.seasons))
        if len(results) > 0:
            return results[0]
        return None

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

    def add_episode_to_document(self, guide_show: 'GuideShow') -> bool:
        new_episode = Episode(show=guide_show)
        season_number = 'Unknown' if guide_show.season_number == '' else guide_show.season_number
        self.find_season(season_number).add_episode(new_episode)
        update_file_result = self.update_JSON_file()
        
        inserted_episode = recorded_shows_collection().find_one_and_update(
            {'show': self.title, 'seasons.season number': season_number},
            {'$push': {'seasons.$.episodes': new_episode.to_dict()}},
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