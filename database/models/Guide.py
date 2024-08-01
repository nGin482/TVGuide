from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
import os

from aux_methods.helper_methods import build_episode, convert_utc_to_local
from database.models.GuideShow import GuideShow
from data_validation.validation import Validation
from services.APIClient import APIClient

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from database.DatabaseService import DatabaseService


class Guide:

    def __init__(self, date: datetime, fta_shows: list[GuideShow], bbc_shows: list[GuideShow]) -> None:
        self.date = date
        self.fta_shows = fta_shows
        self.bbc_shows = bbc_shows

    @classmethod
    def from_database(cls, guide_details: dict, database_service: DatabaseService = None):
        datetime_stamp = datetime.strptime(guide_details['date'], '%d/%m/%Y')

        fta_list = [Guide.build_guide_show(show, [], database_service) for show in guide_details['FTA']]
        bbc_list = [Guide.build_guide_show(show, [], database_service) for show in guide_details['BBC']]

        return cls(datetime_stamp, fta_list, bbc_list)

    @classmethod
    def from_runtime(cls, date: datetime = None):
        guide_date = date if date is not None else Validation.get_current_date()
        from database.DatabaseService import DatabaseService
        database_service = DatabaseService(os.getenv('TVGUIDE_DB'), os.getenv('DATABASE_NAME'))
        fta_shows = Guide.search_free_to_air(database_service)
        bbc_shows = Guide.search_bbc_australia(database_service)
        return cls(guide_date, fta_shows, bbc_shows)
    
    @staticmethod
    def search_free_to_air(database_service: DatabaseService):
        """

        """

        date = Validation.get_current_date().date()

        shows_data: list[dict] = []

        environment = os.getenv('PYTHON_ENV')
        if environment == 'production' or environment == 'testing':
            api_client = APIClient()
            schedule = api_client.get(
                f"https://cdn.iview.abc.net.au/epg/processed/Sydney_{date.strftime('%Y-%m-%d')}.json"
            )['schedule']
        else:
            schedule = database_service.get_source_data('FTA')['schedule']
        search_list = database_service.get_search_list()

        for channel_data in schedule:
            for guide_show in channel_data['listing']:
                title: str = guide_show['title']
                for search_item in search_list:
                    if search_item.show.lower() in title.lower():
                        show_date = datetime.strptime(guide_show['start_time'], '%Y-%m-%dT%H:%M:%S')
                        if show_date.day == date.day:
                            season_number = 'Unknown'
                            episode_number = 0
                            episode_title = ''
                            if 'series_num' in guide_show.keys() and 'episode_num' in guide_show.keys():
                                season_number = int(guide_show['series_num'])
                                episode_number = int(guide_show['episode_num'])
                            if 'episode_title' in guide_show.keys():
                                episode_title = guide_show['episode_title']
                            episodes = build_episode(
                                guide_show['title'],
                                channel_data['channel'],
                                show_date,
                                season_number,
                                episode_number,
                                episode_title
                            )
                            episodes = [episode for episode in episodes if search_item.check_search_conditions(episode)]
                            shows_data.extend(episodes)

        shows_data.sort(key=lambda show: (show['time'], show['channel']))

        shows_on: list['GuideShow'] = []
        for show in shows_data:
            unknown_episodes = [
                show_data for show_data in shows_data
                if show_data['title'] == show['title']
                and show['season_number'] == 'Unknown'
            ]
            guide_show = Guide.build_guide_show(show, unknown_episodes, database_service)
            if 'HD' not in guide_show.channel:
                database_service.capture_db_event(guide_show)
            shows_on.append(guide_show)
        
        return shows_on

    @staticmethod
    def search_bbc_australia(database_service: DatabaseService):

        current_date = Validation.get_current_date().date()
        search_date = current_date.strftime('%Y-%m-%d')
        
        environment = os.getenv('PYTHON_ENV')
        if environment == 'production' or environment == 'testing':
            api_client = APIClient()
            bbc_first_data: dict = api_client.get(
                f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-first?timezone=Australia%2FSydney&date={search_date}'
            )
            bbc_uktv_data = api_client.get(
                f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-uktv?timezone=Australia%2FSydney&date={search_date}'
            )
        else:
            bbc_first_data = database_service.get_source_data('BBC First')['schedule']
            bbc_uktv_data = database_service.get_source_data('BBC UKTV')['schedule']

        search_list = database_service.get_search_list()

        show_list = []

        def search_channel_data(channel_data: list, channel: str):
            for show in channel_data:
                for search_item in search_list:
                    title: str = show['show']['title']
                    if title.lower() == search_item.show.lower():
                        guide_start = datetime.strptime(show['start'], '%Y-%m-%d %H:%M:%S')
                        start_time = convert_utc_to_local(guide_start)
                        series_num = show['episode']['series']['number']
                        episode_num = show['episode']['number']
                        episode_title = show['episode']['title']

                        episodes = build_episode(
                            title,
                            channel,
                            start_time,
                            series_num,
                            episode_num,
                            episode_title
                        )
                        episodes = [episode for episode in episodes if search_item.check_search_conditions(episode)]
                        show_list.extend(episodes)
        
        search_channel_data(bbc_first_data, 'BBC First')
        search_channel_data(bbc_uktv_data, 'BBC UKTV')

        shows_on: list[GuideShow] = []
        for show in show_list:
            guide_show = Guide.build_guide_show(show, show_list, database_service)
            database_service.capture_db_event(guide_show)
            shows_on.append(guide_show)

        return shows_on
    
    @staticmethod
    def build_guide_show(show: dict, unknown_episodes: list[dict], database_service: DatabaseService):
        episode_data = GuideShow.get_show(show['title'], show['season_number'], show['episode_number'], show['episode_title'])
        title, season_number, episode_number, episode_title = episode_data
        recorded_show = database_service.get_one_recorded_show(title)

        if season_number != 'Unknown':
            guide_show = GuideShow.known_season(
                title,
                (show['channel'], show['time']),
                (season_number, episode_number, episode_title),
                recorded_show
            )
        else:
            episode_number = Validation.get_unknown_episode_number(unknown_episodes, title, episode_title)
            if episode_number is None:
                episode_number = 0
            guide_show = GuideShow.unknown_season(
                title,
                (show['channel'], show['time']),
                episode_title,
                recorded_show,
                episode_number
            )

        return guide_show
    
    def compose_message(self):
        """
        toString function that writes the shows, times, channels and episode information (if available) via natural language
        :return: the to-string message
        """
        
        message = f"{self.date.strftime('%A %d-%m-%Y')} TVGuide\n"

        # Free to Air
        message += "\nFree to Air:\n"
        if len(self.fta_shows) == 0:
            message += "Nothing on Free to Air today\n"
        else:
            for show in self.fta_shows:
                message += f'{show.message_string()}\n'

        # BBC
        message = message + "\nBBC:\n"
        if len(self.bbc_shows) == 0:
            message = message + "Nothing on BBC today\n"
        else:
            for show in self.bbc_shows:
                message += f'{show.message_string()}\n'

        return message
    
    def compose_events_message(self):
        guide_list = self.fta_shows + self.bbc_shows
        return "\n".join([f"{show.title} - {show.db_event}" for show in guide_list])
    
    def schedule_reminders(self, database_service: DatabaseService, scheduler: AsyncIOScheduler = None):
        print('===================================================================================')
        print('Reminders:')
        guide_list = self.fta_shows + self.bbc_shows
        for guide_show in guide_list:
            guide_show.schedule_reminder(database_service, scheduler)
        reminders = [guide_show.reminder for guide_show in guide_list if guide_show.reminder is not None]

        if len(reminders) > 0:
            print(f'{len(reminders)} reminders for today')
            print('===================================================================================')
            return '\n'.join([reminder.general_message() for reminder in reminders])
        else:
            print('There are no reminders scheduled for today')
            print('===================================================================================')
            return 'There are no reminders scheduled for today'

    def search_for_show(self, show_title):
        return [show for show in self.fta_shows if show_title in show.title]


    def to_dict(self):
        return {
            'date': self.date.strftime('%d/%m/%Y'),
            'FTA': [show.to_dict() for show in self.fta_shows],
            'BBC': [show.to_dict() for show in self.bbc_shows]
        }
