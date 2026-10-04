from unittest.mock import MagicMock, patch
import unittest

from services.tvmaze import tvmaze_api

from tests.test_data.tvmaze import (
    mock_tvmaze_episodes,
    mock_tvmaze_seasons,
    mock_tvmaze_show
)

class TestTVMazeAPI(unittest.TestCase):

    def setUp(self):
        self.mock_tvmaze_show = mock_tvmaze_show
        self.mock_tvmaze_seasons = mock_tvmaze_seasons
        self.mock_tvmaze_episodes = mock_tvmaze_episodes
        return super().setUp()

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_show_returns_show(self, mock_api: MagicMock):
        mock_api.return_value = self.mock_tvmaze_show

        show = tvmaze_api.get_show("Doctor Who")

        mock_api.assert_called_once_with(
            "https://api.tvmaze.com/singlesearch/shows?q=Doctor Who"
        )

        self.assertEqual(show, self.mock_tvmaze_show)

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_seasons_returns_list_of_seasons(self, mock_api: MagicMock):
        mock_api.return_value = self.mock_tvmaze_seasons

        seasons = tvmaze_api.get_show_seasons("210")

        mock_api.assert_called_once_with(
            "https://api.tvmaze.com/shows/210/seasons"
        )

        self.assertEqual(len(seasons), 3)
        self.assertEqual(seasons, [1, 2, 3])

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_show_episodes_returns_episode_list(self, mock_api: MagicMock):
        mock_api.return_value = self.mock_tvmaze_episodes

        episodes = tvmaze_api.get_show_episodes("210", 1, None, False)

        mock_api.assert_called_once_with(
            "https://api.tvmaze.com/shows/210/episodes"
        )

        self.assertEqual(len(episodes), 6)
        expected_episode = {
            "show": "Doctor Who",
            "season_number": 1,
            "episode_number": 1,
            "episode_title": "Rose",
            "summary": "Season 1 Episode 1",
        }
        self.assertEqual(episodes[0], expected_episode)

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_show_episodes_includes_specials(self, mock_api: MagicMock):
        mock_api.return_value = self.mock_tvmaze_episodes

        episodes = tvmaze_api.get_show_episodes("210", 1, None, True)

        mock_api.assert_called_once_with(
            "https://api.tvmaze.com/shows/210/episodes?specials=1"
        )

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_show_episodes_returns_episodes_season_start(
        self,
        mock_api: MagicMock
    ):
        mock_api.return_value = self.mock_tvmaze_episodes

        episodes = tvmaze_api.get_show_episodes("210", 2, None, False)

        self.assertEqual(len(episodes), 3)
        episode_seasons = [episode["season_number"] for episode in episodes]
        self.assertEqual(episode_seasons, [2, 2, 5])

    @patch("services.tvmaze.tvmaze_api.api_client.get")
    def test_get_show_episodes_returns_episodes_season_end(
        self,
        mock_api: MagicMock
    ):
        mock_api.return_value = self.mock_tvmaze_episodes

        episodes = tvmaze_api.get_show_episodes("210", 1, 1, False)

        self.assertEqual(len(episodes), 3)
        episode_seasons = [episode["season_number"] for episode in episodes]
        self.assertEqual(episode_seasons, [1, 1, 1])

    
