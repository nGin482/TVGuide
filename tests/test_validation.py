from datetime import datetime
import unittest
import json

from aux_methods.helper_methods import sbs_episode_format
from data_validation.validation import Validation

class TestValidation(unittest.TestCase):

    def setUp(self):
        with open('tests/test_data/validation_test_data.json') as fd:
            self.data = json.load(fd)
    
    def test_format_episode_title(self):
        episode_data = next(show for show in self.data if show['title'] == 'Test Episode Title - The')
        formatted_episode_title = Validation.format_episode_title(episode_data['episode_title'])
        self.assertEqual('The Black Spot', formatted_episode_title)

        episode_data = next(show for show in self.data if show['title'] == 'Test Episode Title - A')
        formatted_episode_title = Validation.format_episode_title(episode_data['episode_title'])
        self.assertEqual('A Black Spot', formatted_episode_title)

    def test_check_show_title(self):
        maigret_data = next(show for show in self.data if show['title'] == 'Maigret In Montmartre')
        maigret_show = Validation.check_show_titles(maigret_data['title'])
        self.assertEqual('Maigret', maigret_show)

        dip_data = next(show for show in self.data if show['title'] == 'Death in Paradise')
        death_in_paradise = Validation.check_show_titles(dip_data['title'])
        self.assertEqual('Death In Paradise', death_in_paradise)

        grantchester_data = next(show for show in self.data if show['title'] == 'Grantchester Christmas Special')
        grantchester = Validation.check_show_titles(grantchester_data['title'])
        self.assertEqual('Grantchester', grantchester)        

    def test_sbs_episode_format_returns_season_episode_number(self):
        sbs_data = next((show for show in self.data if show['title'] == 'Litvinenko'), None)
        season_number, episode_number = sbs_episode_format(sbs_data['title'], sbs_data['episode_title'])
        
        self.assertEqual(season_number, 1)
        self.assertEqual(episode_number, 1)

    def test_sbs_episode_format_fails(self):
        sbs_data = next((show for show in self.data if show['title'] == 'Litvinenko'), None)
        sbs_data['episode_title'] = 'Series 1 Ep 1'
        result = sbs_episode_format(sbs_data['title'], sbs_data['episode_title'])
        
        self.assertEqual(result, 'Series 1 Ep 1')
