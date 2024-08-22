from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING

from database.database import Base, engine
from database.models import Reminder, ShowDetails, ShowEpisode

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler


class GuideEpisode(Base):
    __tablename__ = "GuideEpisode"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', Text)
    channel = Column('channel', Text)
    start_time = Column('start_time', DateTime)
    end_time = Column('end_time', DateTime)
    season_number = Column('season_number', Integer)
    episode_number = Column('episode_number', Integer)
    episode_title = Column('episode_title', Text)
    repeat = Column('repeat', Boolean)
    db_event = Column('db_event', Text)
    show_id = Column('show_id', Integer, ForeignKey('ShowDetails.id'))
    episode_id = Column('episode_id', Integer, ForeignKey('ShowEpisode.id'))
    show_details: Mapped['ShowDetails'] = relationship('ShowDetails', back_populates="guide_episodes", uselist=False)
    show_episode: Mapped['ShowEpisode'] = relationship('ShowEpisode', back_populates='guide_episodes', uselist=False)

    def __init__(
        self,
        title: str,
        channel: str,
        start_time: datetime,
        end_time: datetime,
        season_number: int,
        episode_number: int,
        episode_title: str,
        show_id: int,
        episode_id: int = None,
        reminder_id: int = None
    ):
        super().__init__()
        self.title = title
        self.channel = channel
        self.start_time = start_time
        self.end_time = end_time
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.show_id = show_id
        self.episode_id = episode_id
        self.reminder_id = reminder_id

    @staticmethod
    def get_shows_for_date(date: datetime):
        session = Session(engine)

        query = select(GuideEpisode).where(GuideEpisode.start_time.date() == date)
        guide_episodes = session.scalars(query).all()

        return [guide_episode for guide_episode in guide_episodes]
    
    def add_episode(self):
        session = Session(engine, expire_on_commit=False)

        session.add(self)
        session.commit()

    def update_episode(self, field: str, value: str | int | datetime):
        session = Session(engine)

        setattr(self, field, value)
        session.commit()

        session.close()

    def delete_episode(self):
        session = Session(engine)

        session.delete(self)
        session.commit()

        session.close()

    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.start_time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel} (Season {self.season_number}, Episode {self.episode_number}'
        if self.episode_title != '':
            message += f': {self.episode_title}'
        message += ')'
        if self.repeat:
            message = f'{message} (Repeat)'

        return message
    
    def reminder_notification(self):
        return f'REMINDER: {self.title} is on {self.channel} at {self.start_time.strftime("%H:%M")}'


GuideEpisode.metadata.create_all(engine, tables=[GuideEpisode.__table__])