from datetime import datetime
from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, func, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session

from database.database import Base, engine
from database.models import GuideEpisode, ShowDetails


class ShowEpisode(Base):
    __tablename__ = 'ShowEpisode'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    show = Column('show', Text)
    season_number = Column('season_number', Integer)
    episode_number = Column('episode_number', Integer)
    episode_title = Column('episode_title', Text)
    alternative_titles = Column('alternative_titles', ARRAY(Text))
    summary = Column('summary', Text)
    channels = Column('channels', ARRAY(Text))
    air_dates = Column('air_dates', ARRAY(DateTime))
    show_id = Column('show_id', ForeignKey('ShowDetails.id'))
    show_details: Mapped['ShowDetails'] = relationship('ShowDetails', back_populates='show_episodes')
    guide_episodes: Mapped[list['GuideEpisode']] = relationship('GuideEpisode', back_populates='show_episode')

    def __init__(
        self,
        show: str,
        season_number: int,
        episode_number: int,
        episode_title: str,
        summary: str,
        alternative_titles: list[str] = [],
        channels: list[str] = [],
        air_dates: list[datetime] = [],
        show_id: int = None
    ):
        super().__init__()
        self.show = show
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.summary = summary
        self.alternative_titles = alternative_titles
        self.channels = channels
        self.air_dates = air_dates
        self.show_id = show_id

    @staticmethod
    def search_for_episode(show_title: str, season_number: int, episode_number: int, episode_title: str):
        if season_number == -1 and episode_number == 0 and episode_title == '':
            return None
        
        session = Session(engine)

        if season_number != -1 and episode_number != 0:
            query = select(ShowEpisode).where(
                ShowEpisode.show == show_title,
                ShowEpisode.season_number == season_number,
                ShowEpisode.episode_number == episode_number
            )
        else:    
            query = select(ShowEpisode).where(
                ShowEpisode.show == show_title,
                ShowEpisode.episode_title.ilike(episode_title)
            )

        show_episode = session.scalar(query)
        return show_episode
    
    @staticmethod
    def add_all_episodes(episodes: list['ShowEpisode']):
        session = Session(engine)

        session.add_all(episodes)
        session.commit()

        session.close()

    def is_latest_episode(self):
        session = Session(engine)

        season_check = session.scalar(func.max(ShowEpisode.season_number))
        episode_check = session.scalar(func.max(ShowEpisode.episode_number))
        if self.season_number > season_check:
            return True
        return self.season_number == season_check and self.episode_number > episode_check


ShowEpisode.metadata.create_all(engine, tables=[ShowEpisode.__table__])
