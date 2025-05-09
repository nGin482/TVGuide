from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from pymongo.errors import OperationFailure
from pymongo import ReturnDocument, DESCENDING
from datetime import datetime
import json
import os

from data_validation.validation import Validation
from database.models.Guide import Guide
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow, Season, Episode
from database.models.Reminders import Reminder
from database.models.SearchItem import SearchItem
from database.models.Users import User
from database.mongo import mongo_client
from exceptions.DatabaseError import (
    DatabaseError,
    EpisodeNotFoundError,
    ReminderNotFoundError,
    SearchItemAlreadyExistsError,
    SearchItemNotFoundError,
    SeasonNotFoundError,
    ShowNotFoundError,
    UserNotFoundError,
    InvalidSubscriptions
)

class DatabaseService:

    def __init__(self, database_conn: str, database: str) -> None:
        self._mongo_connection = mongo_client(database_conn)
        self.database = self._mongo_connection.get_database(database)
        self.recorded_shows_collection = self.database.get_collection('RecordedShows')
        self.reminders_collection = self.database.get_collection('Reminders')
        self.search_list_collection = self.database.get_collection('ShowList')
        self.guide_collection = self.database.get_collection('Guide')
        self.users_collection = self.database.get_collection('Users')
        self.jobs_collection = self.database.get_collection('Jobs')
        self.source_data_collection = self.database.get_collection('SourceData')
    
# RECORDED SHOWS
    def get_all_recorded_shows(self):
        documents = list(self.recorded_shows_collection.find({}))
        return [RecordedShow.from_database(dict(document)) for document in documents if document['show'] != "Transformers: Bumblebee Cyberverse Adventures"]

    def get_one_recorded_show(self, show_title: str):
        search = self.recorded_shows_collection.find_one({'show': show_title})
        if search is None:
            return None
        return RecordedShow.from_database(dict(search))

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
            update_result = self.recorded_shows_collection.update_one(
                {'show': show_title},
                {'$set': {'seasons.$[season].episodes.$[episode]': episode.to_dict()}},
                array_filters = [
                    {'season.season_number': season_number},
                    {'episode.episode_number': episode.episode_number}
                ]
            )
            if update_result.matched_count != update_result.modified_count:
                from services.hermes.hermes import hermes
                hermes.dispatch('episode_not_updated', show_title, season_number, episode.episode_number, episode.episode_title)
        except OperationFailure as err:
            raise DatabaseError(f"An error occurred when trying to update this episode of {show_title}. Error: {str(err)}")

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

    def delete_recorded_show(self, show: str):
        """
        Remove the given `show` from the RecordedShow collection
        """
        self.recorded_shows_collection.find_one_and_delete(
            {'show': show}
        )

    def backup_recorded_shows(self):
        """
        Create a local backup of the `RecordedShows` collection by storing data locally in JSON files
        """
        
        if not os.path.isdir('database/backups/recorded_shows'):
            os.mkdir('database/backups/recorded_shows')
        
        for recorded_show in self.get_all_recorded_shows():
            recorded_show_title = recorded_show.title.replace(':', '') if ':' in recorded_show.title else recorded_show.title
            with open(f'database/backups/recorded_shows/{recorded_show_title}.json', 'w+') as fd:
                json.dump(recorded_show.to_dict(), fd, indent='\t')

    def rollback_recorded_shows(self, directory: str = 'backups'):
        """
        Rollback the `RecordedShows` collection to a point before the TVGuide has interacted with the DB for the current day
        """
        from services.hermes.hermes import hermes
        
        for recorded_show_file_name in os.listdir(f'database/{directory}/recorded_shows'):
            recorded_show_title = recorded_show_file_name.replace(':', '') if ':' in recorded_show_file_name else recorded_show_file_name
            if '.zip' not in recorded_show_file_name:
                print(recorded_show_title)
                with open(f'database/{directory}/recorded_shows/{recorded_show_title}') as fd:
                    show_data = dict(json.load(fd))
                show_name: str = show_data['show']
                self.recorded_shows_collection.find_one_and_update(
                    {'show': show_name},
                    {'$set': {'seasons': show_data['seasons']}},
                    return_document=ReturnDocument.AFTER
                )
        
        hermes.dispatch('db_rollback')


    def capture_db_event(self, guide_show: GuideShow, date: str = None):
        
        recorded_show = guide_show.recorded_show
        event_date = datetime.strptime(date, '%d/%m/%Y') if date is not None else Validation.get_current_date().date()
        
        try:
            episode = guide_show.find_recorded_episode()
            print(f'{guide_show.title} happening on channel/repeat')
            episode.air_dates.append(event_date)
            episode.channels = list(set(episode.channels))
            result = f"{guide_show.title} has aired today"
            if episode.channel_check(guide_show.channel) is False:
                result = episode.add_channel(guide_show.channel)
            self.update_episode_in_database(guide_show.title, guide_show.season_number, episode)
            guide_show.db_event = result
        except EpisodeNotFoundError as err:
            try:
                new_episode = Episode.from_guide_show(guide_show)
                self.add_new_episode_to_season(recorded_show, guide_show.season_number, new_episode)
                add_episode_status = f'Episode {new_episode.episode_number} {new_episode.episode_title} has been added to Season {guide_show.season_number}'
            except DatabaseError as err:
                add_episode_status = str(err)
            print(f'{guide_show.title} happening on episode')
            guide_show.db_event = add_episode_status
        except SeasonNotFoundError as err:
            new_season = Season.from_guide_show(guide_show)
            try:
                insert_season = self.add_new_season(recorded_show, new_season)
            except DatabaseError as err:
                insert_season = str(err)
            print(f'{guide_show.title} happening on season')
            guide_show.db_event = insert_season
        except ShowNotFoundError as err:
            recorded_show = RecordedShow.from_guide_show(guide_show)
            try:
                insert_show = self.insert_recorded_show_document(recorded_show)
            except DatabaseError as err:
                insert_show = str(err)
            print(f'{guide_show.title} happening on show')
            guide_show.db_event = insert_show
        except Exception as err:
            from services.hermes.hermes import hermes
            hermes.dispatch('show_not_processed', guide_show.message_string(), err)

