import unittest
import json

from database.models.GuideShow import GuideShow


class TestGuide(unittest.TestCase):

    def setUp(self):
        print('hello')
        with open('tests/test_data/test_guide_list.json') as fd:
            self.data = json.load(fd)

    @unittest.skip('Test not yet set')
    def test_get_show(self):
        pass

    def test_season_known(self):
        dw_episode = self.data[0]
        known_episode = GuideShow.known_season(
            dw_episode['title'],
            (dw_episode['channel'], dw_episode['time']),
            (dw_episode['season_number'], dw_episode['episode_number'], dw_episode['episode_title']),
            None
        )
        self.assertEqual('Doctor Who', known_episode.title)
        self.assertEqual('ABC2', known_episode.channel)


if __name__ == '__main__':
    unittest.main()
