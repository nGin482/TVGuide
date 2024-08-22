from sqlalchemy import Column, ForeignKey, Integer, select, Text
from sqlalchemy.orm import Mapped, relationship, Session
from datetime import datetime, timedelta

from database.database import Base, engine
from database.models import GuideEpisode, ShowDetails


class Reminder(Base):
    __tablename__ = 'Reminder'
    
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    show = Column('show', Text)
    alert = Column('alert', Text)
    warning_time = Column('warning_time', Integer)
    occasions = Column('occasions', Text)
    show_id = Column('show_id', Integer, ForeignKey('ShowDetails.id'))
    show_details: Mapped['ShowDetails'] = relationship('ShowDetails', back_populates='reminder', uselist=False)
    guide_episodes: Mapped[list['GuideEpisode']] = relationship('GuideEpisode', back_populates='reminder')

    def __init__(self, show: str, alert: str, warning_time: int, occasions: str, show_id: int = None):
        super().__init__()
        self.show = show
        self.alert = alert
        self.warning_time = warning_time
        self.occasions = occasions
        self.notify_time: datetime = None
        self.show_id = show_id

    @staticmethod
    def get_all_reminders():
        session = Session(engine)

        query = select(Reminder)
        reminders = session.scalars(query).all()
        
        return [reminder for reminder in reminders]
    
    @staticmethod
    def get_reminder_by_show(title: str):
        session = Session(engine)

        query = select(Reminder).where(Reminder.show == title)
        reminder = session.scalar(query)

        return reminder
    
    def add_reminder(self):
        session = Session(engine)

        session.add(self)
        session.commit()

        session.close()

    def update_reminder(self, field, value):
        session = Session(engine)

        setattr(self, field, value)
        session.commit()

        session.close()

    def delete_reminder(self):
        session = Session(engine)

        session.delete(self)
        session.commit()

        session.commit()

Reminder.metadata.create_all(engine, tables=[Reminder.__table__])
