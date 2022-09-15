from abc import ABC, abstractmethod
from datetime import datetime
from data_validation.validation import Validation
from .RecordedShow import RecordedShow, Season
from exceptions.DatabaseError import DatabaseError, EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError
from log import log_imdb_api_results, logging_app
import requests
import logging
import json
import os


class GuideShow:
    
    def __init__(self, title: str, channel: str, time: datetime, episode_info: bool, season_number: str, episode_number: int, episode_title: str, recorded_show: RecordedShow) -> None:
        self.recorded_show = recorded_show
        episode_data = GuideShow.get_show(title, season_number, episode_title)
        if isinstance(episode_data, tuple):
            title = episode_data[0]
            episode_info = episode_data[1]
            season_number = episode_data[2]
            episode_number = episode_data[3]
            episode_title = episode_data[4]
        else:
            title = episode_data

        if season_number == '':
            season_number = 'Unknown'
            episode_number = recorded_show.find_number_of_unknown_episodes() + 1
        
        self.title = title
        self.channel = channel
        self.time = time
        self.episode_info = episode_info
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = Validation.format_title(episode_title)
        self.repeat = self.search_for_repeats()

    @staticmethod
    def get_show(title: str, season_number, episode_title) -> tuple:
        if 'Transformers' in title:
            return TransformersGuideShow.handle(title)
        elif 'Doctor Who' in title:
            return DoctorWho.handle(title)
        elif 'Morse' in title:
            return MorseGuideShow.handle(title)
        elif 'Red Election' in title:
            return RedElection.handle(title, season_number, episode_title)
        elif 'Silent Witness' in title:
            return SilentWitness.handle(season_number, '', episode_title)
        else:
            return Validation.check_show_titles(title)

    def search_for_repeats(self) -> bool:

        if self.episode_info:
            try:
                episode = self.find_recorded_episode()
                if episode:
                    return True
            except (EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError):
                return False
        return False

    def find_recorded_episode(self):
        """
        Checks the local files in the `shows` directory for information about a `GuideShow`'s information\n
        Raises `EpisodeNotFoundError` if the episode can't be found in the database.\n
        Raises `SeasonNotFoundError` if the season can't be found in the database.\n
        Raises `ShowNotFoundError` if the show can't be found in the database.
        """
        # check_show = get_one_recorded_show(show['title'])
        if self.recorded_show:
            season_number = self.season_number
            if season_number == '':
                season_number = 'Unknown'
            season = self.recorded_show.find_season(season_number)
            if season:
                episode = season.find_episode(episode_number=self.episode_number, episode_title=self.episode_title)
                if episode:
                    # if show.season_number != '' and show.episode_number != 0 and season.season_number == 'Unknown':
                        # document_updated = update_recorded_episode(show)['status']
                        # if document_updated:
                        #     print(f"The document for {show['title']} was updated") # TODO: most likely will log this
                    return episode
                else:
                    raise EpisodeNotFoundError
            else:
                raise SeasonNotFoundError
        else:
            raise ShowNotFoundError

    def capture_db_event(self):
        
        try:
            episode = self.find_recorded_episode()
            set_repeat = 'Repeat status is up to date'
            channel_add = 'Channel list is up to date'
            if self.channel not in episode.channels:
                episode.channels.append(self.channel)
                channel_add = f'{self.channel} has been added to the channel list.'
                self.recorded_show.update_JSON_file()
            if not episode.repeat:
                episode.repeat = True
                set_repeat = 'The episode has been marked as a repeat.'
                self.recorded_show.update_JSON_file()
            episode.latest_air_date = datetime.today()
            print(f'{self.title} happening on channel/repeat')
            episode.update_episode_in_database(self.title, self.season_number)
            return {'show': self.to_dict(), 'repeat': set_repeat, 'channel': channel_add}
        except EpisodeNotFoundError as err:
            try:
                add_episode_status = self.recorded_show.add_episode_to_document(self)
            except DatabaseError as err:
                add_episode_status = str(err)
            print(f'{self.title} happening on episode')
            return {'show': self.to_dict(), 'result': add_episode_status}
        except SeasonNotFoundError as err:
            new_season = Season.from_guide_show(self)
            try:
                insert_season = self.recorded_show.add_season(new_season)
            except DatabaseError as err:
                insert_season = str(err)
            print(f'{self.title} happening on season')
            return {'show': self.to_dict(), 'result': insert_season}
        except ShowNotFoundError as err:
            recorded_show = RecordedShow.from_guide_show(self)
            recorded_show.create_JSON_file()
            try:
                insert_show = recorded_show.insert_new_recorded_show_document()
            except DatabaseError as err:
                insert_show = str(err)
            print(f'{self.title} happening on show')
            return {'show': self.to_dict(), 'result': insert_show}
        except Exception as err:
            return {'show': self.to_dict(), 'message': 'Unable to process this episode.', 'error': str(err)}

    def search_imdb_information(self):
        if self.season_number != 'Unknown' and self.episode_number != 0 and self.episode_title != '':
            return self
        if self.season_number == '':
            print(f"{self.title}'s season number empty before searching IMDB API")

        imdb_api_key = os.getenv('IMDB_API')
        results = []
        # get season number and episode number from episode title
        if self.season_number == 'Unknown' and self.episode_title != '':
            log_message = f"Searching IMDB API with {self.title}'s episode title ({self.episode_title}) to retrieve season number and episode number"
            logging_app(log_message, logging.INFO)
            episode_title = self.episode_title.replace(' ', '%20') if ' ' in self.episode_title else self.episode_title
            
            episode_req = requests.get(f'https://imdb-api.com/en/API/SearchEpisode/{imdb_api_key}/{episode_title}')
            
            if episode_req.status_code == 200:
                results: list[dict] = episode_req.json()['results']
                title = 'Death in Paradise' if 'Death In Paradise' in self.title else self.title
                if results:
                    for result in results:
                        if title in result['description'] and self.episode_title.lower() == result['title'].lower():
                            print(result['description'])
                            description = GuideShow._extract_information(result['description'])
                            self.season_number = description[0]
                            self.episode_number = int(description[1])
                        if self.season_number == '':
                            self.season_number = "Unknown"
                            print(f"{self.title}'s season number empty after searching IMDB API")
                else:
                    print(f"IMDB API returned None when looking up {self.title}'s {self.episode_title} episode")
        
        # get episode title from season number and episode number
        if self.episode_title == '' and self.season_number != 'Unknown':
            log_message = f"Searching IMDB API with {self.title}'s season number ({self.season_number}) to retrieve episode title"
            logging_app(log_message, logging.INFO)
            show_id = self.recorded_show.imdb_id
            if show_id:
                season_req = requests.get(f'https://imdb-api.com/en/API/SeasonEpisodes/{imdb_api_key}/{show_id}/{self.season_number}')
                if season_req.status_code == 200:
                    episodes = season_req.json()['episodes']
                    results = episodes
                    for episode in episodes:
                        if episode['episodeNumber'] == str(self.episode_number):
                            self.episode_title = episode['title']
        log_imdb_api_results(self.to_dict(), results)
        return self

    @staticmethod
    def _extract_information(description: str) -> tuple:
        """
        Given a description from an IMDB API result, search this string for information regarding season number and episode number
        """

        desc_break = description.split('|')
        
        season_index = desc_break[0].index('Season ')+7
        season = desc_break[0][season_index:len(desc_break[0])-1]
        
        episode:str = desc_break[1][9:desc_break[1].index('-')-1]
        
        return season, episode
    
    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel}'
        if self.season_number != '' and self.episode_number != '':
            message += f' (Season {self.season_number}, Episode {self.episode_number}'
            if self.episode_title != '':
                message += f': {self.episode_title}'
            message += ')\n'
        else:
            message += f' ({self.episode_title})\n'
        if self.repeat:
            message = message[:-1] + ' (Repeat)\n'

        return message

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'channel': self.channel,
            'time': self.time.strftime('%H:%M'),
            'episode_info': self.episode_info,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat
        }

    def __repr__(self) -> str:
        return self.message_string()

    def __eq__(self, other: 'GuideShow') -> bool:
        return self.title == other.title and self.channel == other.channel and self.time == self.time


