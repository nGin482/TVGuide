from datetime import datetime
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch
import sys
import unittest

load_dotenv('.env')

from database.models.GuideEpisode import GuideEpisode
from tests.test_data.guide_episodes import guide_episodes
from tests.test_data.show_episodes import dw_show_episodes, show_episodes
from tests.test_data.show_details import show_details


class TestGuideEpisode(unittest.TestCase):


    def setUp(self) -> None:
        super().setUp()

    
    @patch('sqlalchemy.orm.session')
    @patch('database.models.GuideEpisode.get_shows_for_date')
    def test_get_guide_episodes(self, mock_get_shows: MagicMock, mock_session: MagicMock):
        mock_session.return_value = True
        mock_get_shows.return_value = guide_episodes
        episodes = GuideEpisode.get_shows_for_date(datetime(year=2024, month=8, day=10), mock_session)
        
        self.assertIsInstance(episodes, list)
        self.assertEqual(len(episodes), 2)
        self.assertIsInstance(episodes[0], GuideEpisode)
        self.assertEqual(episodes[0].title, 'Doctor Who')
        self.assertEqual(episodes[1].title, 'Endeavour')

    def test_guide_episode_repeat_false_no_show_episode(self):
        self.assertFalse(guide_episodes[1].repeat)

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_repeat_false_show_episode(self, mock_session: MagicMock):
        mock_session.return_value = True
        show_episodes[0].air_dates = []
        guide_episodes[0].show_episode = show_episodes[0]
        guide_episodes[0].check_repeat(mock_session)
        self.assertFalse(guide_episodes[0].repeat)
    
    @patch('sqlalchemy.orm.session')
    def test_guide_episode_repeat_true(self, mock_session: MagicMock):
        mock_session.return_value = True
        show_episodes[0].air_dates = [datetime(2023, 9, 12, hour=20, minute=30)]
        guide_episodes[0].show_episode = show_episodes[0]
        guide_episodes[0].check_repeat(mock_session)
        self.assertTrue(guide_episodes[0].repeat)

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_capture_db_event_show_details_episode_none(self, mock_session: MagicMock):
        mock_session.return_value = True
        guide_episodes[0].show_details = None
        guide_episodes[0].show_episode = None
        
        self.assertIsNone(guide_episodes[0].show_details)
        self.assertIsNone(guide_episodes[0].show_episode)
        
        guide_episodes[0].capture_db_event(mock_session)
        self.assertIsNotNone(guide_episodes[0].show_details)
        self.assertEqual(guide_episodes[0].show_details.title, 'Doctor Who')
        self.assertIsNotNone(guide_episodes[0].show_episode)
        self.assertEqual(guide_episodes[0].show_episode.show, 'Doctor Who')

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_capture_db_event_show_episode_none(self, mock_session: MagicMock):
        mock_session.return_value = True

        guide_episodes[0].show_details = show_details[0]
        guide_episodes[0].show_episode = None
        
        self.assertIsNotNone(guide_episodes[0].show_details)
        self.assertIsNone(guide_episodes[0].show_episode)

        guide_episodes[0].capture_db_event(mock_session)

        self.assertIsNotNone(guide_episodes[0].show_details)
        self.assertEqual(guide_episodes[0].show_details.title, 'Doctor Who')
        self.assertIsNotNone(guide_episodes[0].show_episode)
        self.assertEqual(guide_episodes[0].show_episode.show, 'Doctor Who')
        self.assertEqual(guide_episodes[0].db_event, "Season 2 Episode 5 (Rise of the Cybermen) has been inserted")

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_capture_db_event_show_details_none(self, mock_session: MagicMock):
        mock_session.return_value = True

        guide_episodes[0].show_details = None
        guide_episodes[0].show_episode = show_episodes[0]
        
        self.assertIsNone(guide_episodes[0].show_details)
        self.assertIsNotNone(guide_episodes[0].show_episode)

        guide_episodes[0].capture_db_event(mock_session)

        self.assertIsNotNone(guide_episodes[0].show_details)
        self.assertEqual(guide_episodes[0].show_details.title, 'Doctor Who')
        self.assertIsNotNone(guide_episodes[0].show_episode)
        self.assertEqual(guide_episodes[0].show_episode.show, 'Doctor Who')
        self.assertEqual(guide_episodes[0].db_event, "This show is now being recorded")

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_capture_db_event_adds_air_date(self, mock_session: MagicMock):
        mock_session.return_value = True
        guide_episodes[0].show_details = show_details[0]
        guide_episodes[0].show_episode = show_episodes[0]
        
        guide_episodes[0].capture_db_event(mock_session)

        self.assertIn(datetime(2024, 8, 10, 22, 4), guide_episodes[0].show_episode.air_dates)
        self.assertEqual(guide_episodes[0].db_event, "Season 2 Episode 5 (Rise of the Cybermen) has aired today")

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_capture_db_event_adds_channel(self, mock_session: MagicMock):
        mock_session.return_value = True
        guide_episodes[0].show_details = show_details[0]
        guide_episodes[0].show_episode = show_episodes[0]

        guide_episodes[0].channel = "ABC3"
        
        self.assertNotIn("ABC3", guide_episodes[0].show_episode.channels)
        
        guide_episodes[0].capture_db_event(mock_session)

        self.assertIn("ABC3", guide_episodes[0].show_episode.channels)
        self.assertEqual(guide_episodes[0].db_event, "ABC3 has been added to the channel list.")
        guide_episodes[0].channel = "ABC2"

    def test_guide_episode_message_string(self):
        self.assertEqual(guide_episodes[0].message_string(), "22:04: Doctor Who is on ABC2 (Season 2, Episode 5: Rise of the Cybermen)")

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_message_string_repeat(self, mock_session: MagicMock):
        mock_session.return_value = True
        guide_episodes[0].show_episode = show_episodes[0]

        guide_episodes[0].check_repeat(mock_session)
        message = guide_episodes[0].message_string()

        self.assertEqual(message, "22:04: Doctor Who is on ABC2 (Season 2, Episode 5: Rise of the Cybermen) (Repeat)")

    @patch('sqlalchemy.orm.session')
    def test_guide_episode_to_dict(self, mock_session: MagicMock):

        guide_episodes[0].show_episode = None
        guide_episodes[0].check_repeat(mock_session)

        guide_episode_dict = guide_episodes[0].to_dict()

        self.assertEqual(guide_episode_dict['title'], "Doctor Who")
        self.assertEqual(guide_episode_dict['start_time'], "22:04")
        self.assertEqual(guide_episode_dict['end_time'], "22:51")
        self.assertEqual(guide_episode_dict['channel'], "ABC2")
        self.assertEqual(guide_episode_dict['season_number'], 2)
        self.assertEqual(guide_episode_dict['episode_number'], 5)
        self.assertEqual(guide_episode_dict['episode_title'], "Rise of the Cybermen")
        self.assertEqual(guide_episode_dict['repeat'], False)
        self.assertEqual(guide_episode_dict['db_event'], "Season 2 Episode 5 (Rise of the Cybermen) has been inserted")
