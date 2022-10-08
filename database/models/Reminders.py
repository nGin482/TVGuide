from __future__ import annotations
from datetime import datetime, timedelta
from pymongo import ReturnDocument
from exceptions.DatabaseError import DatabaseError, ReminderNotFoundError
from database.mongo import database

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Reminder:
    reminders_collection = database().get_collection('Reminders')

    def __init__(self, show: str, reminder_alert: str, warning_time: int, occassions: str, guide_show: 'GuideShow') -> None:
        self.show = show
        self.reminder_alert = reminder_alert
        self.warning_time = warning_time
        self.occassions = occassions
        if guide_show is not None:
            self.guide_show = guide_show
            self.notify_time = self.calculate_notification_time()

    @classmethod
    def from_values(cls, show: 'GuideShow', reminder_alert: str, warning_time: int, occassions: str):
        return cls(show.title, reminder_alert, warning_time, occassions, show)

    @classmethod
    def from_database(cls, reminder_data: dict, show: 'GuideShow' = None):
        """
        Raises `ReminderNotFoundError` if the reminder document for the given show could not be found.
        """
        show_title: str = reminder_data['show']
        reminder_alert: str = reminder_data['reminder_alert']
        warning_time: int = reminder_data['warning_time']
        occassions: str = reminder_data['occassions']
        return cls(show_title, reminder_alert, warning_time, occassions, show)

    @staticmethod
    def _get_database_data(show_name: str):
        reminders_collection = database().get_collection('Reminders')
        reminder: dict = reminders_collection.find_one({'show': show_name})
        if not reminder:
            raise ReminderNotFoundError(f'The reminder document for {show_name} could not be found in the Database')
        return reminder

    def compare_reminder_interval(self):
        if self.occassions == 'All':
            # send message
            # print(f'REMINDER: {self.show} is on {self.guide_show.channel} at {self.guide_show.time.strftime("%H:%M")}')
            return True
        elif self.occassions == 'Latest':
            latest_season = self.guide_show.recorded_show.find_latest_season()
            print(latest_season)
            if self.guide_show.season_number >= latest_season.season_number:
                latest_episode = max(int(episode.episode_number) for episode in latest_season.episodes)
                if self.guide_show.episode_number > latest_episode:
                    # print(f'REMINDER: {self.show} is on {self.guide_show.channel} at {self.guide_show.time.strftime("%H:%M")}')
                    return True
        elif self.occassions == 'Once':
            return False
        else:
            return False

    def calculate_notification_time(self):
        if self.reminder_alert == 'On-Start':
            return self.guide_show.time
        elif self.reminder_alert == 'After':
            return self.guide_show.time + timedelta(minutes=self.warning_time)
        else:
            return self.guide_show.time - timedelta(minutes=self.warning_time)

    @staticmethod
    def get_reminders_for_shows(show_list: list['GuideShow']):
        reminder_list: list[Reminder] = []
        for show in show_list:
            try:
                reminder = Reminder.from_database(show)
                reminder_list.append(reminder)
            except ReminderNotFoundError:
                pass
        return reminder_list

    def insert_reminder_document(self):
        inserted_document = Reminder.reminders_collection.insert_one(self.to_dict())
        if not inserted_document.inserted_id:
            raise DatabaseError(f'The Reminder document for {self.show} was not inserted into the Reminders collection')
        return True

    def delete_reminder(self):
        """Delete a `Reminder` from the MongoDB collection.\n
        Raises an `exceptions.DatabaseError` if the reminder document could not be found."""
        reminder_deleted: dict = Reminder.reminders_collection.find_one_and_delete(
            {'show': self.show}
        )
        if len(reminder_deleted.keys()) == 0 or not reminder_deleted:
            raise DatabaseError(f'The reminder for {self.show} could not be found')
        return True
    
    def to_dict(self):
        return {
            'show': self.show,
            'reminder_alert': self.reminder_alert,
            'warning_time': self.warning_time,
            'occassions': self.occassions
        }
    
    def __repr__(self) -> str:
        return f"Reminder [Show: {self.show}, Alert: {self.reminder_alert}, Warning Time: {self.warning_time}, Occassions: {self.occassions}]"
