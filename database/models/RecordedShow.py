from datetime import datetime
from .GuideShow import GuideShow
import json

class Episode:
    episode_number: int
    episode_title: str
    channels: list[str]
    first_air_date: datetime
    latest_air_date: datetime
    repeat: bool

    def __init__(self, episode_subdocument: dict = {}, show: GuideShow = None) -> None:
        if len(episode_subdocument.keys()) != 0 and show is None:
            self.episode_number = episode_subdocument['episode number']
            self.episode_title = episode_subdocument['episode title']
            self.channels = episode_subdocument['channels']
            self.first_air_date = episode_subdocument['first air date']
            self.latest_air_date = datetime.today().strftime('%d/%M/%Y')
            self.repeat = episode_subdocument['repeat']
        elif len(episode_subdocument.keys()) == 0 and show is not None:
            self.episode_number = show.episode_number
            self.episode_title = show.episode_title
            self.channels = [show.channel]
            self.first_air_date = datetime.today().strftime('%d/%M/%Y')
            self.latest_air_date = datetime.today().strftime('%d/%M/%Y')
            self.repeat = show.repeat
        else:
            raise ValueError('Please provide details about the episode recorded')

    def update_latest_air_date(self):
        self.latest_air_date = datetime.today().strftime('%d/%M/%Y')
    
    def to_dict(self):
        if type(self.first_air_date) is not str:
            first_air_date = self.first_air_date.strftime('%d/%M/%Y')
        if type(self.latest_air_date) is not str:
            latest_air_date = self.latest_air_date.strftime('%d/%M/%Y')
        
        return {
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'channels': self.channels,
            'first_air_date': first_air_date,
            'latest_air_date': latest_air_date,
            'repeat': self.repeat
        }


class Season:
    season_number: int
    episodes: list[Episode]

    def __init__(self, season_subdocument: dict = {}, show: GuideShow = None) -> None:
        if len(season_subdocument.keys()) != 0 and show is None:
            self.season_number = season_subdocument['season number']
            self.episodes = [Episode(episode_subdocument=episode) for episode in season_subdocument['episodes']]
        elif len(season_subdocument.keys()) == 0 and show is not None:
            self.season_number = show.season_number
            self.episodes = [Episode(show=show)]
        else:
            raise ValueError('Please provide information about the season')

    def find_episode(self, episode_number: int, episode_title: str) -> Episode:
        if episode_number != 0:
            results = list(filter(lambda episode_obj: episode_obj.episode_number == str(episode_number), self.episodes))
        else:
            results = list(filter(lambda episode_obj: episode_obj.episode_title == episode_title, self.episodes))
        print(results)
        if len(results) > 0:
            return results[0]
        return None

    def add_episode(self, episode: Episode):
        self.episodes.append(episode)
    
    def to_dict(self):
        season_dict = {
            'season_number': self.season_number,
            'episodes': []
        }
        episode: Episode
        for episode in self.episodes:
            season_dict['episodes'].append(episode.to_dict())
        
        return season_dict




class RecordedShow:
    title: str
    seasons: list[Season]

    def __init__(self, recorded_show_details: dict = {}, guide_show: GuideShow = None) -> None:
        # self._id = recorded_show_details['_id']
        if guide_show is None and len(recorded_show_details.keys) != 0:
            self.title = recorded_show_details['show']
            self.seasons = [Season(season) for season in recorded_show_details['seasons']]
        elif guide_show and len(recorded_show_details.keys) == 0:
            self.title = guide_show.title
            self.seasons = [Season(show=guide_show)]
        else:
            raise ValueError('Please provide details about the show recorded')
    
    def find_season(self, season_number) -> Season:
        results = list(filter(lambda season_obj: season_obj.season_number == season_number, self.seasons))
        if len(results) > 0:
            return results[0]
        return None

    def add_season(self, season: Season):
        self.seasons.append(season)

    def create_JSON_file(self):
        try:
            with open(f'shows/{self.title}.json', 'w+') as fd:
                json.dump(self, fd, indent='\t')
            return True
        except FileExistsError:
            return False

    def update_JSON_file(self):
        try:
            with open(f'shows/{self.title}.json', 'w') as fd:
                json.dump(self.to_dict(), fd, indent='\t')
            return True
        except FileNotFoundError:
            return False
    
    def to_dict(self) -> dict:
        show_dict = {
            '_id': self._id,
            'title': self.title,
            'seasons': []
        }
        season: Season
        for season in self.seasons:
            show_dict['seasons'].append(season)