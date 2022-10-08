from pymongo.database import Database
from pymongo.errors import OperationFailure
from pymongo import ReturnDocument
from datetime import datetime
import json
import os

from log import log_guide_db_service
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow, Season, Episode
from database.models.Reminders import Reminder
from exceptions.DatabaseError import DatabaseError, EpisodeNotFoundError, ReminderNotFoundError, SearchItemAlreadyExistsError, SearchItemNotFoundError, SeasonNotFoundError, ShowNotFoundError

class DatabaseService:


    def __init__(self, database: Database) -> None:
        self.database = database
        self.recorded_shows_collection = self.database.get_collection('RecordedShows')
        self.reminders_collection = self.database.get_collection('Reminders')
        self.search_list_collection = self.database.get_collection('ShowList')
    
# RECORDED SHOWS
    def get_all_recorded_shows(self):
        documents = list(self.recorded_shows_collection.find({}))
        return [RecordedShow.from_database(dict(document)) for document in documents]

    def get_one_recorded_show(self, show_title: str):
        search = self.recorded_shows_collection.find_one({'show': show_title})
        return RecordedShow.from_database(search)

    def insert_recorded_show_document(self, recorded_show: RecordedShow):
        insert_result = self.recorded_shows_collection.insert_one(recorded_show.to_dict())
        if not insert_result.inserted_id:
            raise DatabaseError('The show was not able to be recorded.')
        else:
            return 'The show is now being recorded.'

    def add_new_season(self, recorded_show: RecordedShow, season: Season):
        """
        Appends the given `Season` object to the list of seasons. Also inserts the `Season` document into the MongoDB collection.\n
        Raises an `exceptions.DatabaseError` if inserting the document fails.
        """
        recorded_show.seasons.append(season)

        inserted_season: dict = self.recorded_shows_collection.find_one_and_update(
            {'show': recorded_show.title},
            {'$push': {'seasons': season.to_dict()}},
            return_document=ReturnDocument.AFTER
        )

        if len(inserted_season.keys()) == 0:
            raise DatabaseError('The season was not inserted into the `RecordedShows` collection')
        return 'The season was successfully inserted'

    def add_new_episode_to_season(self, recorded_show: RecordedShow, season_number: str, episode: Episode):
        """Add the new given `Episode` to the document's collection"""
        season = recorded_show.find_season(season_number)
        season.episodes.append(episode)
        
        self.recorded_shows_collection.find_one_and_update(
            {'show': recorded_show.title},
            {'$push': {'seasons.$[season].episodes': episode.to_dict()}},
            array_filters=[
                {'season.season_number': season_number}
            ],
            return_document=ReturnDocument.AFTER
        )

    def update_episode_in_database(self, show_title: str, season_number: str, episode: Episode):
        """Update the given `Episode` in the database.\n
        Provide the `show_title` and the `season_number` that this episode belongs to.\n
        Raises `DatabaseError` if there is a problem updating the episode"""
        try:
            self.recorded_shows_collection.find_one_and_update(
            {'show': show_title},
            {'$set': {'seasons.$[season].episodes.$[episode]': episode.to_dict()}},
            array_filters = [
                {'season.season_number': season_number},
                {'episode.episode_number': episode.episode_number}
            ],
            return_document = ReturnDocument.AFTER
        )
        except OperationFailure as err:
            raise DatabaseError(f"An error occurred when trying to update this episode of {show_title}. Error: {str(err)}")
        return True

    def remove_episode_from_season(self, show_title: str, season_number: str, episode_number: int):
        """Remove an episode from the given show's specified season.\n
        Provide the `show_title`, `season_number` and the `episode_number`"""

        self.recorded_shows_collection.find_one_and_update(
            {'show': show_title},
            {'$pull': {'seasons.$[season].episodes': {'episode_number': episode_number}}},
            array_filters = [
                {'season.season_number': season_number}
            ],
            return_document=ReturnDocument.AFTER
        )

    def backup_recorded_shows(self):
        """
        Create a local backup of the `RecordedShows` collection by storing data locally in JSON files
        """
        
        for recorded_show in self.get_all_recorded_shows():
            if os.path.isdir('database/backups/recorded_shows'):
                with open(f'database/backups/recorded_shows/{recorded_show.title}.json', 'w+') as fd:
                    json.dump(recorded_show.to_dict(), fd, indent='\t')
            else:
                os.mkdir('database/backups/recorded_shows')
                with open(f'database/backups/recorded_shows/{recorded_show.title}.json', 'w+') as fd:
                    json.dump(recorded_show.to_dict(), fd, indent='\t')

    def rollback_recorded_shows(self):
        """
        Rollback the `RecordedShows` collection to a point before the TVGuide has interacted with the DB for the current day
        """
        
        for recorded_show_file_name in os.listdir('database/backups/recorded_shows'):
            print(recorded_show_file_name)
            with open(f'database/backups/recorded_shows/{recorded_show_file_name}') as fd:
                show_data = json.load(fd)
            show_name: str = show_data['show']
            self.recorded_shows_collection.find_one_and_update(
                {'show': show_name},
                {'$set': {'seasons': show_data['seasons']}},
                return_document=ReturnDocument.AFTER
            )
            # how to notify that this is done
        pass


    def capture_db_event(self, guide_show: GuideShow):
        recorded_show = guide_show.recorded_show
        
        try:
            episode = guide_show.find_recorded_episode()
            set_repeat = 'Repeat status is up to date'
            channel_add = 'Channel list is up to date'
            episode.channels = list(set(episode.channels))
            if not episode.channel_check(guide_show.channel):
                channel_add = episode.add_channel(guide_show.channel)
            if not episode.repeat:
                episode.repeat = True
                set_repeat = 'The episode has been marked as a repeat.'
            episode.latest_air_date = datetime.today()
            print(f'{guide_show.title} happening on channel/repeat')
            self.update_episode_in_database(guide_show.title, guide_show.season_number, episode)
            event = {'show': guide_show.to_dict(), 'repeat': set_repeat, 'channel': channel_add}
        except EpisodeNotFoundError as err:
            try:
                new_episode = Episode.from_guide_show(guide_show)
                self.add_new_episode_to_season(recorded_show, guide_show.season_number, new_episode)
                add_episode_status = f'{new_episode} has been added to Season {guide_show.season_number}'
            except DatabaseError as err:
                add_episode_status = str(err)
            print(f'{guide_show.title} happening on episode')
            event = {'show': guide_show.to_dict(), 'result': add_episode_status}
        except SeasonNotFoundError as err:
            new_season = Season.from_guide_show(guide_show)
            try:
                insert_season = self.add_new_season(new_season)
            except DatabaseError as err:
                insert_season = str(err)
            print(f'{guide_show.title} happening on season')
            event = {'show': guide_show.to_dict(), 'result': insert_season}
        except ShowNotFoundError as err:
            recorded_show = RecordedShow.from_guide_show(guide_show)
            try:
                insert_show = self.insert_recorded_show_document(recorded_show)
            except DatabaseError as err:
                insert_show = str(err)
            print(f'{guide_show.title} happening on show')
            event = {'show': guide_show.to_dict(), 'result': insert_show}
        except Exception as err:
            event = {'show': guide_show.to_dict(), 'message': 'Unable to process this episode.', 'error': str(err)}

        log_guide_db_service(event)
        return event

