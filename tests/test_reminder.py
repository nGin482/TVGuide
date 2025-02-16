from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import MagicMock, patch

from database.models.Reminder import Reminder
from tests.test_data.guide_episodes import guide_episodes
from tests.test_data.reminders import reminders
from tests.test_data.show_episodes import dw_show_episodes

class TestReminder(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    
    @patch('sqlalchemy.orm.session')
    def test_reminder_search_returns_all(self, mock_session: MagicMock):
        mock_session.scalars.return_value = reminders

        reminders_search = Reminder.get_all_reminders(mock_session)

        self.assertEqual(len(reminders_search), 5)
        self.assertEqual(reminders_search[0].show, "Doctor Who")
        self.assertEqual(reminders_search[1].show, "Endeavour")
        self.assertEqual(reminders_search[2].show, "Transformers: Prime")

    @patch('sqlalchemy.orm.session')
    def test_reminder_search_returns_one_reminder(self, mock_session: MagicMock):
        mock_session.scalar.return_value = reminders[1]

        reminder = Reminder.get_reminder_by_show("Endeavour", mock_session)

        self.assertEqual(reminder.show, "Endeavour")
        self.assertEqual(reminder.alert, "Before")
        self.assertEqual(reminder.warning_time, 5)
        self.assertEqual(reminder.occasions, "All")

    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_added_to_database(self, mock_session: MagicMock):
        mock_session.commit.side_effect = ["added"]

        reminder = Reminder(
            "Person of Interest",
            "Before",
            3,
            "All"
        )

        reminder.add_reminder(mock_session)

        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_updated(self, mock_session: MagicMock):
        mock_session.commit.side_effect = ["updated"]

        reminder = Reminder(
            "Person of Interest",
            "Before",
            3,
            "All"
        )

        self.assertEqual(reminder.warning_time, 3)

        reminder.update_reminder("warning_time", 5, mock_session)

        self.assertEqual(reminder.warning_time, 5)

        mock_session.commit.assert_called()

    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_deleted(self, mock_session: MagicMock):
        mock_session.commit.side_effect = ["deleted"]

        reminder = Reminder(
            "Person of Interest",
            "Before",
            3,
            "All"
        )

        reminder.delete_reminder(mock_session)

        mock_session.delete.assert_called()
        mock_session.commit.assert_called()
        
    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_interval_all_occasions(self, mock_session: MagicMock):

        set_reminder = reminders[0].compare_reminder_interval(guide_episodes[0], mock_session)

        self.assertTrue(set_reminder)

    @patch('database.models.ShowEpisode.is_latest_episode')
    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_interval_true_latest_occasion(self, mock_session: MagicMock, mock_show_episode: MagicMock):
        mock_show_episode.return_value = True
        guide_episodes[0].show_episode = dw_show_episodes[0]

        set_reminder = reminders[3].compare_reminder_interval(guide_episodes[0], mock_session)

        self.assertTrue(set_reminder)

    @patch('database.models.ShowEpisode.is_latest_episode')
    @patch('sqlalchemy.orm.session')
    def test_reminder_reminder_interval_false_latest_occasion(self, mock_session: MagicMock, mock_show_episode: MagicMock):
        mock_show_episode.return_value = False
        guide_episodes[0].show_episode = dw_show_episodes[0]

        set_reminder = reminders[3].compare_reminder_interval(guide_episodes[0], mock_session)

        self.assertFalse(set_reminder)

    def test_reminder_calculate_notification_time_before(self):

        start_time = datetime(year=2024, month=10, day=19, hour=20, minute=30)
        reminders[0].calculate_notification_time(start_time)

        notify_time = datetime(year=2024, month=10, day=19, hour=20, minute=27)
        difference = notify_time - start_time

        self.assertEqual(abs(difference.total_seconds()) / 60, reminders[0].warning_time)
        self.assertEqual(reminders[0].notify_time, notify_time)

    def test_reminder_calculate_notification_time_onstart(self):

        start_time = datetime(year=2024, month=10, day=19, hour=20, minute=30)
        reminders[3].calculate_notification_time(start_time)

        notify_time = datetime(year=2024, month=10, day=19, hour=20, minute=30)
        difference = notify_time - start_time

        self.assertEqual(abs(difference.total_seconds()) / 60, reminders[3].warning_time)
        self.assertEqual(reminders[3].notify_time, notify_time)

    def test_reminder_calculate_notification_time_after(self):

        start_time = datetime(year=2024, month=10, day=19, hour=20, minute=30)
        reminders[4].calculate_notification_time(start_time)

        notify_time = datetime(year=2024, month=10, day=19, hour=20, minute=34)
        difference = notify_time - start_time

        self.assertEqual(abs(difference.total_seconds()) / 60, reminders[4].warning_time)
        self.assertEqual(reminders[4].notify_time, notify_time)

    def test_reminder_to_dict(self):

        reminder_dict = reminders[0].to_dict()

        self.assertEqual(reminder_dict['show'], "Doctor Who")
        self.assertEqual(reminder_dict['alert'], "Before")
        self.assertEqual(reminder_dict['warning_time'], 3)
        self.assertEqual(reminder_dict['occasions'], "All")
    