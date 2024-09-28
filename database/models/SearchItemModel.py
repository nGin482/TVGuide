from __future__ import annotations
from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session

from database import Base, engine
from database.models.ShowDetailsModel import ShowDetails


class SearchItem(Base):
    __tablename__ = 'SearchItem'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    show = Column('show', Text)
    search_active = Column('search_active', Boolean)
    exact_title_match = Column('exact_title_match', Boolean)
    min_season_number: Mapped[int] = Column('min_season_number', Integer)
    max_season_number = Column('max_season_number', Integer)
    ignore_titles = Column('ignore_titles', ARRAY(Text))
    ignore_seasons = Column('ignore_seasons', ARRAY(Integer))
    ignore_episodes = Column('ignore_episodes', ARRAY(Text))
    show_id = Column('show_id', ForeignKey('ShowDetails.id'))
    show_details: Mapped['ShowDetails'] = relationship('ShowDetails', back_populates='search')

    def __init__(self, show: str, exact_title_match: bool, max_seasons: int, conditions: dict = {}, show_id: int = None):
        super().__init__()
        self.show = show
        self.search_active = True
        self.exact_title_match = exact_title_match
        self.min_season_number = conditions['min_season_number'] if 'min_season_number' in conditions else 1
        self.max_season_number = conditions['max_season_number'] if 'max_season_number' in conditions else max_seasons
        self.ignore_titles = conditions['ignore_titles'] if 'ignore_titles' in conditions else []
        self.ignore_seasons = conditions['ignore_seasons'] if 'ignore_seasons' in conditions else []
        self.ignore_episodes = conditions['ignore_episodes'] if 'ignore_episodes' in conditions else []
        self.show_id = show_id

    def check_search_conditions(self, episode: dict):
        if episode['season_number'] == -1 and episode['episode_title'] == "":
            return True
        
        if episode['season_number'] == -1 and episode['episode_title'] != "":
            return episode['episode_title'] not in self.ignore_episodes
        if episode['season_number'] < self.min_season_number or episode['season_number'] > self.max_season_number:
            return False
        elif episode['season_number'] in self.ignore_seasons:
            return False
        elif episode['episode_title'] in self.ignore_episodes:
            return False
        else:
            return True
        
    def validate_conditions(self):
        if self.min_season_number > self.max_season_number:
            raise ValueError(f"Minimum season number cannot be greater than maximum season number. Received minimum '{self.min_season_number}' and maximum '{self.max_season_number}'")

    @staticmethod
    def get_all_search_items(session: Session):
        query = select(SearchItem)
        search_items = session.scalars(query)

        return [search_item for search_item in search_items]
    
    @staticmethod
    def get_active_searches(session: Session):
        query = select(SearchItem).where(SearchItem.search_active == True)
        search_items = session.scalars(query)

        return [search_item for search_item in search_items]
    
    @staticmethod
    def get_search_item(show_title: str, session: Session):
        query = select(SearchItem).where(SearchItem.show == show_title)
        search_item = session.scalar(query)

        return search_item
    
    def add_search_item(self, session: Session):
        session.add(self)
        session.commit()

    def update_search(self, field: str, value, session: Session):
        setattr(self, field, value)
        session.commit()

    def delete_search(self, session: Session):
        session.delete(self)
        session.commit()

    def conditions_string(self):
        conditions = f"Minimum Season={self.min_season_number}, Maximum Season={self.max_season_number}, "
        conditions += f"Ignore Titles={self.ignore_titles}, Ignore Seasons={self.ignore_seasons}, Ignore Episodes={self.ignore_episodes}"
        return conditions
    
    def to_dict(self):
        return {
            'show': self.show,
            'search_active': self.search_active,
            'exact_title_match': self.exact_title_match,
            'conditions': {
                'min_season_number': self.min_season_number,
                'max_season_number': self.max_season_number,
                'ignore_titles': self.ignore_titles,
                'ignore_seasons': self.ignore_seasons,
                'ignore_episodes': self.ignore_episodes
            }
        }
    
    def __repr__(self) -> str:
        search_item_string = f"ShowDetails (show={self.show}, search_active={self.search_active}, "
        search_item_string += f"exact_search={self.exact_title_match}, conditions=[{self.conditions_string()}])"
        return search_item_string