class SpecialCases(ABC):

    @abstractmethod
    def handle():
        pass

class TransformersGuideShow(SpecialCases):

    @staticmethod
    def handle(title: str):
        check_transformers = TransformersGuideShow.transformers_shows(title)
        if isinstance(check_transformers, tuple):
            if 'Bumblebee' in title:
                title = 'Transformers'
            return 'Transformers', True, str(check_transformers[0]), check_transformers[1], check_transformers[2]
        return ()

    @staticmethod
    def transformers_shows(transformers: str) -> tuple:
        if 'Fallen' in transformers:
            return 1, 2, 'Revenge of the Fallen'
        elif 'Dark' in transformers:
            return 1, 3, 'Dark of the Moon'
        elif 'Extinction' in transformers:
            return 1, 4, 'Age of Extinction'
        elif 'Knight' in transformers:
            return 1, 5, 'The Last Knight'
        elif 'Bumblebee' in transformers:
            return 1, 6, 'Bumblebee'
        elif transformers == 'Transformers':
            return 1, 1, 'Transformers'
        else:
            return transformers

class DoctorWho(SpecialCases):
    @staticmethod
    def handle(title: str) -> tuple[str, bool, str, int, str] | tuple:
        if title != 'Doctor Who':
            from log import logging_app
            logging_app(title)
            
            check_dw_title: tuple = DoctorWho.doctor_who_episodes(title)
            return 'Doctor Who', True, str(check_dw_title[0]), check_dw_title[1], check_dw_title[2]
        return ()
    
    @staticmethod
    def doctor_who_episodes(title: str) -> tuple:
        """
        Given an episode's title, return the `season number`, `episode number` and correct `episode title` of a Doctor Who episode
        """
        tennant_specials = ['The Next Doctor', 'Planet of the Dead', 'The Waters of Mars', 'The End of Time - Part 1', 'The End of Time - Part 2']
        smith_specials = ['The Snowmen', 'The Day of the Doctor', 'The Time of the Doctor']

        if 'Doctor Who: ' in title:
            title = title.split(': ')[1]
        
        for idx, tennant_special in enumerate(tennant_specials):
            if title.lower() in tennant_special.lower():
                return 'Tennant Specials', idx+1, tennant_special
        for idx, smith_special in enumerate(smith_specials):
            if title.lower() in smith_special.lower():
                return 'Smith Specials', idx+1, smith_special
        
        if 'Christmas Invasion' in title:
            return 2, 0, 'The Christmas Invasion'
        elif 'Runaway Bride' in title:
            return 3, 0, 'The Runaway Bride'
        elif 'Voyage Of The Damned' in title:
            return 4, 0, 'Voyage of the Damned'
        elif 'Christmas Carol' in title:
            return 6, 0, 'A Christmas Carol'
        elif 'Wardrobe' in title:
            return 7, 0, 'The Doctor, the Widow and the Wardrobe'
        elif 'Last Christmas' in title:
            return 9, 0, 'Last Christmas'
        elif 'Husbands Of River Song' in title:
            return 9, 13, 'The Husbands of River Song'
        elif 'Return Of Doctor Mysterio' in title:
            return 10, 0, 'The Return of Doctor Mysterio'
        elif 'Twice Upon A Time' in title:
            return 10, 13, 'Twice Upon a Time'
        elif 'Resolution' in title:
            return 11, 11, 'Resolution'
        elif 'Revolution Of The Daleks' in title:
            return 12, 11, 'Revolution of the Daleks'
        elif 'Eve of the Daleks' in title or 'Eve Of The Daleks' in title:
            return 13, 7, 'Eve of the Daleks'
        else:
            return title

