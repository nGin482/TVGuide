from datetime import datetime
from data_validation.validation import Validation
from database.models.GuideShowCases import TransformersGuideShow, DoctorWho, MorseGuideShow, RedElection, SilentWitness
from database.models.RecordedShow import Episode, RecordedShow, Season
from exceptions.DatabaseError import DatabaseError, EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError
from log import log_imdb_api_results, logging_app
import requests
import logging
import os


class GuideShow:
    shows_with_unknown_season: dict = {}
    
    def __init__(self, title: str, channel: str, time: datetime, episode_info: bool, season_number: str, episode_number: int, episode_title: str, recorded_show: RecordedShow) -> None:
        self._episode_number_updated = False
        
        self.recorded_show = recorded_show
        episode_data = GuideShow.get_show(title, season_number, episode_title)
        if isinstance(episode_data, tuple) and len(episode_data) > 1:
            title = episode_data[0]
            episode_info = episode_data[1]
            season_number = episode_data[2]
            episode_number = episode_data[3]
            episode_title = episode_data[4]        
        

        if season_number == '':
            season_number = 'Unknown'
        
        self.title = Validation.check_show_titles(title)
        self.channel = channel
        self.time = time
        self.episode_info = episode_info
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = Validation.format_episode_title(episode_title)
        self.repeat = False

    @staticmethod
    def get_show(title: str, season_number, episode_title) -> tuple:
        if 'Transformers' in title or 'Bumblebee' in title:
            return TransformersGuideShow.handle(title)
        elif 'Doctor Who' in title:
            return DoctorWho.handle(title)
        elif 'Morse' in title:
            return MorseGuideShow.handle(title)
        elif 'Red Election' in title:
            return RedElection.handle(title, season_number, episode_title)
        elif 'Silent Witness' in title:
            return SilentWitness.handle(season_number, episode_title)
        else:
            return Validation.check_show_titles(title)

    def update_show_details(self):
        if self.season_number == 'Unknown' and self.episode_title != '':
            check_existing_episode = self.recorded_show.find_episode_by_episode_title(self.episode_title)
            if check_existing_episode:
                self.season_number = check_existing_episode[0]
                self.episode_number = check_existing_episode[1]
                unknown_season = self.recorded_show.find_season('Unknown')
                if unknown_season:
                    episode_in_unknown_season = unknown_season.find_episode(episode_title=self.episode_title)
                    if episode_in_unknown_season:
                        episode_in_unknown_season.remove_unknown_episode(self.title)
                        unknown_season.episodes.remove(episode_in_unknown_season)

    def verify_episode_number(self, shows_list: list['GuideShow']):
        """
        Update the `episode_number`, taking into account the number of shows matching the `title` with `season_number == 'Unknown'`
        Takes a filtered list of `GuideShow` objects based on the show's title and if `season_number == 'Unknown'`
        """
        index = None
        for idx, guide_show in enumerate(shows_list):
            if self.episode_title == guide_show.episode_title:
                index = idx
                break
        self.episode_number = self.recorded_show.find_number_of_unknown_episodes() + index + 1

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
            season = self.recorded_show.find_season(self.season_number)
            if season:
                episode = season.find_episode(episode_number=self.episode_number, episode_title=self.episode_title)
                if episode:
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
                channel_add = episode.add_channel(self.channel)
            if not episode.repeat:
                episode.repeat = True
                set_repeat = 'The episode has been marked as a repeat.'
            episode.latest_air_date = datetime.today()
            print(f'{self.title} happening on channel/repeat')
            episode.update_episode_in_database(self.title, self.season_number)
            return {'show': self.to_dict(), 'repeat': set_repeat, 'channel': channel_add}
        except EpisodeNotFoundError as err:
            try:
                season = self.recorded_show.find_season(self.season_number)
                new_episode = Episode.from_guide_show(self)
                season.episodes.append(new_episode)
                season.add_episode_to_season(self.title, new_episode)
                add_episode_status = f'{new_episode} has been added to {season.season_number}'
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
            try:
                insert_show = recorded_show.insert_new_recorded_show_document()
            except DatabaseError as err:
                insert_show = str(err)
            print(f'{self.title} happening on show')
            return {'show': self.to_dict(), 'result': insert_show}
        except Exception as err:
            return {'show': self.to_dict(), 'message': 'Unable to process this episode.', 'error': str(err)}

    def search_imdb_information(self):
        if (self.season_number != 'Unknown' and self.episode_number != 0 and self.episode_title != '') or 'HD' in self.channel:
            return self

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
        return self.message_string()[:-1]

    def __eq__(self, other: 'GuideShow') -> bool:
        return self.title == other.title and self.channel == other.channel and self.time == self.time

    def __hash__(self) -> int:
        return hash((self.title, self.channel, self.time))

