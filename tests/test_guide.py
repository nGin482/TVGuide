from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from textwrap import dedent
import unittest
import json

from database.models.GuideModel import Guide
from tests.test_data.guide_episodes import guide_episodes
from tests.test_data.reminders import reminders
from tests.test_data.show_details import show_details
from tests.test_data.show_episodes import dw_show_episodes
from tests.test_data.search_items import search_items


class TestGuide(unittest.TestCase):

    def setUp(self):
        super().setUpClass()
        
        with open('tests/test_data/fta_data.json') as fd:
            self.fta_data = json.load(fd)

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_search_fta_finds_all_details(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2023, 10, 30))
        guide.create_new_guide()

        count = 0
        for channel in self.fta_data['schedule']:
            count += len(channel['listing'])
        
        guide_show_all_details = guide.fta_shows
        self.assertEqual(len(guide.fta_shows), count)
        self.assertEqual(guide_show_all_details[0].season_number, 4)
        self.assertEqual(guide_show_all_details[0].episode_number, 4)
        self.assertEqual(guide_show_all_details[0].episode_title, "The Sontaran Strategem")
        self.assertEqual(mock_session_commit(), "added")

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_search_fta_finds_details_from_show_episode(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()
        
        self.assertEqual(guide.fta_shows[3].season_number, 4)
        self.assertEqual(guide.fta_shows[3].episode_number, 7)
        self.assertEqual(self.fta_data['schedule'][0]['listing'][2]['episode_title'], "The Unicorn and the Wasp")

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_search_fta_finds_no_details(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()
        
        self.assertEqual(guide.fta_shows[4].season_number, -1)
        self.assertEqual(guide.fta_shows[4].episode_number, 0)
        self.assertEqual(guide.fta_shows[4].episode_title, "")

    # test search item removes one
    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.check_search_conditions')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_removes_episode_failed_search_condition(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_search_conditions: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
        mock_source_data.return_value = self.fta_data
        mock_search_items.return_value = search_items
        mock_search_conditions.side_effect = [True, True, False, True, True]
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        self.assertEqual(len(guide.fta_shows), 4)
    
    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_list_is_sorted(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        self.assertTrue(all(guide.fta_shows[i].start_time <= guide.fta_shows[i+1].start_time for i in range(len(guide.fta_shows) - 1)))
    
    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_create_adds_guide_and_guide_episodes(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]

        guide = Guide(datetime(2024, 10, 12))

        self.assertEqual(len(guide.fta_shows), 0)
        mock_session_commit.assert_not_called()

        guide.create_new_guide()

        self.assertEqual(len(guide.fta_shows), 5)
        mock_session_commit.assert_called()
    
    @patch('sqlalchemy.orm.session')
    def test_guide_get_shows_for_date_returns_episodes_from_db(self, mock_session: MagicMock):
        mock_session.scalars.return_value = guide_episodes

        guide = Guide(datetime(2024, 10, 12))

        self.assertEqual(len(guide.fta_shows), 0)

        guide.get_shows(mock_session)

        self.assertEqual(len(guide.fta_shows), 2)
        self.assertEqual(guide.fta_shows[0].title, "Doctor Who")
        self.assertEqual(guide.fta_shows[1].title, "Endeavour")

    @patch('services.APIClient.APIClient.get')
    def test_guide_gets_source_data(self, mock_api_client: MagicMock):
        mock_api_client.return_value = self.fta_data

        guide = Guide(datetime(2024, 10, 12))

        data = guide.get_source_data("https://source-data.com")

        schedule = data['schedule']
        self.assertEqual(len(schedule), 2)
        self.assertEqual(schedule[0]['channel'], "ABC1")
        self.assertEqual(len(schedule[0]['listing']), 4)
        self.assertEqual(schedule[1]['channel'], "ABC2")
        self.assertEqual(len(schedule[1]['listing']), 1)
    
    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_message_contains_date(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        self.assertIn('12-10-2024', guide.compose_message())

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_message_handles_no_results(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
        mock_source_data.return_value = { 'schedule': [] }
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        self.assertIn('Nothing on Free to Air today', guide.compose_message())

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_message_contains_all_episode_strings(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        expected = """
        00:00: Doctor Who is on ABC1 (Season 4, Episode 4: The Sontaran Strategem)
        00:50: Doctor Who is on ABC1 (Season 4, Episode 5: The Poison Sky)
        01:30: Doctor Who is on ABC2 (Season 4, Episode 6: The Doctor's Daughter)
        03:00: Doctor Who is on ABC1 (Season 4, Episode 7: The Unicorn and the Wasp)
        03:50: Doctor Who is on ABC1 (Season Unknown, Episode 0)
        """
        expected = dedent(expected)

        self.assertIn(expected, guide.compose_message())
    
    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_empty_reminders_message(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()

        self.assertIn('There are no reminders scheduled for today', guide.compose_reminder_message())

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_reminders_message_contains_reminder_details(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_reminder.side_effect = [reminders[0], reminders[0], reminders[0], reminders[0], reminders[0]]
        mock_session_commit.return_value = "added"
        mock_session_merge.side_effect = [True, True, True, True, True]

        guide = Guide(datetime(2023, 10, 30))
        guide.create_new_guide()
        for episode in guide.fta_shows:
            episode.reminder = reminders[0]
            episode.reminder.notify_time = episode.start_time - timedelta(minutes=3)

        reminders_message = guide.compose_reminder_message()

        self.assertIn('REMINDER: Doctor Who is on ABC1 at 00:00', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 00:50', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC2 at 01:30', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 03:00', reminders_message)
        self.assertIn('REMINDER: Doctor Who is on ABC1 at 03:50', reminders_message)

    @patch('sqlalchemy.orm.session.Session.merge')
    @patch('sqlalchemy.orm.session.Session.commit')
    @patch('sqlalchemy.orm.session.Session.scalar')
    @patch('database.models.ShowEpisodeModel.ShowEpisode.search_for_episode')
    @patch('database.models.ShowDetailsModel.ShowDetails.get_show_by_title')
    @patch('database.models.SearchItemModel.SearchItem.get_active_searches')
    @patch('database.models.GuideModel.Guide.get_source_data')
    def test_guide_events_message_contains_all_events(
        self,
        mock_source_data: MagicMock,
        mock_search_items: MagicMock,
        mock_show_detail: MagicMock,
        mock_show_episode: MagicMock,
        mock_reminder: MagicMock,
        mock_session_commit: MagicMock,
        mock_session_merge: MagicMock
    ):
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
        mock_session_merge.side_effect = [True, True, True, True, True]
        
        guide = Guide(datetime(2024, 10, 12))
        guide.create_new_guide()
        
        self.assertIn("This show is now being recorded", guide.compose_events_message())

    def tearDown(self) -> None:
        super().tearDown()


if __name__ == '__main__':
    unittest.main()
