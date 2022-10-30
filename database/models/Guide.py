from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Guide:

    def __init__(self, date: str, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]) -> None:
        
        self.date = datetime.strptime(date, '%d/%m/%Y')
        self.fta_shows = fta_shows
        self.bbc_shows = bbc_shows

    @classmethod
    def from_database(cls, guide_details: dict):
        return cls(guide_details['date'], guide_details['FTA'], guide_details['BBC'])

    @classmethod
    def from_runtime(cls, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]):
        return cls(datetime.today().strftime('%d/%m/%Y'), fta_shows, bbc_shows)

    def search_for_show(self, show_title):
        return [show for show in self.fta_shows if show_title in show.title]


    def to_dict(self):
        return {
            'date': datetime.today().strftime('%d/%m/%Y'),
            'FTA': [show.to_dict() for show in self.fta_shows],
            'BBC': [show.to_dict() for show in self.bbc_shows]
        }