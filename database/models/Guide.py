from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.DatabaseService import DatabaseService

from database.models.GuideShow import GuideShow

class Guide:

    def __init__(self, date: str, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]) -> None:
        
        self.date = datetime.strptime(date, '%d/%m/%Y')
        self.fta_shows = fta_shows
        self.bbc_shows = bbc_shows

    @classmethod
    def from_database(cls, guide_details: dict, database_service: DatabaseService = None):
        fta_list = []
        datetime_stamp = datetime.strptime(guide_details['date'], '%d/%m/%Y')
        for show in guide_details['FTA']:
            time = show['time'].split(':')
            datetime_stamp = datetime_stamp.replace(hour=int(time[0]), minute=int(time[1]))
            if show['season_number'] != 'Unknown':
                guide_show = GuideShow.known_season(
                    show['title'],
                    (show['channel'], datetime_stamp),
                    (show['season_number'], show['episode_number'], show['episode_title']),
                    database_service.get_one_recorded_show(show['title'])
                )
            else:
                guide_show = GuideShow.unknown_season(
                    show['title'],
                    (show['channel'], datetime_stamp),
                    show['episode_title'],
                    database_service.get_one_recorded_show(show['title']),
                    show['episode_number']
                )
            fta_list.append(guide_show)

        return cls(guide_details['date'], fta_list, [])

    @classmethod
    def from_runtime(cls, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]):
        return cls(datetime.today().strftime('%d/%m/%Y'), fta_shows, bbc_shows)

    def search_for_show(self, show_title):
        return [show for show in self.fta_shows if show_title in show.title]


    def to_dict(self):
        return {
            'date': self.date.strftime('%d/%m/%Y'),
            'FTA': [show.to_dict() for show in self.fta_shows],
            'BBC': [show.to_dict() for show in self.bbc_shows]
        }