class MorseGuideShow(SpecialCases):

    @staticmethod
    def handle(title: str):
        titles = title.split(': ')
        episode = MorseGuideShow.morse_episodes(titles[1])
        
        return 'Inspector Morse', True, str(episode[0]), episode[1], episode[2]

    @staticmethod
    def morse_episodes(guide_title: str) -> tuple:
        """
        Given an episode's title, return the `season number`, `episode number` and correct `episode title` of an Inspector Morse episode
        """

        morse_titles = [
            {'Episodes': ['The Dead Of Jericho', 'The Silent World Of Nicholas Quinn', 'Service Of All The Dead']},
            {'Episodes':
                ['The Wolvercote Tongue', 'Last Seen Wearing', 'The Settling Of The Sun', 'Last Bus To Woodstock']},
            {'Episodes': ['Ghost In The Machine', 'The Last Enemy', 'Deceived By Flight', 'The Secret Of Bay 5B']},
            {'Episodes': ['The Infernal Spirit', 'The Sins Of The Fathers', 'Driven To Distraction',
                        'The Masonic Mysteries']},
            {'Episodes':
                ['Second Time Around', 'Fat Chance', 'Who Killed Harry Field?', 'Greeks Bearing Gifts', 'Promised Land']},
            {'Episodes': ['Dead On Time', 'Happy Families', 'The Death Of The Self', 'Absolute Conviction',
                        'Cherubim And Seraphim']},
            {'Episodes': ['Deadly Slumber', 'The Day Of The Devil', 'Twilight Of The Gods']},
            {'Episodes': ['The Way Through The Woods', 'The Daughters Of Cain', 'Death Is Now My Neighbour',
                        'The Wench Is Dead', 'The Remorseful Day']}]

        if 'Service Of All' in guide_title:
            return 1, 3, 'Service Of All The Dead'
        if 'Infernal Spirit' in guide_title:
            return 4, 1, 'The Infernal Serpent'
        if 'In Australia' in guide_title:
            return 5, 4, 'Promised Land'
        if 'Death Is' in guide_title:
            return 8, 3, 'Death Is Now My Neighbour'
        else:
            for season_idx, season in enumerate(morse_titles):
                for episode_idx, title in enumerate(season['Episodes']):
                    if 'The' in guide_title and 'The' not in title:
                        title = 'The ' + title
                    if guide_title in title:
                        return season_idx+1, episode_idx+1, title

