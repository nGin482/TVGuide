from datetime import datetime
from pymongo import MongoClient
from mongomock import MongoClient as Client, Database, Collection
import unittest
import json
import os

from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.models.Reminders import Reminder
from exceptions.DatabaseError import SeasonNotFoundError
from repeat_handler import get_today_shows_data


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.test_db = self.client.get_database('TVGUIDE_DB')
        self.recorded_shows_collection = self.test_db.get_collection('RecordedShows')
        # self.test_db = MongoClient(os.getenv('TVGUIDE_DB')).get_database('test')
        # self.recorded_shows_collection = self.test_db.get_collection('RecordedShows')

        with open('tests/test_data/recorded_shows.json') as fd:
            self.recorded_shows: list[dict] = json.load(fd)

        
        with open(f"today_guide/{os.listdir('today_guide')[0]}") as fd:
            today_shows = json.load(fd)
        
        with open(f'tests/test_guide_list.json') as fd:
            data: list[dict] = json.load(fd)
        data.extend(today_shows['FTA'])
        
    def test_connection(self):
        self.assertIsInstance(self.test_db, Database)
        self.assertIsInstance(self.recorded_shows_collection, Collection)

    def test_create_recorded_show_from_db(self):
        recorded_show = RecordedShow.from_database(self.recorded_shows[0])
        self.assertEqual(recorded_show.title, self.recorded_shows[0]['show'])
        self.assertGreater(len(recorded_show.seasons), 0)
        episode_count = 0
        for season in recorded_show.seasons:
            for episode in season.episodes:
                episode_count += 1
        self.assertGreater(episode_count, 0)

    def test_create_recorded_show_from_guide_show(self):
        new_show = GuideShow(
            'Endeavour',
            'ABC1',
            datetime(2022, 8, 26),
            True,
            '6',
            1,
            'Pylon',
            RecordedShow.from_database(RecordedShow.get_one_recorded_show('Endeavour'))
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

    def test_insert_new_show(self):
        new_unforgotten_episode = GuideShow(
            'Unforgotten',
            'SBS',
            datetime(2022, 8, 10, 20, 30),
            True,
            '4',
            1,
            'Episode 1',
            None
        )
        print(len(RecordedShow.get_all_recorded_shows()))
        new_unforgotten_episode.capture_db_event()
        print(len(RecordedShow.get_all_recorded_shows()))
    
    def test_insert_new_season(self):
        new_show = GuideShow(
            'Endeavour',
            'ABC1',
            datetime.now(),
            True,
            '10',
            1,
            'Test',
            self.recorded_shows_collection.find_one({'show': 'Endeavour'})
        )

        new_show.capture_db_event()

    def test_insert_new_episode(self):
        new_show = GuideShow(
            'Endeavour',
            'ABC1',
            datetime.now(),
            True,
            '10',
            1,
            'Test',
            self.recorded_shows_collection.find_one({'show': 'Endeavour'})
        )

        new_show.capture_db_event()


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
        print(self.guide_shows)
        reminders = Reminder.get_reminders_for_shows(self.guide_shows)
        print(reminders)
        self.assertTrue(reminders[0].compare_reminder_interval())
        with self.assertRaises(IndexError) as exception_context:
            reminders[1].compare_reminder_interval()
    

    def tearDown(self) -> None:
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
