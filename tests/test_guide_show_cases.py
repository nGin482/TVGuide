import unittest
import json

from database.models.GuideShow import GuideShow

class TestGuideShowCases(unittest.TestCase):

    def setUp(self) -> None:
        with open('tests/test_data/test_guide_list.json') as fd:
            self.data = json.load(fd)
    
    def test_get_transformers_1_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Transformers')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(1, episode_number)
        self.assertEqual('Transformers', episode_title)

    def test_get_transformers_2_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Transformers: Revenge of the Fallen')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(2, episode_number)
        self.assertEqual('Revenge of the Fallen', episode_title)

    def test_get_transformers_3_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Transformers: Dark of the Moon')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(3, episode_number)
        self.assertEqual('Dark of the Moon', episode_title)

    def test_get_transformers_4_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Transformers: Age of Extinction')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(4, episode_number)
        self.assertEqual('Age of Extinction', episode_title)

    def test_get_transformers_5_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Transformers: The Last Knight')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(5, episode_number)
        self.assertEqual('The Last Knight', episode_title)

    def test_get_bumblebee_movie(self):
        transformers_data = next(show for show in self.data if show['title'] == 'Bumblebee')
        title, season_number, episode_number, episode_title = GuideShow.get_show(
            transformers_data['title'],
            transformers_data['season_number'],
            transformers_data['episode_number'],
            transformers_data['episode_title']
        )
        self.assertEqual('Transformers', title)
        self.assertEqual('1', season_number)
        self.assertEqual(6, episode_number)
        self.assertEqual('Bumblebee', episode_title)

    @unittest.skip('Test not yet set')
    def test_get_doctor_who_show(self):
        pass