class RedElection(SpecialCases):

    def handle(title: str, season_number: str, episode_title: str):
        from log import logging_app
        logging_app(f'Logging Red Election Episode\nSeason Number: {season_number}\nEpisode title: {episode_title}')
        
        episode_details = title[title.find('Series'):]
        
        episode_detail_values = episode_details.split(' ')
        return 'Red Election', True, episode_detail_values[1], episode_detail_values[3], ''

class SilentWitness(SpecialCases):
    
    @staticmethod
    def handle(season_number: str, episode_number: int, episode_title: str):
        episode_data = SilentWitness.silent_witness(season_number, episode_number, episode_title)
        return episode_data

    @staticmethod
    def silent_witness(season_number: str, episode_number: int, episode_title: str):
        check_episode = SilentWitness.check_silent_witness(episode_title)
        from log import logging_app
        logging_app(f'Logging Silent Witness Episode\nSeason Number: {season_number}\nEpisode Number: {episode_number}\nEpisode Title: {episode_number}\nResult: {str(check_episode)}')
        
        if season_number == '24':
            return 'Silent Witness', True, season_number, episode_number, episode_title
        else:
            print(f'Episode title: {episode_title}')

        if check_episode:
            return check_episode
        else:
            return False

    def check_silent_witness(episode_title: str):
        season_24_episodes = {
            'Redemption': ["Redemption Part 1", "Redemption Part 2"],
            'Bad Love': ["Bad Love Part 1", "Bad Love Part 2"],
            'Reputations': ["Reputations Part 1", "Reputations Part 2"],
            "Brother's Keeper": ["Brother's Keeper Part 1", "Brother's Keeper Part 2"],
            'Matters of Life and Death': ["Matters of Life and Death Part 1", "Matters of Life and Death Part 2"]
        }

        silent_witness_story = None
        index = -1

        for idx, key in enumerate(season_24_episodes.keys()):
            if key in episode_title:
                silent_witness_story = season_24_episodes[key]
                index = idx
                break

        if silent_witness_story:
            if 'Part' in episode_title:
                if 'One' in episode_title:
                    episode_title = episode_title.replace('One', '1')
                if 'Two' in episode_title:
                    episode_title = episode_title.replace('Two', '2')
                episode_part_num = [char for char in episode_title if char.isdigit()][0]
                episode_part_num = int(episode_part_num)
                episode_number = (index * 2) + episode_part_num
                return 'Silent Witness', True, '24', episode_number, episode_title
            else:
                raise ValueError('Unable to understand this Silent Witness episode')
        else:
            raise ValueError('This episode is not in Season 24')