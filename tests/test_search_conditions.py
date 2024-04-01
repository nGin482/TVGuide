
from dotenv import load_dotenv
import unittest
import json
import os

from database.DatabaseService import DatabaseService
from database.models.SearchItem import SearchItem


class TestSearchConditions(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        load_dotenv('.env.local.test')
        os.environ['PYTHON_ENV'] = 'testing'

        self.database_service = DatabaseService(os.getenv('TVGUIDE_DB'), 'test')

        with open('tests/test_data/search_list.json') as fd:
            search_list = json.load(fd)
        search_list = [SearchItem(
            search_list_doc['show'],
            search_list_doc['image'],
            search_list_doc['conditions'],
            search_list_doc['search_active']
        ) for search_list_doc in search_list]

        self.database_service.search_list_collection.insert_many([search_item.to_dict() for search_item in search_list])

        with open('tests/test_data/test_guide_list.json') as fd:
            self.guide_list: list[dict] = json.load(fd)

        self.search_list = self.database_service.get_search_list()

    def test_exact_search(self):
        lewis_guide_show = next(show for show in self.guide_list if show['title'] == 'Lewis')
        lewisham_alley_guide_show = next(show for show in self.guide_list if show['title'] == 'Lewisham Alley')
        lewis_search_item = next(show for show in self.search_list if show.show == 'Lewis')
        
        lewis_exact_search_check = lewis_search_item.check_search_conditions(lewis_guide_show)
        lewisham_alley_exact_search_check = lewis_search_item.check_search_conditions(lewisham_alley_guide_show)

        self.assertTrue(lewis_exact_search_check)
        self.assertFalse(lewisham_alley_exact_search_check)

    def test_exclude_show_titles(self):
        ncis_guide_show = next(show for show in self.guide_list if show['title'] == 'NCIS')
        ncis_new_orleans_guide_show = next(show for show in self.guide_list if show['title'] == 'NCIS: New Orleans')
        ncis_search_item = next(show for show in self.search_list if show.show == 'NCIS')

        ncis_title_exclusion_check = ncis_search_item.check_search_conditions(ncis_guide_show)
        ncis_new_orleans_title_exclusion_check = ncis_search_item.check_search_conditions(ncis_new_orleans_guide_show)
        
        self.assertTrue(ncis_title_exclusion_check)
        self.assertFalse(ncis_new_orleans_title_exclusion_check)

    def test_min_season(self):
        death_in_paradise_guide_shows = [show for show in self.guide_list if show['title'] == 'Death in Paradise']
        death_in_paradise_search_item = next(show for show in self.search_list if show.show == 'Death in Paradise')

        dip_min_season_check_excluded = death_in_paradise_search_item.check_search_conditions(death_in_paradise_guide_shows[0])
        dip_min_season_check_included = death_in_paradise_search_item.check_search_conditions(death_in_paradise_guide_shows[1])

        self.assertFalse(dip_min_season_check_excluded)
        self.assertTrue(dip_min_season_check_included)

    def test_max_season(self):
        doctor_who_guide_shows = [show for show in self.guide_list if show['title'] == 'Doctor Who']
        doctor_who_search_item = next(show for show in self.search_list if show.show == 'Doctor Who')

        dw_max_season_check_excluded = doctor_who_search_item.check_search_conditions(doctor_who_guide_shows[-1])
        dw_max_season_check_included = doctor_who_search_item.check_search_conditions(doctor_who_guide_shows[-2])

        self.assertFalse(dw_max_season_check_excluded)
        self.assertTrue(dw_max_season_check_included)

    def test_only_season(self):
        tfa_guide_shows = [show for show in self.guide_list if show['title'] == 'Transformers: Animated' and show['season_number'] in [1, 2]]
        tfa_search_item = next(show for show in self.search_list if show.show == 'Transformers')

        self.assertTrue(tfa_search_item.check_search_conditions(tfa_guide_shows[0]))
        self.assertFalse(tfa_search_item.check_search_conditions(tfa_guide_shows[1]))


    def test_season_range(self):
        vera_guide_shows = [show for show in self.guide_list if show['title'] == 'Vera' and show['season_number'] in [1, 3, 4, 6]]
        vera_search_item = next(show for show in self.search_list if show.show == 'Vera')

        vera_in_range = vera_search_item.check_search_conditions(vera_guide_shows[0])
        vera_min_boundary = vera_search_item.check_search_conditions(vera_guide_shows[1])
        vera_max_boundary = vera_search_item.check_search_conditions(vera_guide_shows[2])
        vera_out_range = vera_search_item.check_search_conditions(vera_guide_shows[3])

        self.assertTrue(vera_in_range)
        self.assertTrue(vera_min_boundary)
        self.assertTrue(vera_max_boundary)
        self.assertFalse(vera_out_range)

    def test_search_active(self):
        maigret_guide_show = next(show for show in self.guide_list if show['title'] == 'Maigret')
        maigret_search_item = next(show for show in self.search_list if show.show == 'Maigret')

        search_active_check = maigret_search_item.check_search_conditions(maigret_guide_show)

        self.assertFalse(search_active_check)


    def tearDown(self) -> None:
        super().tearDown()
        self.database_service.search_list_collection.delete_many({})

        
