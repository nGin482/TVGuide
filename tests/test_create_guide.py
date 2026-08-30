from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json
import logging
import unittest
import warnings

from guide import create_guide

from tests.test_data.show_details import show_details
from tests.test_data.show_episodes import dw_show_episodes
from tests.test_data.search_items import search_items


class TestCreateGuide(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        logging.disable()
        
        with open("tests/test_data/fta_data.json") as fd:
            self.fta_data = json.load(fd)

        # Suppress deprecation warnings from the discord library
        warnings.filterwarnings(
            "ignore", 
            category=DeprecationWarning, 
            module="discord"
        )


    @patch("sqlalchemy.orm.session.Session.commit")
    @patch("sqlalchemy.orm.session.Session.execute")
    @patch("database.models.Reminder.get_reminder_by_show")
    @patch("database.models.ShowEpisodeModel.ShowEpisode.search_for_episode")
    @patch("database.models.ShowDetailsModel.ShowDetails.get_show_by_title")
    @patch("database.models.SearchItemModel.SearchItem.get_active_searches")
    @patch("database.models.GuideModel.Guide.get_source_data")
    @patch("services.hermes.hermes.hermes", new_callable=AsyncMock)
    @patch("utils.get_current_date")
    async def test_guide_messages_sent(
        self,
        mock_date: MagicMock,
        mock_hermes: MagicMock,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_execute: MagicMock,
        mock_session_commit: MagicMock,
    ):
        mock_date.return_value = datetime(2026, 8, 10)
        mock_source_data.return_value = self.fta_data
        mock_search_items.return_value = search_items
        mock_show_detail.return_value = show_details[0]
        mock_show_episode.side_effect = [
            dw_show_episodes[7],
            dw_show_episodes[8],
            dw_show_episodes[9],
            dw_show_episodes[10],
            None
        ]
        mock_reminder.return_value = None
        mock_session_commit.return_value = "added"
        mock_execute.return_value = None

        await create_guide()

        guide_message = """# Monday 10-08-2026 TVGuide

Free to Air:
* 09:00: Doctor Who is on ABC1 (Season 4, Episode 4: The Sontaran Strategem)
* 09:50: Doctor Who is on ABC1 (Season 4, Episode 5: The Poison Sky)
* 11:30: Doctor Who is on ABC2 (Season 4, Episode 6: The Doctor's Daughter)
* 13:00: Doctor Who is on ABC1 (Season 4, Episode 7: The Unicorn and the Wasp)
* 13:50: Doctor Who is on ABC1 (Season Unknown, Episode 0)
"""
        reminders_message = """## Reminders

There are no reminders scheduled for today"""
        events_message = """# Events - Monday 10-08-2026
* Doctor Who - This show is now being recorded
* Doctor Who - This show is now being recorded
* Doctor Who - This show is now being recorded
* Doctor Who - This show is now being recorded
* Doctor Who - This show is now being recorded"""

        mock_hermes.send_guide_message.assert_called_once_with(
            guide_message,
            reminders_message,
            events_message
        )