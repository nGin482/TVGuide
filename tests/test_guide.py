from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import unittest
import json

from database.DatabaseService import DatabaseService
from database.models.RecordedShow import RecordedShow
from database.mongo import mongo_client
from guide import search_free_to_air

requests = Mock()
# datetime = Mock()
# https://realpython.com/python-mock-library/

class TestGuide(unittest.TestCase):

    def setUp(self):
        self.database_service = DatabaseService(mongo_client().get_database('test'))

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


if __name__ == '__main__':
    unittest.main()
