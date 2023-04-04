from __future__ import annotations
from datetime import timedelta
from exceptions.DatabaseError import ReminderNotFoundError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Reminder:

    def __init__(self, show: str, reminder_alert: str, warning_time: int, occassions: str, guide_show: 'GuideShow') -> None:
        self.show = show
        self.reminder_alert = reminder_alert
        self.warning_time = warning_time
        self.occassions = occassions
        if guide_show is not None:
            self.guide_show = guide_show
            self.notify_time = self.calculate_notification_time()

    @classmethod
    def from_values(cls, show: str, reminder_alert: str, warning_time: int, occassions: str, guide_show: 'GuideShow' = None):
        return cls(show, reminder_alert, warning_time, occassions, guide_show)

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

    def to_dict(self):
        return {
            'show': self.show,
            'reminder_alert': self.reminder_alert,
            'warning_time': self.warning_time,
            'occassions': self.occassions
        }

    def notification(self):
        return f'REMINDER: {self.show} is on {self.guide_show.channel} at {self.guide_show.time.strftime("%H:%M")}'
    
    def general_message(self):
        return f'{self.notification()}\nYou will be reminded at {self.calculate_notification_time().strftime("%H:%M")}'

    def reminder_details(self):
        return f'{self.show}\nReminder Alert: {self.reminder_alert}\nWarning Time: {self.warning_time}\nOccassions: {self.occassions}'
    
    def __repr__(self) -> str:
        return f"Reminder [Show: {self.show}, Alert: {self.reminder_alert}, Warning Time: {self.warning_time}, Occassions: {self.occassions}]"