# SEARCH LIST
    def get_search_list(self):
        "Get the list of shows being searched for."
        documents: list[dict] = list(self.search_list_collection.find({}))
        return [document['show'] for document in documents]

    def insert_into_showlist_collection(self, show: str):
        """Insert the given `show` into the SearchList collection.\n
        Raises `SearchItemAlreadyExistsError` if the given show already exists in the collection,
        or `DatabaseError` if there is a problem adding the show."""
        show_exists = self.search_list_collection.find_one({'show': show})
        if show_exists:
            raise SearchItemAlreadyExistsError(f'The show {show} is already being searched for')
        else:
            try:
                self.search_list_collection.insert_one({"show": show})
                return True
            except OperationFailure as err:
                raise DatabaseError(f'There was a problem adding {show} to the search list. Error: {str(err)}')

    def remove_show_from_list(self, show_to_remove: str):
        """Remove the given show from the SearchList collection.\n
        Raises `SearchItemNotFoundError` if the given show can't be found in the collection,
        or `DatabaseError` if there is a problem removing the show."""
        show_exists = self.search_list_collection.find_one({'show': show_to_remove})
        if show_exists:
            raise SearchItemNotFoundError(f'The show {show_to_remove} is already being searched for')
        try:
            self.search_list_collection.delete_one({'show': show_to_remove})
            return True
        except OperationFailure as err:
            raise DatabaseError(f'There was a problem removing {show_to_remove} from the show list. Error: {str(err)}')

# REMINDERS
    def get_all_reminders(self):
        "Get all reminders set"
        reminders = list(self.reminders_collection.find({}))
        return [Reminder.from_database(reminder) for reminder in reminders]

    def get_one_reminder(self, show_title: str):
        """Get the reminder set for the show specified by `show_title`.\n
        Raises `ReminderNotFoundError` if a remidner for the show does not exist"""
        reminder = self.reminders_collection.find_one({'show': show_title})
        if reminder is None:
            raise ReminderNotFoundError(f'A reminder has not been set for {show_title}')
        return Reminder.from_database(reminder)

    def get_reminders_for_shows(self, guide_list: list['GuideShow']):
        """
        """
        all_reminders = self.get_all_reminders()
        guide_reminders: list[Reminder] = []
        for show in guide_list:
            for reminder in all_reminders:
                if reminder.show == show.title:
                    reminder.guide_show = show
                    guide_reminders.append(reminder)

        return guide_reminders

    def insert_new_reminder(self, reminder: Reminder):
        """
        Insert the given `Reminder` object into the collection.\n
        Raises `DatabaseError` if the reminder was not inserted.
        """
        inserted_document = self.reminders_collection.insert_one(reminder.to_dict())
        if not inserted_document.inserted_id:
            raise DatabaseError(f'The Reminder document for {reminder.show} was not inserted into the Reminders collection')
        return True


