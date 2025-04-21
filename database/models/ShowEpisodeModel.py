from datetime import datetime
from sqlalchemy import (
    any_,
    ARRAY,
    Column,
    DateTime,
    ForeignKey,
    func,
    Integer,
    literal,
    or_,
    select,
    Text,
)
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING

from database import Base
from data_validation.validation import Validation

if TYPE_CHECKING:
    from database.models.GuideEpisode import GuideEpisode
    from database.models.ShowDetailsModel import ShowDetails
    from utils.types.models import TShowEpisode



class ShowEpisode(Base):
    __tablename__ = 'ShowEpisode'

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    show: Mapped[str] = Column('show', Text)
    season_number: Mapped[int] = Column('season_number', Integer)
    episode_number: Mapped[int] = Column('episode_number', Integer)
    episode_title: Mapped[str] = Column('episode_title', Text)
    alternative_titles: Mapped[list[str]] = Column('alternative_titles', ARRAY(Text))
    summary: Mapped[str] = Column('summary', Text)
    channels: Mapped[list[str]] = Column('channels', ARRAY(Text))
    air_dates: Mapped[list[datetime]] = Column('air_dates', ARRAY(DateTime))
    show_id: Mapped[int] = Column('show_id', ForeignKey('ShowDetails.id'))
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
    def get_episode_by_id(episode_id: int, session: Session):
        query = select(ShowEpisode).where(ShowEpisode.id == episode_id)

        episode = session.scalar(query)
        return episode
    
    @staticmethod
    def search_for_episode(
        show_title: str,
        season_number: int,
        episode_number: int,
        episode_title: str,
        session: Session
    ):
        if season_number == -1 and episode_number == 0 and episode_title == '':
            return None
        
        if season_number != -1 and episode_number != 0:
            query = select(ShowEpisode).where(
                ShowEpisode.show == show_title,
                ShowEpisode.season_number == season_number,
                ShowEpisode.episode_number == episode_number
            )
        else:
            query = select(ShowEpisode).where(
                ShowEpisode.show == show_title,
                or_(
                    ShowEpisode.episode_title.ilike(episode_title),
                    literal(episode_title).like(any_(ShowEpisode.alternative_titles))
                )
            )

        show_episode = session.scalar(query)
        return show_episode

    @staticmethod
    def get_episodes_by_season(show_title: str, season_number: int, session: Session):
        query = select(ShowEpisode).where(ShowEpisode.show == show_title, ShowEpisode.season_number == season_number)

        episodes = session.scalars(query)
        
        return [episode for episode in episodes]
    
    @staticmethod
    def add_all_episodes(episodes: list['ShowEpisode'], session: Session):
        session.add_all(episodes)
        session.commit()

    def add_episode(self, session: Session):
        session.add(self)
        session.commit()

    def update_full_episode(self, episode_details: dict, session: Session):
        for key in episode_details.keys():
            setattr(self, key, episode_details[key])
        session.commit()

    def delete_episode(self, session: Session):
        session.delete(self)
        session.commit()

    def is_latest_episode(self, session: Session):
        season_check = session.scalar(func.max(ShowEpisode.season_number))
        episode_check = session.scalar(func.max(ShowEpisode.episode_number))
        if self.season_number > season_check:
            return True
        return self.season_number == season_check and self.episode_number >= episode_check
    
    def channel_check(self, channel: str):
        """Check that the given episode is present in the episode's channel list. Return True if present, False if not.\n
        If `ABC1` is present, also check `ABCHD`.\n
        If `SBS` is present, also check `SBSHD`.\n
        If `10` is present, also check `TENHD`.\n"""

        if 'ABC1' in self.channels and 'ABCHD' not in self.channels:
            return False
        if 'SBS' in self.channels and 'SBSHD' not in self.channels:
            return False
        if '10' in self.channels and 'TENHD' not in self.channels:
            return False
        if channel not in self.channels:
            return False
        return True
    
    def add_channel(self, channel: str):
        """Add the given channel to the episode's channel list.\n
        If the channel is `ABC1`, `ABCHD` will also be added.\n
        If the channel is `TEN`, `TENHD` will also be added.\n
        If the channel is `SBS`, `SBSHD` will also be added.\n"""
        if channel not in self.channels:
            self.channels.append(channel)
        if ('ABC1' in channel or 'ABC1' in self.channels) and 'ABCHD' not in self.channels:
            self.channels.append('ABCHD')
            return f'{channel} and ABCHD have been added to the channel list.'
        elif (('TEN' in channel or '10' in channel) or ('10' in self.channels or 'TEN' in self.channels)) and 'TENHD' not in self.channels:
            self.channels.append('TENHD')
            return f'{channel} and TENHD have been added to the channel list.'
        elif ('SBS' in channel or 'SBS' in self.channels) and 'SBSHD' not in self.channels:
            self.channels.append('SBSHD')
            return f'{channel} and SBSHD have been added to the channel list.'
        else:
            return f'{channel} has been added to the channel list.'
        
    def add_air_date(self, air_date: datetime = None):
        date = Validation.get_current_date() if air_date is None else air_date
        self.air_dates.append(date)

    def to_dict(self) -> TShowEpisode:
        return {
            'id': self.id,
            'show': self.show,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'summary': self.summary,
            'alternative_titles': self.alternative_titles,
            'channels': self.channels,
            'air_dates': self.air_dates
        }
    
    def __repr__(self) -> str:
        return f"ShowEpisode [show={self.show}, season_number={self.season_number}, episode_number={self.episode_number}]"
