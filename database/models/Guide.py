from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from database.models.GuideShow import GuideShow
from data_validation.validation import Validation
if TYPE_CHECKING:
    from database.DatabaseService import DatabaseService


class Guide:

    def __init__(self, date: str, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]) -> None:
        
        self.date = datetime.strptime(date, '%d/%m/%Y')
        self.fta_shows = fta_shows
        self.bbc_shows = bbc_shows

    @classmethod
    def from_database(cls, guide_details: dict, database_service: DatabaseService = None):
        fta_list = []
        datetime_stamp = datetime.strptime(guide_details['date'], '%d/%m/%Y')

        fta_list = Guide.create_guide_shows(guide_details['FTA'], database_service, datetime_stamp)
        bbc_list = Guide.create_guide_shows(guide_details['BBC'], database_service, datetime_stamp)

        return cls(guide_details['date'], fta_list, bbc_list)

    @classmethod
    def from_runtime(cls, fta_shows: list[GuideShow], bbc_shows: list[GuideShow], date: datetime = None):
        guide_date = date if date is not None else Validation.get_current_date()
        return cls(guide_date.strftime('%d/%m/%Y'), fta_shows, bbc_shows)
    
    @staticmethod
    def create_guide_shows(show_list: list[dict], database_service: DatabaseService, datetime_stamp: datetime):
        guide_show_list: list[GuideShow] = []
        for show in show_list:
            time = show['time'].split(':')
            datetime_stamp = datetime_stamp.replace(hour=int(time[0]), minute=int(time[1]))
            if show['season_number'] != 'Unknown':
                guide_show = GuideShow.known_season(
                    show['title'],
                    (show['channel'], datetime_stamp),
                    (show['season_number'], show['episode_number'], show['episode_title']),
                    database_service.get_one_recorded_show(show['title'])
                )
                guide_show.db_event = show['event']
            else:
                guide_show = GuideShow.unknown_season(
                    show['title'],
                    (show['channel'], datetime_stamp),
                    show['episode_title'],
                    database_service.get_one_recorded_show(show['title']),
                    show['episode_number']
                )
                guide_show.db_event = show['event']
            guide_show_list.append(guide_show)
        return guide_show_list

    def search_for_show(self, show_title):
        return [show for show in self.fta_shows if show_title in show.title]


    def to_dict(self):
        return {
            'date': self.date.strftime('%d/%m/%Y'),
            'FTA': [show.to_dict() for show in self.fta_shows],
            'BBC': [show.to_dict() for show in self.bbc_shows]
        }