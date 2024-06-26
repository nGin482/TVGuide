from datetime import datetime
from unittest.mock import patch
from dotenv import load_dotenv
import unittest
import json
import os

from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.models.Reminders import Reminder
from database.models.Users import User
from exceptions.DatabaseError import UserNotFoundError, InvalidSubscriptions


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        load_dotenv('.env.local.test')
        os.environ['PYTHON_ENV'] = 'testing'
        self.database_service = DatabaseService(os.getenv('TVGUIDE_DB'), 'test')

        with open('tests/test_data/recorded_shows.json') as fd:
            self.recorded_shows: list[dict] = json.load(fd)

        with open('tests/test_data/users.json') as fd:
            self.users: list[dict] = json.load(fd)

        for recorded_show in self.recorded_shows:
            self.database_service.insert_recorded_show_document(RecordedShow.from_database(recorded_show))
        self.database_service.users_collection.insert_many([User.from_database(user).to_dict() for user in self.users])
        with open(f'tests/test_data/test_guide_list.json') as fd:
            data: list[dict] = json.load(fd)
        self.guide_list = data
        
    def test_connection(self):
        self.assertEqual(self.database_service.database.name, 'test')

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    def test_capture_db_event_adds_air_date(self, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today

        guide_show_dict = self.guide_list[0]
        guide_show = GuideShow.known_season(
            guide_show_dict['title'],
            (guide_show_dict['channel'], datetime.strptime(guide_show_dict['time'], '%H:%M')),
            (guide_show_dict['season_number'], guide_show_dict['episode_number'], guide_show_dict['episode_title']),
            self.database_service.get_one_recorded_show(guide_show_dict['title'])
        )

        self.database_service.capture_db_event(guide_show)
        
        recorded_show = self.database_service.get_one_recorded_show(guide_show.title)
        episode = recorded_show.find_season(guide_show.season_number).find_episode(episode_number=guide_show.episode_number)

        self.assertIn(datetime(2023, 10, 30), episode.air_dates)
        self.assertIn('has aired today', guide_show.db_event)
        self.assertTrue(episode.is_repeat())

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    def test_capture_db_event_adds_channel(self, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today        

        guide_show = GuideShow.known_season(
            'Doctor Who',
            ('ABC3', datetime(2023, 11, 8, 22, 45)),
            ('4', 2, 'Fires of Pompeii'),
            self.database_service.get_one_recorded_show('Doctor Who')
        )

        self.database_service.capture_db_event(guide_show)

        recorded_show = self.database_service.get_one_recorded_show(guide_show.title)
        episode = recorded_show.find_season(guide_show.season_number).find_episode(episode_number=guide_show.episode_number)

        self.assertIn(datetime(2023, 10, 30), episode.air_dates)
        self.assertIn('added to the channel list', guide_show.db_event)
        self.assertIn('ABC3', episode.channels)
        self.assertTrue(episode.is_repeat())

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    def test_capture_db_event_adds_episode(self, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today        

        guide_show = GuideShow.known_season(
            'Person of Interest',
            ('GEM', datetime(2023, 11, 8, 22, 45)),
            ('1', 2, 'Ghosts'),
            self.database_service.get_one_recorded_show('Person of Interest')
        )
        
        self.database_service.capture_db_event(guide_show)

        recorded_show = self.database_service.get_one_recorded_show(guide_show.title)
        episode = recorded_show.find_season(guide_show.season_number).find_episode(episode_number=guide_show.episode_number)

        self.assertIsNotNone(episode)
        self.assertIn('GEM', episode.channels)
        self.assertIn(datetime(2023, 10, 30), episode.air_dates)
        self.assertFalse(episode.is_repeat())

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    def test_capture_db_event_adds_season(self, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today        

        guide_show = GuideShow.known_season(
            'Endeavour',
            ('ABC1', datetime(2023, 11, 8, 20, 30)),
            ('5', 6, 'Icarus'),
            self.database_service.get_one_recorded_show('Endeavour')
        )
        
        before_season = self.database_service.get_one_recorded_show(guide_show.title).find_season(guide_show.season_number)
        
        self.database_service.capture_db_event(guide_show)

        recorded_show = self.database_service.get_one_recorded_show(guide_show.title)
        after_season = self.database_service.get_one_recorded_show(guide_show.title).find_season(guide_show.season_number)
        episode = recorded_show.find_season(guide_show.season_number).find_episode(episode_number=guide_show.episode_number)

        self.assertIsNone(before_season)
        self.assertIsNotNone(after_season)
        self.assertIsNotNone(episode)
        self.assertIn('ABC1', episode.channels)
        self.assertIn('ABCHD', episode.channels)
        self.assertIn(datetime(2023, 10, 30), episode.air_dates)
        self.assertFalse(episode.is_repeat())

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    def test_capture_db_event_adds_show(self, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today        

        guide_show = GuideShow.known_season(
            'Maigret',
            ('ABC1', datetime(2023, 11, 8, 20, 30)),
            ('1', 1, 'Maigret Sets A Trap'),
            self.database_service.get_one_recorded_show('Maigret')
        )
        
        before_show = self.database_service.get_one_recorded_show(guide_show.title)
        
        self.database_service.capture_db_event(guide_show)

        recorded_show = self.database_service.get_one_recorded_show(guide_show.title)
        after_season = self.database_service.get_one_recorded_show(guide_show.title).find_season(guide_show.season_number)
        episode = recorded_show.find_season(guide_show.season_number).find_episode(episode_number=guide_show.episode_number)

        self.assertIsNone(before_show)
        self.assertIsNotNone(recorded_show)
        self.assertIsNotNone(after_season)
        self.assertIsNotNone(episode)
        self.assertEqual(after_season.season_number, guide_show.season_number)
        self.assertEqual(episode.episode_number, guide_show.episode_number)
        self.assertIn('ABC1', episode.channels)
        self.assertIn('ABCHD', episode.channels)
        self.assertIn(datetime(2023, 10, 30), episode.air_dates)

    
    @unittest.skip
    def test_create_recorded_show_from_db(self):
        recorded_show = RecordedShow.from_database(self.recorded_shows[0])
        self.assertEqual(recorded_show.title, self.recorded_shows[0]['show'])
        self.assertGreater(len(recorded_show.seasons), 0)
        episode_count = 0
        for season in recorded_show.seasons:
            episode_count += len(season.episodes)
        self.assertGreater(episode_count, 0)

    @unittest.skip
    def test_create_recorded_show_from_guide_show(self):
        new_show = GuideShow(
            'Endeavour',
            'ABC1',
            datetime(2022, 8, 26),
            '6',
            1,
            'Pylon',
            None
        )
        recorded_show = RecordedShow.from_guide_show(new_show)
        self.assertEqual(recorded_show.title, new_show.title)
        self.assertIsInstance(recorded_show.seasons[0].season_number, str)
        self.assertEqual(recorded_show.seasons[0].season_number, new_show.season_number)
        self.assertIsInstance(recorded_show.seasons[0].episodes[0].episode_number, int)
        self.assertEqual(recorded_show.seasons[0].episodes[0].episode_number, new_show.episode_number)
        self.assertEqual(recorded_show.seasons[0].episodes[0].episode_title, new_show.episode_title)
        self.assertIn(new_show.channel, recorded_show.seasons[0].episodes[0].channels)
        print(recorded_show)
        self.assertFalse(recorded_show.seasons[0].episodes[0].repeat)

    @unittest.skip
    def test_01_insert_new_show(self):
        new_unforgotten_episode = GuideShow(
            'Unforgotten',
            'SBS',
            datetime(2022, 8, 10, 20, 30),
            '4',
            1,
            'Episode 1',
            None
        )
        original_length = len(self.test_db.get_all_recorded_shows())
        self.test_db.capture_db_event(new_unforgotten_episode)
        new_length = len(self.test_db.get_all_recorded_shows())

        self.assertGreater(new_length, original_length)
    
    @unittest.skip
    def test_02_insert_new_season(self):
        new_show = GuideShow(
            'Unforgotten',
            'ABC1',
            datetime.now(),
            '10',
            1,
            'Test',
            self.test_db.get_one_recorded_show('Unforgotten')
        )
        self.assertIsNotNone(new_show.recorded_show)
        original_length = len(new_show.recorded_show.seasons)
        self.test_db.capture_db_event(new_show)
        new_length = len(new_show.recorded_show.seasons)
        self.assertGreater(new_length, original_length)


    @unittest.skip
    def test_03_insert_new_episode(self):
        new_show = GuideShow(
            'Unforgotten',
            'ABC1',
            datetime.now(),
            '10',
            2,
            'Test-2',
            self.test_db.get_one_recorded_show('Unforgotten')
        )

        self.assertIsNone(new_show.recorded_show)
        original_length = len(new_show.recorded_show.find_season(new_show.season_number).episodes)
        self.test_db.capture_db_event(new_show)
        new_length = len(new_show.recorded_show.find_season(new_show.season_number).episodes)
        self.assertGreater(new_length, original_length)


    @unittest.skip
    def test_create_reminder_from_values(self):
        reminder_dw = Reminder.from_values(self.guide_shows[0], 'Before', 3, 'All')
        print(reminder_dw.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder_dw.show, self.guide_shows[0].title)
        self.assertEqual(reminder_dw.reminder_alert, 'Before')
        self.assertEqual(reminder_dw.warning_time, 3)
        self.assertEqual(reminder_dw.occasions, 'All')
        self.assertEqual(reminder_dw.guide_show, self.guide_shows[0])
        self.reminders.append(reminder_dw)

        reminder_endeavour = Reminder.from_values(self.guide_shows[1], 'Before', 3, 'All')
        print(reminder_endeavour.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder_endeavour.show, self.guide_shows[1].title)
        self.assertEqual(reminder_endeavour.reminder_alert, 'Before')
        self.assertEqual(reminder_endeavour.warning_time, 3)
        self.assertEqual(reminder_endeavour.occasions, 'All')
        self.assertEqual(reminder_endeavour.guide_show, self.guide_shows[1])
        self.reminders.append(reminder_endeavour)

    @unittest.skip
    def test_reminder_needed(self):
        dw_episode = GuideShow('Doctor Who', ('ABC1', datetime.today()), ('6', 7, 'A Good Man Goes To War', True), None)
        endeavour = GuideShow('Endeavour', ('ABC1', datetime.today()), ('5', 6, 'Icarus', True), None)
        guide_list = [dw_episode, endeavour]
        reminders = self.test_db.get_reminders_for_shows(guide_list)
        print(f'Reminders: {reminders}')
        self.assertGreater(len(reminders), 1)
        print(len(reminders))
        self.assertTrue(reminders[0].compare_reminder_interval())
        self.assertTrue(reminders[1].compare_reminder_interval())
        self.assertIsNotNone(reminders[0].guide_show)
        self.assertIsNotNone(reminders[1].guide_show)
        print(reminders[0].notification())
        print(reminders[1].notification())
        # with self.assertRaises(IndexError) as exception_context:
        #     reminders[1].compare_reminder_interval()

    def test_delete_recorded_show_succeeds(self):

        shows_count_before = len(self.database_service.get_all_recorded_shows())

        self.database_service.delete_recorded_show('Test Delete')

        shows_count_after = len(self.database_service.get_all_recorded_shows())

        self.assertEqual(shows_count_after, shows_count_before - 1)

    def test_get_user_returns_user_if_found(self):
        user = self.database_service.get_user('Splintax')
        
        self.assertIsInstance(user, User)
        self.assertEqual('Splintax', user.username)

    def test_get_user_returns_none_if_not_found(self):
        user = self.database_service.get_user('Random')
        self.assertIsNone(user)

    def test_create_user_succeeds(self):
        initial_user_count = self.database_service.users_collection.count_documents({})
        new_user = {
            'username': 'Wallaby',
            'password': 'SOCOM Tactical Strike',
            'show_subscriptions': [
                'Doctor Who',
                'Shetland',
                'Maigret'
            ],
            'reminder_subscriptions': [],
        }
        self.database_service.register_user(
            new_user['username'], new_user['password'], new_user['show_subscriptions'], new_user['reminder_subscriptions']
        )
        new_user_count = self.database_service.users_collection.count_documents({})
        new_user_doc = self.database_service.get_user('Wallaby')

        self.assertEqual(6, initial_user_count)
        self.assertEqual(7, new_user_count)
        self.assertEqual('Wallaby', new_user_doc.username)
        self.assertNotEqual(new_user['password'], new_user_doc.password)
        self.assertEqual('Standard', new_user_doc.role)

    def test_change_user_password_succeeds(self):
        initial_user = self.database_service.get_user('Splintax')

        self.database_service.change_user_password('Splintax', 'changing to a new password')

        post_user = self.database_service.get_user('Splintax')

        self.assertNotEqual(initial_user.password, post_user.password)
        self.assertNotEqual('changing to a new password', post_user.password)

    def test_change_user_password_raises_error(self):
        initial_user = self.database_service.get_user('Random')

        with self.assertRaises(UserNotFoundError) as context:
            self.database_service.change_user_password('Random', 'changing to another password')

        self.assertIsNone(initial_user)
        self.assertIn('Random', str(context.exception))

    def test_add_show_subscriptions(self):
        intial_user = self.database_service.get_user('Splintax')

        self.database_service.update_user_subscriptions('Splintax', 'add', 'searchList', ['Maigret', 'Vera', 'Transformers: Prime', 'Shetland'])

        post_user = self.database_service.get_user('Splintax')

        self.assertEqual(2, len(intial_user.show_subscriptions))
        self.assertEqual(6, len(post_user.show_subscriptions))
        self.assertIn('Transformers: Prime', post_user.show_subscriptions)
        self.assertIn('Shetland', post_user.show_subscriptions)
        
    def test_remove_show_subscriptions(self):
        intial_user = self.database_service.get_user('Crux')

        self.database_service.update_user_subscriptions('Crux', 'remove', 'searchList', ['Transformers: Prime'])

        post_user = self.database_service.get_user('Crux')

        self.assertEqual(2, len(intial_user.show_subscriptions))
        self.assertEqual(1, len(post_user.show_subscriptions))
        self.assertNotIn('Transformers: Prime', post_user.show_subscriptions)
        self.assertIn('Transformers: Cyberverse', post_user.show_subscriptions)

    def test_add_reminder_subscriptions(self):
        intial_user = self.database_service.get_user('Sulejmani')

        self.database_service.update_user_subscriptions('Sulejmani', 'add', 'reminders', ['Transformers: Prime'])

        post_user = self.database_service.get_user('Sulejmani')

        self.assertEqual(0, len(intial_user.reminder_subscriptions))
        self.assertEqual(1, len(post_user.reminder_subscriptions))
        self.assertIn('Transformers: Prime', post_user.reminder_subscriptions)

    def test_remove_reminder_subscriptions(self):
        intial_user = self.database_service.get_user('Jazz')

        self.database_service.update_user_subscriptions('Jazz', 'remove', 'reminders', ['Doctor Who'])

        post_user = self.database_service.get_user('Jazz')

        self.assertEqual(3, len(intial_user.reminder_subscriptions))
        self.assertEqual(2, len(post_user.reminder_subscriptions))
        self.assertNotIn('Doctor Who', post_user.reminder_subscriptions)
        self.assertIn('Endeavour', post_user.reminder_subscriptions)
        self.assertIn('Shetland', post_user.reminder_subscriptions)

    def test_updating_subscriptions_raises_error(self):
        with self.assertRaises(InvalidSubscriptions) as context:
            self.database_service.update_user_subscriptions('Crux', 'add', 'searchList', [])
        self.assertIn('Please provide a list of show subscriptions', str(context.exception))

    def test_promote_user_succeeds(self):
        user_initial = self.database_service.get_user('Splintax')
        self.database_service.promote_user('Splintax')
        promoted_user = self.database_service.get_user('Splintax')

        self.assertEqual('Standard', user_initial.role)
        self.assertEqual('Admin', promoted_user.role)

    def test_promote_user_raises_error(self):

        with self.assertRaises(UserNotFoundError) as context:
            self.database_service.promote_user('Random')
        self.assertIn('Random', str(context.exception))

    def test_delete_user_succeeds(self):
        initial_user_count = self.database_service.users_collection.count_documents({})
        user_initial = self.database_service.get_user('John Smith')

        result = self.database_service.delete_user('John Smith')
        post_user_count = self.database_service.users_collection.count_documents({})
        post_user = self.database_service.get_user('John Smith')

        self.assertEqual(7, initial_user_count)
        self.assertIsNotNone(user_initial)
        self.assertTrue(result)
        self.assertEqual(6, post_user_count)
        self.assertIsNone(post_user)

    def test_delete_user_fails(self):
        initial_user_count = self.database_service.users_collection.count_documents({})
        user_initial = self.database_service.get_user('Random')

        result = self.database_service.delete_user('Random')
        post_user_count = self.database_service.users_collection.count_documents({})
        post_user = self.database_service.get_user('Random')

        self.assertEqual(7, initial_user_count)
        self.assertIsNone(user_initial)
        self.assertFalse(result)
        self.assertEqual(7, post_user_count)
        self.assertIsNone(post_user)
    

    @classmethod
    def tearDownClass(self) -> None:
        self.database_service.recorded_shows_collection.delete_many({})
        self.database_service.users_collection.delete_many({})
        return super().tearDownClass()

    # test:
        # creating RecordedShow
            # RS object
                # with dictionary
                # with GuideShow object
            # RS document in DB
        # creating recorded show
        # inserting season
        # inserting episode
            # make sure the repeat status is false on insert
        # adding channel
        # marking as repeat
        # guideShow_object.capture_db_event()
            # guideShow_object.repeat and channel updating during capture_db_event()
