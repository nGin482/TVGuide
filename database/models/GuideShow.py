from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from data_validation.validation import Validation
from database.models.GuideShowCases import TransformersGuideShow
from exceptions.DatabaseError import EpisodeNotFoundError, SeasonNotFoundError, ShowNotFoundError

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from database.DatabaseService import DatabaseService
    from database.models.RecordedShow import RecordedShow
    from database.models.Reminders import Reminder

class GuideShow:
    
    def __init__(self, title: str, airing_details: tuple[str, datetime], episode_details: tuple[str, int, str, bool], recorded_show: RecordedShow, new_show: bool = False) -> None:
        channel, time = airing_details
        season_number, episode_number, episode_title, repeat = episode_details
        
        self.title = title
        self.channel = channel
        self.time = time
        self.season_number = season_number
        self.episode_number = episode_number
        self.episode_title = episode_title
        self.repeat = repeat
        self.recorded_show = recorded_show
        self.reminder: Reminder = None
        self.db_event = 'No DB event was performed on this show.'
        self.new_show = new_show

    @classmethod
    def known_season(cls, title: str, airing_details: tuple[str, datetime], episode_details: tuple[str, int, str], recorded_show: RecordedShow):
        season_number, episode_number, episode_title = episode_details
        repeat = False
        new_show = False
        
        if recorded_show is not None:
            season = recorded_show.find_season(season_number)
            if season is not None:
                if episode_number != 0:
                    episode = season.find_episode(episode_number=episode_number)
                else:
                    episode = season.find_episode(episode_title=episode_title)
                if episode and episode_title == "":
                    episode_title = episode.episode_title
                if episode and (episode.is_repeat() or len(episode.air_dates) == 1):
                    repeat = True
        else:
            new_show = True
        
        return cls(title, airing_details, (season_number, episode_number, episode_title, repeat), recorded_show, new_show)

    @classmethod
    def unknown_season(cls, title: str, airing_details: tuple[str, datetime], episode_title: str, recorded_show: RecordedShow, unknown_episodes: int):
        repeat = False
        new_show = False
        season_number = 'Unknown'

        if recorded_show is None:
            new_show = True
            episode_number = unknown_episodes
        elif episode_title == "":
            episode_number = 1 if unknown_episodes == 0 else unknown_episodes
        else:
            episode_search = recorded_show.find_episode_instances(episode_title)
            if episode_search is None:
                unknown_season_episodes = recorded_show.get_unknown_episodes_count()
                episode_number = 1 if unknown_season_episodes + unknown_episodes == 0 else unknown_season_episodes + unknown_episodes
            else:
                season_number, episode = episode_search
                episode_number = episode.episode_number
                if episode.is_repeat() or len(episode.air_dates) == 1:
                    repeat = True
        
        return cls(title, airing_details, (season_number, episode_number, episode_title, repeat), recorded_show, new_show)

    @staticmethod
    def get_show(title: str, season_number: str, episode_number: int, episode_title: str):
        if 'Transformers' in title or 'Bumblebee' in title:
            handle_result = TransformersGuideShow.handle(title)
            if isinstance(handle_result, str):
                return handle_result, season_number, episode_number, episode_title
            return handle_result
        if ': ' in title and episode_title == "":
            title, episode_title = title.split(': ')
        if ' - ' in title and episode_title == "":
            title, episode_title = title.split(' - ')
        if f'{title} - ' in episode_title:
            episode_title = episode_title.split(' - ')[1]
        return Validation.check_show_titles(title), season_number, episode_number, episode_title

    def find_recorded_episode(self):
        """
        Checks the local files in the `shows` directory for information about a `GuideShow`'s information\n
        Raises `EpisodeNotFoundError` if the episode can't be found in the database.\n
        Raises `SeasonNotFoundError` if the season can't be found in the database.\n
        Raises `ShowNotFoundError` if the show can't be found in the database.
        """
        if self.recorded_show or not self.new_show:
            season = self.recorded_show.find_season(self.season_number)
            if season:
                episode = season.find_episode(episode_number=self.episode_number, episode_title=self.episode_title)
                if episode:
                    return episode
                else:
                    raise EpisodeNotFoundError
            else:
                raise SeasonNotFoundError
        else:
            raise ShowNotFoundError
        
    def schedule_reminder(self, database_service: DatabaseService, scheduler: AsyncIOScheduler = None):
        """
        Create a reminder for the episode aired, if one has been created for this show.\n
        Returns `None` if no reminder has been set for the show.
        """
        reminder = database_service.get_one_reminder(self.title)
        if reminder is not None and reminder.compare_reminder_interval(self) and 'HD' not in self.channel:
            reminder.airing_details = (self.channel, self.time)
            reminder.calculate_notification_time()
            self.reminder = reminder
            if scheduler is not None:
                from apscheduler.triggers.date import DateTrigger
                from services.hermes.utilities import send_message
                scheduler.add_job(
                    send_message,
                    DateTrigger(run_date=reminder.notify_time, timezone='Australia/Sydney'),
                    [reminder.notification()],
                    id=f'reminder-{reminder.show}-{Validation.get_current_date()}',
                    name=f'Send the reminder message for {reminder.show}'
                )

    def message_string(self):
        """
        String that is displayed in the Guide's notification message
        """
        time = self.time.strftime('%H:%M')
        message = f'{time}: {self.title} is on {self.channel}'
        message += f' (Season {self.season_number}, Episode {self.episode_number}'
        if self.episode_title != '':
            message += f': {self.episode_title}'
        message += ')'
        if self.repeat:
            message = f'{message} (Repeat)'

        return message

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'channel': self.channel,
            'time': self.time.strftime('%H:%M'),
            'season_number': self.season_number,
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'repeat': self.repeat,
            'event': self.db_event
        }

    def __repr__(self) -> str:
        return self.message_string()

    def __eq__(self, other: 'GuideShow') -> bool:
        return self.title == other.title and self.channel == other.channel and self.time == self.time

    def __hash__(self) -> int:
        return hash((self.title, self.channel, self.time))

