from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session
from typing import TYPE_CHECKING
import logging

from database import Base
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from database.models import Reminder, ShowDetails, ShowEpisode


class GuideEpisode(Base):
    __tablename__ = "GuideEpisode"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    guide_id: Mapped[int] = Column('guide_id', Integer, ForeignKey('Guide.id'))
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
    reminder_id = Column('reminder_id', Integer, ForeignKey('Reminder.id'))
    show_details: Mapped['ShowDetails'] = relationship('ShowDetails', back_populates="guide_episodes", uselist=False)
    show_episode: Mapped['ShowEpisode'] = relationship('ShowEpisode', back_populates='guide_episodes', uselist=False)
    reminder: Mapped['Reminder'] = relationship('Reminder', back_populates='guide_episodes', uselist=False)

    logger = logging.getLogger("GuideEpisode")
    logger.setLevel(logging.DEBUG)

    def __init__(
        self,
        title: str,
        channel: str,
        start_time: datetime,
        end_time: datetime,
        season_number: int,
        episode_number: int,
        episode_title: str,
        guide_id: int,
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
        self.guide_id = guide_id
        self.show_id = show_id
        self.episode_id = episode_id
        self.reminder_id = reminder_id

    @staticmethod
    def get_shows_for_date(date: datetime, session: Session):
        end_date = date + timedelta(days=1)

        query = select(GuideEpisode).where(GuideEpisode.start_time.between(date, end_date))
        guide_episodes = session.scalars(query)

        return [guide_episode for guide_episode in guide_episodes]
    
    def add_episode(self, session: Session):
        session.add(self)
        session.commit()

    def update_episode(self, field: str, value: str | int | datetime, session: Session):
        setattr(self, field, value)
        session.commit()

    def delete_episode(self, session: Session):
        session.delete(self)
        session.commit()

    def check_repeat(self, session: Session):
        if self.show_episode:
            self.repeat = len(self.show_episode.air_dates) > 0
        else:
            self.repeat = False
        session.commit()

    def capture_db_event(self, session: Session):

        def create_show_details():
            show_details = ShowDetails(
                self.title,
                '',
                '',
                [],
                ''
            )
            show_details.add_show(session)
            return show_details
        def create_show_episode():
            show_episode = ShowEpisode(
                self.title,
                self.season_number,
                self.episode_number,
                self.episode_title,
                '',
                [],
                [self.channel],
                [self.start_time],
                self.show_details.id
            )
            show_episode.add_episode(session)
            return show_episode

        from sqlalchemy import insert, update
        if self.show_episode and self.show_details:
            events = {}

            air_dates = self.show_episode.air_dates
            air_dates.append(self.start_time)
            events["air_dates"] = air_dates

            episode_details = f"""Season {self.season_number} Episode {self.episode_number} ({self.episode_title})"""
            self.db_event = f"{episode_details} has aired today"
            if not self.show_episode.channel_check(self.channel):
                self.show_episode.channels.append(self.channel)
                events["channels"] = self.show_episode.channels
                self.db_event = self.show_episode.add_channel(self.channel)
            statement = update(ShowEpisode).where(ShowEpisode.id == self.episode_id).values(events)
        elif self.show_details is None and self.show_episode is None:
            self.show_details = create_show_details()
            self.show_episode = create_show_episode()
            
            show_details_insert_values = self.show_details.to_dict()
            del show_details_insert_values['id']
            show_episode_insert_values = self.show_episode.to_dict()
            del show_episode_insert_values['id']

            show_details_statement = insert(ShowDetails).values(show_details_insert_values)
            statement = insert(ShowEpisode).values(show_episode_insert_values)

            session.execute(show_details_statement)
            self.db_event = "This show is now being recorded"
        elif self.show_episode is None and self.show_details is not None:
            self.show_episode = create_show_episode()

            show_episode_insert_values = self.show_episode.to_dict()
            del show_episode_insert_values['id']
            
            statement = insert(ShowEpisode).values(show_episode_insert_values)
            
            episode_details = f"Season {self.season_number} Episode {self.episode_number} ({self.episode_title})"
            self.db_event = f"{episode_details} has been inserted"
        else:
            self.show_details = create_show_details()

            show_details_insert_values = self.show_details.to_dict()
            del show_details_insert_values['id']

            statement = insert(ShowDetails).values(show_details_insert_values)
            self.db_event = "This show is now being recorded"

        session.execute(statement)
        session.commit()

    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.start_time.strftime('%H:%M')
        season_number = 'Unknown' if self.season_number == -1 else self.season_number
        message = f'{time}: {self.title} is on {self.channel} (Season {season_number}, Episode {self.episode_number}'
        if self.episode_title != '':
            message += f': {self.episode_title}'
        message += ')'
        if self.repeat:
            message = f'{message} (Repeat)'

        return message
    
    def reminder_notification(self):
        return f'REMINDER: {self.title} is on {self.channel} at {self.start_time.strftime("%H:%M")}'
    
    def reminder_message(self, notify_time: datetime):
        return f"{self.reminder_notification()}.\nYou will be reminded at {notify_time.strftime('%H:%M')}"
    
    def __repr__(self) -> str:
        season_number = 'Unknown' if self.season_number == -1 else self.season_number
        return (
            f"GuideEpisode (show={self.title}, channel={self.channel}, time={self.start_time}-{self.end_time}, "
            f"season number={season_number}, episode number={self.episode_number}, episode title={self.episode_title}, "
            f"repeat={self.repeat})"
        )

    def to_dict(self):
        return {
            'title': self.title,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'channel': self.channel,
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat,
            'db_event': self.db_event
        }

