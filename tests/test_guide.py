import unittest
import json

from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow


class TestGuide(unittest.TestCase):

    def setUp(self):
        with open('tests/test_data/test_guide_list.json') as fd:
            self.data = json.load(fd)
        with open('tests/test_data/recorded_shows.json') as fd:
            temp_data = json.load(fd)
            self.recorded_shows: list['RecordedShow'] = []
            for recorded_show in temp_data:
                self.recorded_shows.append(RecordedShow.from_database(recorded_show))

    def test_season_known_repeat_true(self):
        dw_episode = self.data[0]
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        known_episode = GuideShow.known_season(
            dw_episode['title'],
            (dw_episode['channel'], dw_episode['time']),
            (dw_episode['season_number'], dw_episode['episode_number'], dw_episode['episode_title']),
            dw_recorded_show
        )
        self.assertEqual(True, known_episode.repeat)

    def test_season_known_repeat_false(self):
        episode_data = next(show for show in self.data if show['episode_title'] == 'A Good Man Goes to War')
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        known_episode = GuideShow.known_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            (episode_data['season_number'], episode_data['episode_number'], episode_data['episode_title']),
            dw_recorded_show
        )
        self.assertEqual(False, known_episode.repeat)

    def test_season_unknown_no_details(self):
        episode_data = next(show for show in self.data if show['episode_title'] == '')
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            None,
            2
        )
        self.assertEqual(2, unknown_episode.episode_number)
        self.assertEqual('Unknown', unknown_episode.season_number)

    def test_season_unknown_no_details_2(self):
        episode_data = next(show for show in self.data if show['episode_title'] == '')
        dw_recorded_show = next((show for show in self.recorded_shows if show.title == 'Doctor Who'), None)
        unknown_episode = GuideShow.unknown_season(
            episode_data['title'],
            (episode_data['channel'], episode_data['time']),
            episode_data['episode_title'],
            dw_recorded_show,
            2
        )
        self.assertEqual(5, unknown_episode.episode_number)
        self.assertEqual('Unknown', unknown_episode.season_number)



if __name__ == '__main__':
    unittest.main()