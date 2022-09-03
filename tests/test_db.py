from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import unittest
import json
import os

from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.models.Reminders import Reminder
from exceptions.DatabaseError import SeasonNotFoundError
from repeat_handler import get_today_shows_data, tear_down


class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_db = MongoClient(os.getenv('TVGUIDE_DB')).get_database('test')
        self.recorded_shows_collection = self.test_db.get_collection('RecordedShows')
        with open(f'tests/test_data.json') as fd:
            data = json.load(fd)
        get_today_shows_data([show['title'] for show in data])
        self.guide_shows = [GuideShow(
            item['title'],
            item['channel'],
            datetime.strptime(item['time'], '%H:%M'),
            item['episode_info'],
            item['season_number'],
            item['episode_number'],
            item['episode_title']
        ) for item in data]

    def test_connection(self):
        self.assertIsInstance(self.test_db, Database)
        self.assertIsInstance(self.recorded_shows_collection, Collection)

    def test_create_recorded_show_from_guide_show(self):
        recorded_show = RecordedShow(guide_show=self.guide_shows[0])
        self.assertEqual(recorded_show.title, self.guide_shows[0].title)
        self.assertIsInstance(recorded_show.seasons[0].season_number, str)
        self.assertEqual(recorded_show.seasons[0].season_number, self.guide_shows[0].season_number)
        self.assertIsInstance(recorded_show.seasons[0].episodes[0].episode_number, int)
        self.assertEqual(recorded_show.seasons[0].episodes[0].episode_number, self.guide_shows[0].episode_number)
        self.assertEqual(recorded_show.seasons[0].episodes[0].episode_title, self.guide_shows[0].episode_title)
        self.assertIn(self.guide_shows[0].channel, recorded_show.seasons[0].episodes[0].channels)

        self.assertTrue(recorded_show.seasons[0].episodes[0].repeat)

    def test_create_recorded_show_from_db(self):
        mongodb_record:dict = RecordedShow.get_one_recorded_show(self.guide_shows[1].title)
        recorded_show = RecordedShow(mongodb_record)
        self.assertIsInstance(mongodb_record, dict)
        self.assertEqual(recorded_show.title, mongodb_record['show'])
        self.assertGreater(len(recorded_show.seasons), 0)
        self.assertGreater(len(recorded_show.find_season(self.guide_shows[1].season_number).episodes), 0)
        self.assertIsNotNone(self.guide_shows[1].recorded_show)

    def test_insert_recorded_show(self):
        new_show = GuideShow(
            'Endeavour',
            'ABC1',
            datetime.now(),
            True,
            '10',
            1,
            'Test'
        )

        self.guide_shows.append(new_show)
        with self.assertRaises(SeasonNotFoundError) as exception_context:
            new_show.find_recorded_episode()


    def test_create_reminder_from_values(self):
        reminder = Reminder.from_values(self.guide_shows[0], 'Before', 3, 'All')
        print(reminder.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder.show, self.guide_shows[0].title)
        self.assertEqual(reminder.reminder_alert, 'Before')
        self.assertEqual(reminder.warning_time, 3)
        self.assertEqual(reminder.occassions, 'All')
        self.assertEqual(reminder.guide_show, self.guide_shows[0])

        reminder = Reminder.from_values(self.guide_shows[1], 'Before', 3, 'All')
        print(reminder.guide_show.recorded_show.find_latest_season())
        self.assertEqual(reminder.show, self.guide_shows[1].title)
        self.assertEqual(reminder.reminder_alert, 'Before')
        self.assertEqual(reminder.warning_time, 3)
        self.assertEqual(reminder.occassions, 'All')
        self.assertEqual(reminder.guide_show, self.guide_shows[1])
    

    def tearDown(self) -> None:
        tear_down()
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
        # JSON file updates as well
        # guideShow_object.capture_db_event()
            # guideShow_object.repeat and channel updating during capture_db_event()
