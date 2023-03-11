from datetime import datetime
from pymongo import MongoClient
import unittest
import json
import os

from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.models.Reminders import Reminder


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = MongoClient(os.getenv('TVGUIDE_DB'))
        self.prod_db = self.client.get_database('tvguide')
        self.test_db = DatabaseService(self.client.get_database('test'))
        self.recorded_shows_collection = self.test_db.recorded_shows_collection

        with open('tests/test_data/recorded_shows.json') as fd:
            self.recorded_shows: list[dict] = json.load(fd)
        with open(f"today_guide/{os.listdir('today_guide')[0]}") as fd:
            today_shows = json.load(fd)
        with open(f'tests/test_data/test_guide_list.json') as fd:
            data: list[dict] = json.load(fd)
        data.extend(today_shows['FTA'])
        self.guide_list = data
        
    def test_connection(self):
        self.assertEqual(self.test_db.database.name, 'test')

    # @unittest.skip
    def test_create_recorded_show_from_db(self):
        recorded_show = RecordedShow.from_database(self.recorded_shows[0])
        self.assertEqual(recorded_show.title, self.recorded_shows[0]['show'])
        self.assertGreater(len(recorded_show.seasons), 0)
        episode_count = 0
        for season in recorded_show.seasons:
            episode_count += len(season.episodes)
        self.assertGreater(episode_count, 0)

    # @unittest.skip
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

    # @unittest.skip
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
    
    # @unittest.skip
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


    # @unittest.skip
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


    # @unittest.skip
    def test_create_reminder_from_values(self):
        reminder_dw = Reminder.from_values(self.guide_shows[0], 'Before', 3, 'All')
        print(reminder_dw.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder_dw.show, self.guide_shows[0].title)
        self.assertEqual(reminder_dw.reminder_alert, 'Before')
        self.assertEqual(reminder_dw.warning_time, 3)
        self.assertEqual(reminder_dw.occassions, 'All')
        self.assertEqual(reminder_dw.guide_show, self.guide_shows[0])
        self.reminders.append(reminder_dw)

        reminder_endeavour = Reminder.from_values(self.guide_shows[1], 'Before', 3, 'All')
        print(reminder_endeavour.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder_endeavour.show, self.guide_shows[1].title)
        self.assertEqual(reminder_endeavour.reminder_alert, 'Before')
        self.assertEqual(reminder_endeavour.warning_time, 3)
        self.assertEqual(reminder_endeavour.occassions, 'All')
        self.assertEqual(reminder_endeavour.guide_show, self.guide_shows[1])
        self.reminders.append(reminder_endeavour)

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
    

    def tearDown(self) -> None:
        self.test_db.recorded_shows_collection.delete_many({})
        return super().tearDown()

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
