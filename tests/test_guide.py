from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from dotenv import load_dotenv
from textwrap import dedent
import unittest
import json
import os

from database.DatabaseService import DatabaseService
from database.models.Reminders import Reminder
from database.mongo import mongo_client
from guide import search_free_to_air, compose_message, reminders

requests = Mock()
# https://realpython.com/python-mock-library/

class TestGuide(unittest.TestCase):

    def setUp(self):
        load_dotenv('.env')
        self.database_service = DatabaseService(mongo_client().get_database('test'))

        with open('tests/test_data/reminders_data.json') as fd:
            reminders_data = json.load(fd)
        for reminder in reminders_data:
            new_reminder = Reminder.from_database(reminder)
            self.database_service.insert_new_reminder(new_reminder)

    def guide_data():
        with open('tests/test_data/fta_data.json') as fd:
            fta_data = json.load(fd)

        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = fta_data
        
        return response_mock
    
    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_search_fta_finds_all_details(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today
        
        data = search_free_to_air(self.database_service)
        
        guide_show_all_details = data[0]
        self.assertEqual('4', guide_show_all_details.season_number)
        self.assertEqual(4, guide_show_all_details.episode_number)
        self.assertEqual('The Sontaran Strategem', guide_show_all_details.episode_title)

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_search_fta_finds_season_episode_number(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today
        
        data = search_free_to_air(self.database_service)
        
        guide_show_episode_num = data[1]
        self.assertEqual('4', guide_show_episode_num.season_number)
        self.assertEqual(5, guide_show_episode_num.episode_number)
        self.assertEqual('', guide_show_episode_num.episode_title)

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_search_fta_finds_episode_title(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today
        
        data = search_free_to_air(self.database_service)
        
        guide_show_episode_title = data[3]
        self.assertEqual('Unknown', guide_show_episode_title.season_number)
        self.assertEqual(1, guide_show_episode_title.episode_number)
        self.assertEqual("The Doctor's Daughter", guide_show_episode_title.episode_title)

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_search_fta_finds_no_details(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today
        
        data = search_free_to_air(self.database_service)
        
        guide_show_episode_title = data[4]
        self.assertEqual('Unknown', guide_show_episode_title.season_number)
        self.assertEqual(2, guide_show_episode_title.episode_number)
        self.assertEqual("", guide_show_episode_title.episode_title)

    @patch('guide.get', return_value=guide_data())
    def test_search_is_sorted(self, mock_requests):
        data = search_free_to_air(self.database_service)

        self.assertTrue(all(data[i].time <= data[i+1].time for i in range(len(data) - 1)))
    
    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_message_contains_current_date(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today
        
        data = search_free_to_air(self.database_service)
        message = compose_message(data, [])

        self.assertIn('30-10-2023', message)

    @patch('guide.get', return_value=guide_data())
    def test_message_contains_date_provided(self, mock_requests):
        date_provided = datetime(2023, 11, 4)
        
        data = search_free_to_air(self.database_service)
        message = compose_message(data, [], date_provided)

        self.assertIn('04-11-2023', message)

    def test_message_handles_empty_list(self):
        message = compose_message([], [])

        self.assertIn('Nothing on Free to Air today', message)

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_message_creates_guide(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today

        data = search_free_to_air(self.database_service)
        message = compose_message(data, [])

        expected = """
        00:00: Doctor Who is on ABC1 (Season 4, Episode 4: The Sontaran Strategem)
        00:45: Doctor Who is on ABC1 (Season 4, Episode 5)
        01:30: Doctor Who is on ABC2 (Season 4, Episode 7: The Unicorn and the Wasp)
        03:00: Doctor Who is on ABC1 (Season Unknown, Episode 1: The Doctor's Daughter)
        03:45: Doctor Who is on ABC1 (Season Unknown, Episode 2)
        """
        expected = dedent(expected)

        self.assertIn(expected, message)
    
    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_empty_reminders_message(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today

        reminders_message = reminders([], self.database_service)

        self.assertIn('There are no reminders scheduled for today', reminders_message)

    @patch('data_validation.validation.datetime', side_effect=lambda *args, **kw: datetime(*args, **kw))
    @patch('guide.get', return_value=guide_data())
    def test_reminders_message_contains_reminder_details(self, mock_requests, mock_datetime):
        mocked_today = datetime(2023, 10, 30)
        mock_datetime.now.return_value = mocked_today

        data = search_free_to_air(self.database_service)
        reminders_message = reminders(data, self.database_service)

        self.assertIn('REMINDER: Doctor Who is on ABC1 at 00:00', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 00:45', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC2 at 01:30', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 03:00', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 03:45', reminders_message)

    def tearDown(self) -> None:
        reminders = self.database_service.get_all_reminders()
        for reminder in reminders:
            self.database_service.delete_reminder(reminder.show)


if __name__ == '__main__':
    unittest.main()
