from datetime import date, datetime
from timeit import repeat


class Episode:
    episode_number: int
    episode_title: str
    channels: list[str]
    first_air_date: datetime
    latest_air_date: datetime
    repeat: bool

    def __init__(self, episode_details: dict) -> None:
        self.episode_number = episode_details['episode number']
        self.episode_title = episode_details['episode title']
        self.channels = episode_details['channels']
        self.first_air_date = episode_details['first air date']
        self.repeat = episode_details['repeat']

    def to_dict(self):
        return {
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'channels': self.channels,
            'first_air_date': self.first_air_date,
            # 'latest_air_date': self.latest_air_date,
            'repeat': self.repeat
        }


class Season:
    season_number: int
    episodes: list[Episode]

    def __init__(self, season_details: dict) -> None:
        self.season_number = season_details['season number']
        self.episodes = season_details['episodes']
        self.episodes = [Episode(episode) for episode in self.episodes]

    def find_episode(self, episode_number: int, episode_title: str) -> Episode:
        if episode_number != 0:
            results = list(filter(lambda episode_obj: episode_obj.episode_number == str(episode_number), self.episodes))
        else:
            results = list(filter(lambda episode_obj: episode_obj.episode_title == episode_title, self.episodes))
        print(results)
        if len(results) > 0:
            return results[0]
        return None
    
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

    def __init__(self, recorded_show_details: dict) -> None:
        # self._id = recorded_show_details['_id']
        self.title = recorded_show_details['show']
        self.seasons = [Season(season) for season in recorded_show_details['seasons']]
        # TODO: Initialise seasons
    
    def find_season(self, season_number) -> Season:
        results = list(filter(lambda season_obj: season_obj.season_number == season_number, self.seasons))
        if len(results) > 0:
            return results[0]
        return None


    def to_dict(self) -> dict:
        show_dict = {
            '_id': self._id,
            'title': self.title,
            'seasons': []
        }
        season: Season
        for season in self.seasons:
            show_dict['seasons'].append(season)