from datetime import datetime

from data_validation.validation import Validation
from database.models.GuideShowCases import TransformersGuideShow, DoctorWho, MorseGuideShow, RedElection, SilentWitness
from database.models.RecordedShow import RecordedShow
from exceptions.DatabaseError import EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError
# from services.imdb_api import search_for_episode_title, search_for_season_number

class GuideShow:
    
    def __init__(self, title: str, airing_details: tuple[str, datetime], episode_details: tuple[str, int, str, bool], recorded_show: RecordedShow, new_show: bool = False) -> None:
        channel, time = airing_details
        season_number, episode_number, episode_title, repeat = episode_details
        
        self.title = title
        self.channel = channel
        self.time = time
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.repeat = repeat
        self.recorded_show = recorded_show
        self.db_event = 'No DB event was performed on this show.'
        self.new_show = new_show

    @classmethod
    def known_season(cls, title: str, airing_details: tuple[str, datetime], episode_details: tuple[str, int, str], recorded_show: RecordedShow):
        season_number, episode_number, episode_title = episode_details
        repeat = False
        new_show = False
        
        if recorded_show is not None:
            season = recorded_show.find_season(season_number)
            if season is not None:
                if episode_number != 0:
                    episode = season.find_episode(episode_number=episode_number)
                else:
                    episode = season.find_episode(episode_title=episode_title)
                if episode_title == "":
                    episode_title = episode.episode_title
                if episode.is_repeat() or len(episode.air_dates) == 1:
                    repeat = True
        else:
            new_show = True
        
        return cls(title, airing_details, (season_number, episode_number, episode_title, repeat), recorded_show, new_show)

    @classmethod
    def unknown_season(cls, title: str, airing_details: tuple[str, datetime], episode_title: str, recorded_show: RecordedShow, unknown_episodes: int):
        repeat = False
        new_show = False
        season_number = 'Unknown'

        if recorded_show is None:
            new_show = True
            episode_number = unknown_episodes
        elif episode_title == "":
            episode_number = 1 if unknown_episodes == 0 else unknown_episodes
        else:
            episode_search = recorded_show.find_episode_instances(episode_title)
            if episode_search is None:
                if recorded_show.find_season('Unknown') is not None:
                    unknown_season_episodes = max(episode.episode_number for episode in recorded_show.find_season('Unknown').episodes)
                else:
                    unknown_season_episodes = 0
                episode_number = 1 if unknown_season_episodes + unknown_episodes == 0 else unknown_season_episodes + unknown_episodes
            else:
                season_number, episode = episode_search
                episode_number = episode.episode_number
                if episode.is_repeat() or len(episode.air_dates) == 1:
                    repeat = True
        
        return cls(title, airing_details, (season_number, episode_number, episode_title, repeat), recorded_show, new_show)

    @staticmethod
    def get_show(title: str, season_number: str, episode_number: int, episode_title: str):
        if 'Transformers' in title or 'Bumblebee' in title:
            handle_result = TransformersGuideShow.handle(title)
            if isinstance(handle_result, str):
                return handle_result, season_number, episode_number, episode_title
            return handle_result
        elif 'Doctor Who' in title:
            handle_result = DoctorWho.handle(title, episode_title)
            if isinstance(handle_result, str):
                return handle_result, season_number, episode_number, episode_title
            return handle_result
        elif 'Morse' in title:
            return MorseGuideShow.handle(title)
        elif 'Red Election' in title:
            return RedElection.handle(title, episode_title)
        elif 'Silent Witness' in title:
            return SilentWitness.handle(episode_title)
        elif 'NCIS Encore' in title:
            return 'NCIS', season_number, episode_number, episode_title
        else:
            return Validation.check_show_titles(title), season_number, episode_number, episode_title

    def find_recorded_episode(self):
        """
        Checks the local files in the `shows` directory for information about a `GuideShow`'s information\n
        Raises `EpisodeNotFoundError` if the episode can't be found in the database.\n
        Raises `SeasonNotFoundError` if the season can't be found in the database.\n
        Raises `ShowNotFoundError` if the show can't be found in the database.
        """
        # check_show = get_one_recorded_show(show['title'])
        if self.recorded_show or not self.new_show:
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

    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel}'
        message += f' (Season {self.season_number}, Episode {self.episode_number}'
        if self.episode_title != '':
            message += f': {self.episode_title}'
        message += ')'
        if self.repeat:
            message = f'{message} (Repeat)'

        return message

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'channel': self.channel,
            'time': self.time.strftime('%H:%M'),
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat,
            'event': self.db_event
        }

    def __repr__(self) -> str:
        return self.message_string()

    def __eq__(self, other: 'GuideShow') -> bool:
        return self.title == other.title and self.channel == other.channel and self.time == self.time

    def __hash__(self) -> int:
        return hash((self.title, self.channel, self.time))

