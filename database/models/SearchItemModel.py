from __future__ import annotations
from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session

from database.database import Base, engine
from database.models import ShowDetails


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

    def __init__(self, show: str, exact_title_match: bool, conditions: dict = {}, show_id: int = None):
        super().__init__()
        self.show = show
        self.search_active = True
        self.exact_title_match = exact_title_match
        self.min_season_number = conditions['min_season_number'] if 'min_season_number' in conditions else 1
        self.max_season_number = conditions['max_season_number'] if 'max_season_number' in conditions else 10
        self.ignore_titles = conditions['ignore_titles'] if 'ignore_titles' in conditions else []
        self.ignore_seasons = conditions['ignore_seasons'] if 'ignore_seasons' in conditions else []
        self.ignore_episodes = conditions['ignore_episodes'] if 'ignore_episodes' in conditions else []
        self.show_id = show_id

    @staticmethod
    def get_all_search_items():
        session = Session(engine)

        query = select(SearchItem)
        search_items = session.scalars(query)

        return [search_item for search_item in search_items]
    
    @staticmethod
    def get_active_searches():
        session = Session(engine)

        query = select(SearchItem).where(SearchItem.search_active == True)
        search_items = session.scalars(query)

        return [search_item for search_item in search_items]
    
    def add_search_item(self):
        session = Session(engine)

        session.add(self)
        session.commit()

        session.close()

    def update_search(self, field: str, value):
        session = Session(engine)

        setattr(self, field, value)
        session.commit()

        session.close()

    def delete_search(self):
        session = Session(engine)

        session.delete(self)
        session.commit()

        session.close()

    def conditions_string(self):
        conditions = f"Minimum Season={self.min_season_number}, Maximum Season={self.max_season_number}, "
        conditions += f"Ignore Titles={self.ignore_titles}, Ignore Seasons={self.ignore_seasons}, Ignore Episodes={self.ignore_episodes}"
        return conditions
    
    def __repr__(self) -> str:
        search_item_string = f"ShowDetails (show={self.show}, search_active={self.search_active}, "
        search_item_string += f"exact_search={self.exact_title_match}, conditions=[{self.conditions_string()}])"
        return search_item_string

SearchItem.metadata.create_all(engine, tables=[SearchItem.__table__])