# SEARCH LIST
    def get_search_list(self):
        "Get the list of shows being searched for."
        documents: list[dict] = list(self.search_list_collection.find({}))
        return [SearchItem.from_database(document) for document in documents]
    
    def add_search_item(self, search_item: SearchItem):
        show_exists = self.search_list_collection.find_one({ 'show': search_item.show })
        if show_exists:
            raise SearchItemAlreadyExistsError(f'The show {search_item.show} is already being searched for')
        try:
            self.search_list_collection.insert_one(search_item.to_dict())
        except OperationFailure as err:
            raise DatabaseError(f'There was a problem adding {search_item.show} to the search list. Error: {str(err)}')

    def remove_show_from_list(self, show_to_remove: str):
        """Remove the given show from the SearchList collection.\n
        Raises `SearchItemNotFoundError` if the given show can't be found in the collection,
        or `DatabaseError` if there is a problem removing the show."""
        show_exists = self.search_list_collection.find_one({'show': show_to_remove})
        if not show_exists:
            raise SearchItemNotFoundError(f'The show {show_to_remove} could not be found in the SearchList.')
        try:
            self.search_list_collection.delete_one({'show': show_to_remove})
            return True
        except OperationFailure as err:
            raise DatabaseError(f'There was a problem removing {show_to_remove} from the Search List. Error: {str(err)}')

# REMINDERS
    def get_all_reminders(self):
        "Get all reminders set"
        reminders = list(self.reminders_collection.find({}))
        return [Reminder.from_database(reminder) for reminder in reminders]

    def get_one_reminder(self, show_title: str):
        """Get the reminder set for the show specified by `show_title`.\n
        Returns `None` if a reminder for the show does not exist"""
        reminder = self.reminders_collection.find_one({'show': show_title})
        if reminder is None:
            return None
        return Reminder.from_database(reminder)

    def get_reminders_for_shows(self, guide_list: list['GuideShow']):
        """
        Given a list of `GuideShow` objects, filter the list of `Reminders` based on whether there is a match.\n
        If there is a match, assign the `GuideShow` to the reminder.
        """
        all_reminders = self.get_all_reminders()
        guide_reminders: list[Reminder] = []
        for show in guide_list:
            for reminder in all_reminders:
                if reminder.show == show.title and 'HD' not in show.channel:
                    reminder.guide_show = show
                    reminder.notify_time = reminder.calculate_notification_time()
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

    def update_reminder(self, reminder: Reminder):
        updated_reminder = self.reminders_collection.find_one_and_replace(
            {'show': reminder.show},
            reminder.to_dict()
        )
        if updated_reminder is None:
            raise ReminderNotFoundError(f'The reminder for {reminder.show} could not be found')
        return True
    
    def delete_reminder(self, show: str):
        """Delete a `Reminder` from the MongoDB collection.\n
        Raises an `exceptions.ReminderNotFoundError` if the reminder document could not be found."""
        reminder_deleted: dict = self.reminders_collection.find_one_and_delete(
            {'show': show}
        )
        if reminder_deleted is None:
            raise ReminderNotFoundError(f'The reminder for {show} could not be found')
        return True

