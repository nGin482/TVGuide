import unittest

from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from database.mongo import mongo_client
from guide import search_free_to_air

class TestGuide(unittest.TestCase):


    def setUp(self) -> None:
        self.database_service = DatabaseService(mongo_client().get_database('tvguide'))
        return super().setUp()

    def test_search_free_to_air():
        dw_episode = {
            'title': 'Doctor Who: The Power of the Doctor',
            'channel': 'ABC2',
            'time': '10:30',
            'season_number': '',
            'episode_number': 0,
            'episode_title': ''
        }

    def test_today_data():
        pass
