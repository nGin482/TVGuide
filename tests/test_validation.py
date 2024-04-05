from datetime import datetime
import unittest
import json

from aux_methods.helper_methods import sbs_episode_format
from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from data_validation.validation import Validation


class TestValidation(unittest.TestCase):

    def setUp(self):
        with open('tests/test_data/validation_test_data.json') as fd:
            self.data = json.load(fd)
        with open('tests/test_data/recorded_shows.json') as fd:
            temp_data = json.load(fd)
            self.recorded_shows: list['RecordedShow'] = []
            for recorded_show in temp_data:
                self.recorded_shows.append(RecordedShow.from_database(recorded_show))
    
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

    def test_get_unknown_episode_number_no_recorded_show(self):
        "Test handling for unknown episode numbers without recorded shows"
        
        shows_on: list['GuideShow'] = []
        episode_numbers = []
        for show in self.data:
            if show['season_number'] == 'Unknown':
                episode_number = Validation.get_unknown_episode_number(self.data, show['title'], show['episode_title'])
                if episode_number is None:
                    episode_number = 1
                guide_show = GuideShow.unknown_season(
                    show['title'],
                    (show['channel'], datetime.strptime(show['time'], '%H:%M')),
                    show['episode_title'],
                    None,
                    episode_number
                )
                shows_on.append(guide_show)
                episode_numbers.append(episode_number)

        self.assertEqual(1, episode_numbers[0])
        self.assertEqual(2, episode_numbers[1])
        self.assertEqual(3, episode_numbers[2])
        self.assertEqual(1, shows_on[0].episode_number)
        self.assertEqual(2, shows_on[1].episode_number)
        self.assertEqual(3, shows_on[2].episode_number)
        
        self.assertEqual(1, episode_numbers[3])
        self.assertEqual(2, episode_numbers[4])
        self.assertEqual(3, episode_numbers[5])
        self.assertEqual(1, shows_on[3].episode_number)
        self.assertEqual(2, shows_on[4].episode_number)
        self.assertEqual(3, shows_on[5].episode_number)


    def test_get_unknown_episode_number_recorded_show(self):
        ncis_data = next((show for show in self.recorded_shows if show.title == 'NCIS'), None)
        shows_on: list['GuideShow'] = []
        episode_numbers = []
        for show in self.data:
            if show['season_number'] == 'Unknown':
                episode_number = Validation.get_unknown_episode_number(self.data, show['title'], show['episode_title'])
                if episode_number is None:
                    episode_number = 1
                guide_show = GuideShow.unknown_season(
                    show['title'],
                    (show['channel'], datetime.strptime(show['time'], '%H:%M')),
                    show['episode_title'],
                    ncis_data,
                    episode_number
                )
                shows_on.append(guide_show)
                episode_numbers.append(episode_number)

        self.assertEqual(1, episode_numbers[0])
        self.assertEqual(2, episode_numbers[1])
        self.assertEqual(3, episode_numbers[2])
        self.assertEqual(4, shows_on[0].episode_number)
        self.assertEqual(5, shows_on[1].episode_number)
        self.assertEqual(6, shows_on[2].episode_number)

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