# GUIDE
    def get_all_guides(self):
        guides = self.guide_collection.find({})
        return list(Guide.from_database(guide, self) for guide in guides)

    def get_guide_date(self, date: str):
        """Get the Guide data for the date provided. Date should be provided in the format `dd/mm/YYYY`"""
        guide_date = self.guide_collection.find_one({'date': date})
        if guide_date is None:
            return None
        return Guide.from_database(dict(guide_date), self)

    def get_guide_month(self, month: str):
        """
        Search for all Guide data recorded in the provided month.\n
        Supports the month as a zero-padded decimal number, the month's full name (January) and the abbreviated name (Jan)"""
        if not month.isnumeric():
            if len(month) == 3:
                month = str(datetime.strptime(month, '%b').month)
            else:
                month = str(datetime.strptime(month, '%B').month)
        guide_search = self.guide_collection.find({'date': f"/{month}/"})
        return [Guide.from_database(dict(document)) for document in guide_search]
    
    def get_latest_guide(self):
        """Return the latest `Guide` record from the collection"""
        guide_results = list(self.guide_collection.find({}).sort('_id', DESCENDING).limit(1))
        if len(guide_results) > 0:
            latest_guide = dict(guide_results[0])
            return Guide.from_database(latest_guide, self)
        return None

    def search_guides_for_show(self, show_title: str):
        """Search all guide data for when the given show_title has been aired"""
        guides = [Guide.from_database(details) for details in self.get_all_guides()]
        return [{'date': guide.date, 'show': show} for guide in guides for show in guide.search_for_show(show_title)]

    def add_guide_data(self, new_guide: Guide):
        """Add the Guide data to the database.\n
        Raises `exceptions.DatabaseError` if the Guide data for the current day already exists or 
        was not able to be inserted."""

        check_guide_exists = self.get_guide_date(new_guide.date)
        if check_guide_exists is not None:
            raise DatabaseError(f"A Guide for today's date ({new_guide.date}) already exists")
        guide_inserted = self.guide_collection.insert_one(new_guide.to_dict())
        if not guide_inserted.inserted_id:
            raise DatabaseError(f"The Guide was not able to be inserted")

    def remove_guide_data(self, date: str):
        """Remove the Guide data for the given date from the database.\n
        Raises `exceptions.DatabaseError` if the given date could not be found."""

        delete_result = self.guide_collection.find_one_and_delete({
            'date': date
        })
        if delete_result is None:
            raise DatabaseError(f"The Guide data for {date} could not be found")
        
    def revert_guide(self):
        "Forget sending a message and rollback the database to its previous state"
        self.rollback_recorded_shows()
        self.remove_guide_data(Validation.get_current_date().strftime('%d/%m/%Y'))
        
    # Users
    def get_all_users(self):
        users = self.users_collection.find({})
        return [User.from_database(user) for user in users]

    def get_user(self, username: str):
        user_document = self.users_collection.find_one({'username': username})
        if user_document:
            return User.from_database(user_document)
        return None
    
    def register_user(self, username: str, password: str, shows: list[str], reminders: list[str]):
        new_user = User.register_new_user(username, password, shows, reminders)

        self.users_collection.insert_one(new_user.to_dict())
    
    def update_user_subscriptions(self, username: str, operation: str, resource: str, subscriptions: list[str]):
        user = self.get_user(username)
        if resource == 'searchList':
            if operation == 'add':
                user.subscribe_to_shows(subscriptions)
            if operation == 'remove':
                user.remove_show_subscriptions(subscriptions)
        elif resource == 'reminders':
            if operation == 'add':
                user.subscribe_to_reminders(subscriptions)
            if operation == 'remove':
                user.remove_reminder_subscriptions(subscriptions)
        else:
            raise InvalidSubscriptions('Subscriptions can only be updated for search items and reminders')

        updated_user = self.users_collection.find_one_and_update(
            { 'username': username },
            { '$set':
                {
                    'show_subscriptions': sorted(user.show_subscriptions),
                    'reminder_subscriptions': sorted(user.reminder_subscriptions)
                }
            },
            projection = { '_id': False },
            return_document = ReturnDocument.AFTER
        )
        return updated_user
        
    def promote_user(self, username: str):
        user = self.get_user(username)
        if user:
            updated_user = self.users_collection.find_one_and_update(
                { 'username': username },
                { '$set': { 'role': 'Admin' } },
                { '_id': False, 'password': False },
                return_document=ReturnDocument.AFTER
            )
            return updated_user
        else:
            raise UserNotFoundError(f'No user can be found with the username {username}')
        
    def change_user_password(self, username: str, new_password: str):
        user = self.get_user(username)
        if user:
            user.change_password(new_password)
            updated_user = self.users_collection.find_one_and_update(
                { 'username': username },
                { '$set': { 'password': user.password } },
                { '_id': False, 'password': False },
                return_document=ReturnDocument.AFTER
            )
            return updated_user
        else:
            raise UserNotFoundError(f'No user can be found with the username {username}')

    def delete_user(self, username: str):
        user = self.get_user(username)
        if user:
            self.users_collection.find_one_and_delete({'username': username})
            return True
        return False
    
    # JOBS
    def get_all_jobs(self, scheduler: AsyncIOScheduler):
        job_documents = self.jobs_collection.find({})
        jobs_list: list[Job] = [scheduler.get_job(job['job_id']) for job in job_documents]
        return jobs_list
    
    def get_one_job(self, job_id: str, scheduler: AsyncIOScheduler):
        job_doc = self.jobs_collection.find_one({ 'job_id': job_id })
        if job_doc:
            job: Job = scheduler.get_job(job_doc['job_id'])
            return job
        return None

    def remove_job(self, job_id: str, scheduler: AsyncIOScheduler):
        job_doc = self.jobs_collection.find_one({ 'job_id': job_id })
        if job_doc:
            scheduler.remove_job(job_doc['job_id'])

    # Source Data - Development Environment
    def get_source_data(self, service: str = 'All'):
        source_data = self.source_data_collection.find_one({ 'service': service })
        return dict(source_data)
    
    def import_data(self, resource: str):
        match resource:
            case 'recorded_shows':
                self.import_recorded_shows()
            case 'source_data':
                self.import_source_data()
            case 'search_list':
                self.import_search_list()
            case 'users':
                self.import_users()
            case 'all':
                self.import_recorded_shows()
                self.import_source_data()
                self.import_search_list()
                self.import_users()

    def import_recorded_shows(self):
        self.recorded_shows_collection.delete_many({})

        with open('dev-data/recorded_shows.json') as fd:
            recorded_shows = list(json.load(fd))

        recorded_show_result = self.recorded_shows_collection.insert_many(recorded_shows)
        print(len(recorded_show_result.inserted_ids), 'documents added to the Recorded Shows collection')

    def import_source_data(self):
        self.source_data_collection.delete_many({})

        with open('dev-data/fta_source_data.json') as fd:
            fta_data = list(json.load(fd))
        with open('dev-data/bbc_first_source_data.json') as fd:
            bbc_first_data = list(json.load(fd))
        with open('dev-data/bbc_uktv_source_data.json') as fd:
            bbc_uktv_data = list(json.load(fd))

        fta_result = self.source_data_collection.insert_one({
            'service': "FTA",
            'schedule': fta_data
        })
        bbc_first_result = self.source_data_collection.insert_one({
            'service': "BBC First",
            'schedule': bbc_first_data
        })
        bbc_uktv_result = self.source_data_collection.insert_one({
            'service': "BBC UKTV",
            'schedule': bbc_uktv_data
        })
        print(fta_result.inserted_id, 'added to SourceData collection')
        print(bbc_first_result.inserted_id, 'added to SourceData collection')
        print(bbc_uktv_result.inserted_id, 'added to SourceData collection')

    def import_search_list(self):
        self.search_list_collection.delete_many({})

        with open('dev-data/search_list.json') as fd:
            search_list = json.load(fd)
        
        result = self.search_list_collection.insert_many(search_list)
        print(len(result.inserted_ids), 'documents inserted in the Search List collection')

    def import_users(self):
        self.users_collection.delete_many({})

        with open('dev-data/users.json') as fd:
            raw_users = list(json.load(fd))
            users = [User.register_new_user(
                user['username'],
                user['password'],
                user['show_subscriptions'],
                user['reminder_subscriptions']
            ) for user in raw_users]
        
        users_result = self.users_collection.insert_many([user.to_dict() for user in users])
        print(users_result.inserted_ids, 'added to the Users collection')

    def tear_down_data(self):
        self.source_data_collection.delete_many({})
        self.search_list_collection.delete_many({})
        self.recorded_shows_collection.delete_many({})

    def __repr__(self) -> str:
        return f'DatabaseService [Client: {self.database.client} | Database: {self.database}]'