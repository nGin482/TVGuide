from dotenv import load_dotenv
from unittest.mock import MagicMock, patch
import unittest
import json
import os

from database.models.SearchItemModel import SearchItem
from tests.test_data.search_items import search_items


class TestSearchConditions(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        self.search_items = search_items

    @patch('sqlalchemy.orm.session')
    def test_get_all_search_items(self, mock_session: MagicMock):
        mock_session.scalars.return_value = self.search_items

        search_list = SearchItem.get_all_search_items(mock_session)

        self.assertEqual(len(search_list), 3)
        self.assertEqual(search_list[0].show, 'Doctor Who')
        self.assertEqual(search_list[1].show, 'Endeavour')
        self.assertTrue(search_list[0].search_active)
        self.assertTrue(search_list[1].search_active)

    @patch('sqlalchemy.orm.session')
    def test_get_active_searches(self, mock_session: MagicMock):
        self.search_items[2].search_active = False
        mock_session.scalars.return_value = [
            search_item for search_item in self.search_items if search_item.search_active is True
        ]

        search_list = SearchItem.get_active_searches(mock_session)

        self.assertEqual(len(search_list), 2)
        self.assertTrue(search_list[0].search_active)
        self.assertTrue(search_list[1].search_active)

    @patch('sqlalchemy.orm.session')
    def test_get_search_item(self, mock_session: MagicMock):
        mock_session.scalar.return_value = self.search_items[1]

        search_item = SearchItem.get_search_item("Endeavour", mock_session)

        self.assertIsNotNone(search_item)
        self.assertEqual(search_item.show, "Endeavour")    

    def test_search_conditions_no_details(self):
        episode = {
            "season_number": -1,
            "episode_title": ""
        }
        result = self.search_items[0].check_search_conditions(episode)
        self.assertTrue(result)

    def test_search_ignore_episodes_false(self):
        episode = {
            "season_number": -1,
            "episode_title": "Tooth and Claw"
        }

        result = self.search_items[0].check_search_conditions(episode)
        self.assertTrue(result)

    def test_search_ignore_episodes_true(self):
        episode = {
            "season_number": -1,
            "episode_title": "Tooth and Claw"
        }
        self.search_items[0].ignore_episodes = [
            "Tooth and Claw"
        ]

        result = self.search_items[0].check_search_conditions(episode)
        self.assertFalse(result)

    def test_search_inside_season_range(self):
        episode = {
            "season_number": 7,
            "episode_number": 1,
            "episode_title": "Asylum of the Daleks"
        }

        result = self.search_items[0].check_search_conditions(episode)
        self.assertTrue(result)

    def test_search_outside_season_range(self):
        episode = {
            "season_number": 15,
            "episode_number": 4,
            "episode_title": ""
        }

        result = self.search_items[0].check_search_conditions(episode)
        self.assertFalse(result)

    def test_search_ignore_seasons(self):
        episode = {
            "season_number": 8,
            "episode_number": 7,
            "episode_title": "Kill the Moon"
        }
        self.search_items[0].ignore_seasons = [8]

        result = self.search_items[0].check_search_conditions(episode)
        self.assertFalse(result)

    def test_search_ignore_episodes(self):
        episode = {
            "season_number": 8,
            "episode_number": 7,
            "episode_title": "Kill the Moon"
        }
        self.search_items[0].ignore_episodes = ["Kill the Moon"]

        result = self.search_items[0].check_search_conditions(episode)
        self.assertFalse(result)

    def test_to_dict(self):
        self.search_items[0].ignore_seasons = []
        self.search_items[0].ignore_episodes = []
        result = search_items[0].to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['show'], "Doctor Who")
        self.assertTrue(result['search_active'])
        self.assertFalse(result['exact_title_match'])
        self.assertEqual(len(result['conditions']['ignore_seasons']), 0)
        self.assertEqual(len(result['conditions']['ignore_episodes']), 0)
        self.assertEqual(len(result['conditions']['ignore_titles']), 0)
        self.assertEqual(result['conditions']['min_season_number'], 1)
        self.assertEqual(result['conditions']['max_season_number'], 14)


    def tearDown(self) -> None:
        super().tearDown()
        self.search_items = search_items

        
