from unittest.mock import MagicMock, patch
import unittest

from services.ShowService import ShowService
from database.models.ShowEpisodeModel import ShowEpisode
from utils.types.models import TShowEpisode

from tests.test_data.show_details import show_details
from tests.test_data.show_episodes import dw_show_episodes
from tests.test_data.tvmaze import mock_tvmaze_episodes

class TestShowService(unittest.TestCase):

    def setUp(self):
        self.show_service = ShowService()
        return super().setUp()


    @patch("services.ShowService.ShowDetails.get_show_by_title")
    def test_show_service_get_show_by_title(self, mock_show_details: MagicMock):
        mock_show_details.return_value = show_details[0]
        mock_session = MagicMock()

        show = self.show_service.get_show_by_title("Doctor Who", mock_session)

        self.assertEqual(show, show_details[0])

    # TODO: Unit tests for add_show()

    @patch("services.ShowService.tvmaze_api.get_show_seasons")
    def test_show_service_needs_episode_refresh(self, mock_tvmaze_seasons: MagicMock):
        show_data = show_details[0]
        show_data.show_episodes = dw_show_episodes
        mock_tvmaze_seasons.return_value = [
            season["season"]
            for season in mock_tvmaze_episodes
        ]

        episode_check = self.show_service.needs_episode_refresh(show_data)

        self.assertEqual(
            episode_check,
            {
                "needs_refresh": True,
                "latest_season_recorded": 4,
                "tvmaze_season_max": 5,
            }
        )

    @patch("services.ShowService.ShowEpisode.add_all_episodes")
    @patch("services.ShowService.tvmaze_api.get_show_episodes")
    def test_show_service_fetch_latest_episodes(
        self,
        mock_get_show_episodes: MagicMock,
        mock_add_all_episodes: MagicMock
    ):
        show_episodes: list[TShowEpisode] = [
            {
                "show": mock_episode["_links"]["show"]["name"],
                "season_number": mock_episode["season"],
                "episode_number": mock_episode["number"],
                "episode_title": mock_episode["name"],
                "summary": mock_episode["summary"],
            }
            for mock_episode in mock_tvmaze_episodes
            if mock_episode["season"] >= 5
        ]
        mock_get_show_episodes.return_value = show_episodes
        mock_session = MagicMock()

        show_data = show_details[0]
        show_data.show_episodes = dw_show_episodes  

        episodes_added = self.show_service.fetch_latest_episodes(
            show_data,
            {
                "needs_refresh": True,
                "latest_season_recorded": 4,
                "tvmaze_season_max": 5
            },
            mock_session
        )

        mock_get_show_episodes.assert_called_once_with(
            "210",
            5,
            5
        )

        # Assert what ShowEpisode.add_all_episodes was called with
        mock_add_all_episodes.assert_called_once()
        mock_add_all_episodes_args, _ = mock_add_all_episodes.call_args
        episode_list_arg = mock_add_all_episodes_args[0]
        self.assertEqual(len(episode_list_arg), 1)
        captured_episode = episode_list_arg[0]
        self.assertEqual(captured_episode.show, "Doctor Who")
        self.assertEqual(captured_episode.season_number, 5)
        self.assertEqual(captured_episode.episode_number, 1)
        self.assertEqual(captured_episode.episode_title, "The Eleventh Hour")
        self.assertEqual(captured_episode.summary, "Season 5 Episode 1")

        self.assertEqual(
            episodes_added,
            {
                "episodes_added": 1,
            }
        )