from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from database.models.ShowEpisodeModel import ShowEpisode
from tests.test_data.show_episodes import (
    add_channel_show_episodes,
    add_episodes,
    add_episode,
    channel_check_show_episodes,
    dw_show_episodes,
    find_episode,
    find_episodes_by_season,
    show_episodes
)

class TestShowEpisode(TestCase):

    def setUp(self):
        super().setUp()

    @patch('sqlalchemy.select')
    @patch('sqlalchemy.orm.session')
    def test_search_for_episode_season_number(self, mock_session: MagicMock, mock_select: MagicMock):
        episode = find_episode(show_episodes, "Doctor Who", 2, 5, "Rise of the Cybermen")
        mock_select.where.side_effect = find_episode(show_episodes, "Doctor Who", 2, 5, "Rise of the Cybermen")
        mock_session.scalar.return_value = episode

        episode = ShowEpisode.search_for_episode("Doctor Who", 2, 5, "Rise of the Cybermen", mock_session)

        self.assertEqual(episode.show, "Doctor Who")
        self.assertEqual(episode.season_number, 2)
        self.assertEqual(episode.episode_number, 5)
        self.assertEqual(episode.episode_title, "Rise of the Cybermen")

    @patch('sqlalchemy.select')
    @patch('sqlalchemy.orm.session')
    def test_search_for_episode_episode_title(self, mock_session: MagicMock, mock_select: MagicMock):
        episode = find_episode(show_episodes, "Endeavour", -1, 0, "Icarus")
        mock_select.where.side_effect = find_episode(show_episodes, "Endeavour", -1, 0, "Icarus")
        mock_session.scalar.return_value = episode

        episode = ShowEpisode.search_for_episode("Endeavour", -1, 0, "Icarus", mock_session)

        self.assertEqual(episode.show, "Endeavour")
        self.assertEqual(episode.season_number, 5)
        self.assertEqual(episode.episode_number, 6)
        self.assertEqual(episode.episode_title, "Icarus")

    @patch('sqlalchemy.select')
    @patch('sqlalchemy.orm.session')
    def test_search_for_episodes_by_season(self, mock_session: MagicMock, mock_select: MagicMock):
        episodes = find_episodes_by_season(dw_show_episodes, "Doctor Who", 2)
        mock_select.where.side_effect = find_episodes_by_season(dw_show_episodes, "Doctor Who", 2)
        mock_session.scalars.return_value = episodes

        doctor_who_s2 = ShowEpisode.get_episodes_by_season("Doctor Who", 2, mock_session)

        self.assertEqual(len(doctor_who_s2), 4)
        for episode in doctor_who_s2:
            self.assertEqual(episode.season_number, 2)
            self.assertEqual(episode.season_number, 2)
            self.assertEqual(episode.season_number, 2)
            self.assertEqual(episode.season_number, 2)

    @patch('sqlalchemy.orm.session')
    def test_add_all_episodes(self, mock_session: MagicMock):
        mock_session.add_all.return_value = add_episodes(dw_show_episodes)

        ShowEpisode.add_all_episodes(dw_show_episodes, mock_session)
        store = add_episodes(dw_show_episodes)

        self.assertEqual(len(store), 5)

    @patch('sqlalchemy.orm.session')
    def test_add_single_episodes(self, mock_session: MagicMock):
        mock_session.add.return_value = add_episode(dw_show_episodes)

        ShowEpisode.add_all_episodes(dw_show_episodes, mock_session)
        store = add_episode(dw_show_episodes[0])

        self.assertEqual(len(store), 1)
        self.assertEqual(store[0].show, "Doctor Who")
        self.assertEqual(store[0].season_number, 2)
        self.assertEqual(store[0].episode_number, 1)

    @patch('sqlalchemy.orm.session')
    def test_show_episode_latest_season(self, mock_session: MagicMock):
        mock_session.scalar.side_effect = [2, 13]

        latest_episode_check = dw_show_episodes[4].is_latest_episode(mock_session)

        self.assertTrue(latest_episode_check)

    @patch('sqlalchemy.orm.session')
    def test_show_episode_latest_episode_true(self, mock_session: MagicMock):
        mock_session.scalar.side_effect = [4, 1]

        latest_episode_check = dw_show_episodes[4].is_latest_episode(mock_session)

        self.assertTrue(latest_episode_check)

    @patch('sqlalchemy.orm.session')
    def test_show_episode_latest_episode_false(self, mock_session: MagicMock):
        mock_session.scalar.side_effect = [4, 13]

        latest_episode_check = dw_show_episodes[4].is_latest_episode(mock_session)

        self.assertFalse(latest_episode_check)

    def test_show_episode_channel_check_false_abchd(self):
        self.assertFalse(channel_check_show_episodes[0].channel_check("ABC1"))

    def test_show_episode_channel_check_false_sbshd(self):
        self.assertFalse(channel_check_show_episodes[1].channel_check("SBS"))
    
    def test_show_episode_channel_check_false_tenhd(self):
        self.assertFalse(channel_check_show_episodes[2].channel_check("10"))

    def test_show_episode_channel_check_false_episode_channel(self):
        self.assertFalse(channel_check_show_episodes[3].channel_check("ABC2"))

    def test_show_episode_channel_check_true(self):
        self.assertTrue(channel_check_show_episodes[3].channel_check("ABC1"))

    def test_show_episode_add_channel_abchd(self):
        result = add_channel_show_episodes[0].add_channel("ABC1")

        self.assertEqual(add_channel_show_episodes[0].channels, ["ABC1", "ABCHD"])
        self.assertEqual(result, "ABC1 and ABCHD have been added to the channel list.")

    def test_show_episode_add_channel_sbshd(self):
        result = add_channel_show_episodes[1].add_channel("SBS")

        self.assertEqual(add_channel_show_episodes[1].channels, ["SBS", "SBSHD"])
        self.assertEqual(result, "SBS and SBSHD have been added to the channel list.")

    def test_show_episode_add_channel_tenhd_10(self):
        result = add_channel_show_episodes[2].add_channel("10")

        self.assertEqual(add_channel_show_episodes[2].channels, ["10", "TENHD"])
        self.assertEqual(result, "10 and TENHD have been added to the channel list.")

    def test_show_episode_add_channel_tenhd_ten(self):
        result = add_channel_show_episodes[2].add_channel("TEN")

        self.assertIn("10", add_channel_show_episodes[2].channels)
        self.assertIn("TEN", add_channel_show_episodes[2].channels)
        self.assertIn("TENHD", add_channel_show_episodes[2].channels)
        self.assertEqual(result, "TEN has been added to the channel list.")

    def test_show_episode_add_channel(self):
        result = add_channel_show_episodes[3].add_channel("ABC2")

        self.assertEqual(add_channel_show_episodes[3].channels, ["ABC2"])
        self.assertEqual(result, "ABC2 has been added to the channel list.")

    def test_show_episode_add_channel_not_added_if_exists(self):
        result = add_channel_show_episodes[3].add_channel("ABC2")

        self.assertEqual(len(add_channel_show_episodes[3].channels), 1)
    
    def test_show_episode_adds_given_air_date(self):
        
        show_episodes[1].add_air_date(datetime(2024, 7, 20))

        self.assertEqual(len(show_episodes[1].air_dates), 1)
        self.assertEqual(datetime(2024, 7, 20), show_episodes[1].air_dates[0])

    @patch('data_validation.validation.Validation.get_current_date')
    def test_show_episode_adds_current_air_date(self, mock_current_date: MagicMock):
        mock_current_date.return_value = datetime(2024, 7, 21)
        
        channel_check_show_episodes[0].add_air_date()

        self.assertEqual(len(channel_check_show_episodes[0].air_dates), 1)
        self.assertEqual(datetime(2024, 7, 21), channel_check_show_episodes[0].air_dates[0])

    def test_show_episode_to_dict(self):
        
        show_episode_dict = show_episodes[1].to_dict()

        self.assertEqual(show_episode_dict['show'], "Endeavour")
        self.assertEqual(show_episode_dict['season_number'], 5)
        self.assertEqual(show_episode_dict['episode_number'], 6)
        self.assertEqual(show_episode_dict['episode_title'], "Icarus")
        self.assertEqual(show_episode_dict['summary'], "Final episode of Season 5")
        self.assertEqual(len(show_episode_dict['alternative_titles']), 0)
        self.assertEqual(show_episode_dict['channels'], ["ABC1", "ABCHD"])
        self.assertEqual(len(show_episode_dict['air_dates']), 1)
        self.assertEqual(show_episode_dict['air_dates'][0], datetime(2024, 7, 20))
