from datetime import datetime
from dotenv import load_dotenv
import unittest
import json
import os

from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.models.Reminders import Reminder
from exceptions.DatabaseError import EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError


class TestGuideShow(unittest.TestCase):

    def setUp(self):
        load_dotenv('.env')
        self.database_service = DatabaseService(os.getenv('TVGUIDE_DB'), 'test')
        with open('tests/test_data/test_guide_list.json') as fd:
            self.data = json.load(fd)
        with open('tests/test_data/recorded_shows.json') as fd:
            temp_data = json.load(fd)
            self.recorded_shows: list['RecordedShow'] = []
            for recorded_show in temp_data:
                self.recorded_shows.append(RecordedShow.from_database(recorded_show))
        with open('tests/test_data/reminders_data.json') as fd:
            reminders_data = json.load(fd)
        for reminder in reminders_data:
            new_reminder = Reminder.from_database(reminder)
            self.database_service.insert_new_reminder(new_reminder)

    def test_season_known_sets_episode_title(self):
        dw_guide_episode = next((show for show in self.data if show['title'] == 'Doctor Who' and show['season_number'] == "4" and show['episode_number'] == 4), None)
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_guide_show = GuideShow.known_season(
            dw_guide_episode['title'],
            (dw_guide_episode['channel'], dw_guide_episode['time']),
            (dw_guide_episode['season_number'], dw_guide_episode['episode_number'], dw_guide_episode['episode_title']),
            dw_recorded_show
        )
        self.assertEqual(dw_guide_show.episode_title, 'The Sontaran Strategem')

    def test_season_known_sets_repeat_true(self):
        dw_episode = self.data[0]
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        known_episode = GuideShow.known_season(
            dw_episode['title'],
            (dw_episode['channel'], dw_episode['time']),
            (dw_episode['season_number'], dw_episode['episode_number'], dw_episode['episode_title']),
            dw_recorded_show
        )
        self.assertEqual(True, known_episode.repeat)

    def test_season_known_sets_repeat_false(self):
        episode_data = next(show for show in self.data if show['episode_title'] == 'A Good Man Goes to War')
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        known_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            dw_recorded_show
        )
        self.assertEqual(False, known_episode.repeat)

    def test_season_unknown_no_recorded_show(self):
        episode_data = next(show for show in self.data if show['episode_title'] == '')
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            None,
            2
        )
        self.assertEqual('Unknown', unknown_episode.season_number)
        self.assertEqual(2, unknown_episode.episode_number)
        self.assertEqual('', unknown_episode.episode_title)

    def test_season_unknown_no_episode_title(self):
        episode_data = next(show for show in self.data if show['episode_title'] == '')
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            2
        )
        self.assertEqual(2, unknown_episode.episode_number)
        self.assertEqual('Unknown', unknown_episode.season_number)

    def test_season_unknown_finds_recorded_episode_repeat_true(self):
        episode_data = next(show for show in self.data if show['episode_title'] == 'The Poison Sky')
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            1
        )
        self.assertEqual("4", unknown_episode.season_number)
        self.assertEqual(5, unknown_episode.episode_number)
        self.assertEqual('The Poison Sky', unknown_episode.episode_title)
        self.assertEqual(True, unknown_episode.repeat)

    def test_season_unknown_finds_recorded_episode_repeat_false(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Doctor's Daughter")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            1
        )
        self.assertEqual("4", unknown_episode.season_number)
        self.assertEqual(6, unknown_episode.episode_number)
        self.assertEqual("The Doctor's Daughter", unknown_episode.episode_title)
        self.assertEqual(False, unknown_episode.repeat)

    def test_season_unknown_finds_no_recorded_episode(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Unicorn and the Wasp")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            3
        )
        self.assertEqual("Unknown", unknown_episode.season_number)
        self.assertEqual(6, unknown_episode.episode_number)
        self.assertEqual("The Unicorn and the Wasp", unknown_episode.episode_title)
        self.assertEqual(False, unknown_episode.repeat)

    def test_get_show_splits_title_with_colon(self):
        episode_data = next(show for show in self.data if show['title'] == "Lewis: The Quality of Mercy")
        show_title, season_number, episode_number, episode_title = GuideShow.get_show(
            episode_data['title'],
            episode_data['season_number'],
            episode_data['episode_number'],
            episode_data['episode_title']
        )
        self.assertEqual('Lewis', show_title)
        self.assertEqual('Unknown', season_number)
        self.assertEqual(0, episode_number)
        self.assertEqual('The Quality of Mercy', episode_title)

    def test_get_show_splits_title_with_dash(self):
        episode_data = next(show for show in self.data if show['title'] == "Lewis - The Quality of Mercy")
        show_title, season_number, episode_number, episode_title = GuideShow.get_show(
            episode_data['title'],
            episode_data['season_number'],
            episode_data['episode_number'],
            episode_data['episode_title']
        )
        self.assertEqual('Lewis', show_title)
        self.assertEqual('Unknown', season_number)
        self.assertEqual(0, episode_number)
        self.assertEqual('The Quality of Mercy', episode_title)

    def test_get_show_splits_episode_title_with_title(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "Lewis - The Quality of Mercy")
        show_title, season_number, episode_number, episode_title = GuideShow.get_show(
            episode_data['title'],
            episode_data['season_number'],
            episode_data['episode_number'],
            episode_data['episode_title']
        )
        self.assertEqual('Lewis', show_title)
        self.assertEqual('Unknown', season_number)
        self.assertEqual(0, episode_number)
        self.assertEqual('The Quality of Mercy', episode_title)
        
    def test_finds_recorded_episode(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Doctor's Daughter")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            3
        )
        self.assertIsNotNone(unknown_episode.recorded_show)
        self.assertIsNotNone(unknown_episode.find_recorded_episode())

    def test_find_recorded_episode_throws_EpisodeNotFound(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Unicorn and the Wasp")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            3
        )
        self.assertIsNotNone(unknown_episode.recorded_show)
        self.assertRaises(EpisodeNotFoundError, unknown_episode.find_recorded_episode)

    def test_find_recorded_episode_throws_SeasonNotFound(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Eleventh Hour")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            dw_recorded_show
        )
        self.assertIsNotNone(dw_episode.recorded_show)
        self.assertRaises(SeasonNotFoundError, dw_episode.find_recorded_episode)

    def test_find_recorded_episode_throws_ShowNotFound(self):
        episode_data = next(show for show in self.data if show['title'] == "The Capture")
        recorded_show = next((show for show in self.recorded_shows if show.title == 'The Capture'), None)
        the_capture_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            recorded_show
        )
        self.assertIsNone(the_capture_episode.recorded_show)
        self.assertRaises(ShowNotFoundError, the_capture_episode.find_recorded_episode)

    def test_create_reminder_finds_no_reminder(self):
        episode_data = next(show for show in self.data if show['title'] == "The Capture")
        recorded_show = next((show for show in self.recorded_shows if show.title == 'The Capture'), None)
        the_capture_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            recorded_show
        )
        the_capture_episode.create_reminder(self.database_service)
        
        self.assertIsNone(the_capture_episode.reminder)

    def test_create_reminder_fails_interval_comparison(self):
        episode_data = next(show for show in self.data if show['title'] == "Lewis")
        recorded_show = next((show for show in self.recorded_shows if show.title == 'Lewis'), None)
        lewis_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            recorded_show
        )
        lewis_episode.create_reminder(self.database_service)
        
        self.assertIsNotNone(self.database_service.get_one_reminder(lewis_episode.title))
        self.assertIsNone(lewis_episode.reminder)

    def test_create_reminder_success(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "A Good Man Goes to War")
        recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            recorded_show
        )
        episode.create_reminder(self.database_service)

        self.assertIsNotNone(self.database_service.get_one_reminder('Doctor Who'))
        self.assertIsNotNone(episode.reminder)
        self.assertEqual(('ABC2', datetime(1900, 1, 1, 18, 29)), episode.reminder.airing_details)
        self.assertEqual(datetime(1900, 1, 1, 18, 26), episode.reminder.notify_time)

    def test_message_string_no_episode_title_not_repeat(self):
        episode_data = next(
            show for show in self.data if show['title'] == "Doctor Who" and show['season_number'] == "4" and show['episode_number'] == 8
        )
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            dw_recorded_show
        )
        self.assertEqual("22:29: Doctor Who is on ABC2 (Season 4, Episode 8)", dw_episode.message_string())

    def test_message_string_episode_title_not_repeat(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Doctor's Daughter")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            episode_data['episode_title'],
            dw_recorded_show,
            1
        )
        self.assertEqual("22:29: Doctor Who is on ABC2 (Season 4, Episode 6: The Doctor's Daughter)", dw_episode.message_string())

    def test_message_string_no_episode_title_repeat(self):
        episode_data = next(
            show for show in self.data if show['title'] == "Doctor Who" and show['season_number'] == "4" and show['episode_number'] == 9
        )
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            dw_recorded_show
        )
        self.assertEqual("22:29: Doctor Who is on ABC2 (Season 4, Episode 9) (Repeat)", dw_episode.message_string())

    def test_message_string_episode_title_repeat(self):
        episode_data = next(show for show in self.data if show['episode_title'] == "The Poison Sky")
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        dw_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], datetime.strptime(episode_data['time'], '%H:%M')),
            episode_data['episode_title'],
            dw_recorded_show,
            1
        )
        self.assertEqual("22:29: Doctor Who is on ABC2 (Season 4, Episode 5: The Poison Sky) (Repeat)", dw_episode.message_string())

    def tearDown(self):
        reminders = self.database_service.get_all_reminders()
        for reminder in reminders:
            self.database_service.delete_reminder(reminder.show)
    

if __name__ == '__main__':
    unittest.main()
