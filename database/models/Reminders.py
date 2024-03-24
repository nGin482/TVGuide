from __future__ import annotations
from datetime import datetime, timedelta

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.GuideShow import GuideShow

class Reminder:

    def __init__(self, show: str, reminder_alert: str, warning_time: int, occasions: str) -> None:
        self.show = show
        self.reminder_alert = reminder_alert
        self.warning_time = warning_time
        self.occasions = occasions
        self.notify_time: datetime = None
        self.airing_details: tuple[str, datetime] = ()

    @classmethod
    def from_values(cls, title: str, reminder_alert: str, warning_time: int, occasions: str):
        return cls(title, reminder_alert, warning_time, occasions)

    @classmethod
    def from_database(cls, reminder_data: dict):
        """
        Raises `ReminderNotFoundError` if the reminder document for the given show could not be found.
        """
        show_title: str = reminder_data['show']
        reminder_alert: str = reminder_data['reminder_alert']
        warning_time: int = reminder_data['warning_time']
        occasions: str = reminder_data['occasions']
        return cls(show_title, reminder_alert, warning_time, occasions)

    def compare_reminder_interval(self, guide_show: GuideShow):
        if self.occasions == 'All':
            # send message
            # print(f'REMINDER: {self.show} is on {self.guide_show.channel} at {self.guide_show.time.strftime("%H:%M")}')
            return True
        elif self.occasions == 'Latest':
            latest_season = guide_show.recorded_show.find_latest_season()
            print(latest_season)
            if guide_show.season_number >= latest_season.season_number:
                latest_episode = max(int(episode.episode_number) for episode in latest_season.episodes)
                if guide_show.episode_number > latest_episode:
                    # print(f'REMINDER: {self.show} is on {self.guide_show.channel} at {self.guide_show.time.strftime("%H:%M")}')
                    return True
        elif self.occasions == 'Once':
            return False
        else:
            return False

    def calculate_notification_time(self):
        if self.reminder_alert == 'On-Start':
            self.notify_time = self.airing_details[1]
        elif self.reminder_alert == 'After':
            self.notify_time = self.airing_details[1] + timedelta(minutes=self.warning_time)
        else:
            self.notify_time = self.airing_details[1] - timedelta(minutes=self.warning_time)

    def to_dict(self):
        return {
            'show': self.show,
            'reminder_alert': self.reminder_alert,
            'warning_time': self.warning_time,
            'occasions': self.occasions
        }

    def notification(self):
        return f'REMINDER: {self.show} is on {self.airing_details[0]} at {self.airing_details[1].strftime("%H:%M")}'
    
    def general_message(self):
        return f'{self.notification()}\nYou will be reminded at {self.notify_time.strftime("%H:%M")}'

    def reminder_details(self):
        return f'{self.show}\nReminder Alert: {self.reminder_alert}\nWarning Time: {self.warning_time}\noccasions: {self.occasions}'
    
    def __repr__(self) -> str:
        return f"Reminder [Show: {self.show}, Alert: {self.reminder_alert}, Warning Time: {self.warning_time}, occasions: {self.occasions}]"
