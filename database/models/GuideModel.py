from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import Mapped, Session
from sqlalchemy.exc import OperationalError, PendingRollbackError
import json
import logging

from aux_methods.helper_methods import build_episode, convert_utc_to_local, show_data_to_file
from aux_methods.types import ShowData
from config import session
from database import Base
from database.models.GuideEpisode import GuideEpisode
from database.models.Reminder import Reminder
from database.models.SearchItemModel import SearchItem
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from data_validation.validation import Validation
from services.APIClient import APIClient


class Guide(Base):
    __tablename__ = 'Guide'

    id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = Column('date', DateTime)

    logger = logging.getLogger("Guide")
    
    def __init__(self, date: datetime):
        self.date = date
        self.fta_shows = []
        self.bbc_shows = []

    def add_guide(self, session: Session):
        session.add(self)
        session.commit()

    def delete_guide(self, session: Session):
        session.delete(self)
        session.commit()

    def search_free_to_air(self, scheduler: AsyncIOScheduler = None):
        """

        """

        shows_data: list[ShowData] = []

        schedule = self.get_source_data(
            f"https://cdn.iview.abc.net.au/epg/processed/Sydney_{self.date.strftime('%Y-%m-%d')}.json"
        )['schedule']
        search_list = SearchItem.get_active_searches(session)

        for channel_data in schedule:
            for guide_show in channel_data['listing']:
                title: str = guide_show['title']
                for search_item in search_list:
                    if "bumblebee" in title.lower():
                        title = "Transformers: Cyberverse"
                    if search_item.show.lower() in title.lower():
                        start_time = datetime.strptime(guide_show['start_time'], '%Y-%m-%dT%H:%M:%S')
                        end_time = datetime.strptime(guide_show['end_time'], '%Y-%m-%dT%H:%M:%S')
                        season_number = -1
                        episode_number = 0
                        episode_title = ''
                        if 'series_num' in guide_show and 'episode_num' in guide_show:
                            season_number = int(guide_show['series_num'])
                            episode_number = int(guide_show['episode_num'])
                        if 'episode_title' in guide_show:
                            episode_title = guide_show['episode_title']
                        episodes = build_episode(
                            guide_show['title'],
                            channel_data['channel'],
                            start_time,
                            end_time,
                            season_number,
                            episode_number,
                            episode_title
                        )
                        episodes = [episode for episode in episodes if search_item.check_search_conditions(episode)]
                        shows_data.extend(episodes)

        shows_data = [dict(t) for t in {tuple(d.items()) for d in shows_data}]
        
        shows_data.sort(key=lambda show: (show['start_time'], show['channel']))


        shows_on: list['GuideEpisode'] = []
        for show in shows_data:
            show_details = ShowDetails.get_show_by_title(show['title'], session)
            show_episode = ShowEpisode.search_for_episode(
                show['title'],
                show['season_number'],
                show['episode_number'],
                show['episode_title'],
                session
            )
            reminder = Reminder.get_reminder_by_show(show['title'], session)
            guide_episode = GuideEpisode(
                show['title'],
                show['channel'],
                show['start_time'],
                show['end_time'],
                show_episode.season_number if show_episode is not None else show['season_number'],
                show_episode.episode_number if show_episode is not None else show['episode_number'],
                show_episode.episode_title if show_episode is not None else show['episode_title'],
                self.id,
                show_details.id,
                show_episode.id if show_episode is not None else None,
                reminder.id if reminder is not None else None
            )
            guide_episode.add_episode(session)
            guide_episode.check_repeat(session)
            guide_episode.set_reminder(scheduler)
            if 'HD' not in guide_episode.channel:
                guide_episode.capture_db_event(session)
            shows_on.append(guide_episode)
        
        return shows_on

    def search_bbc_australia(self):

        current_date = Validation.get_current_date().date()
        search_date = current_date.strftime('%Y-%m-%d')
        
        bbc_first_data = self.get_source_data(
            f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-first?timezone=Australia%2FSydney&date={search_date}'
        )
        bbc_uktv_data = self.get_source_data(
            f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-uktv?timezone=Australia%2FSydney&date={search_date}'
        )

        search_list = SearchItem.get_active_searches(session)

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

        shows_on: list['GuideEpisode'] = []
        for show in show_list:
            guide_episode = GuideEpisode(
                show['title'],
                show['channel'],
                show['start_time'],
                show['start_time'],
                show['season_number'],
                show['episode_number'],
                show['episode_title']
            )
            # guide_show = Guide.build_guide_show(show, show_list, database_service)

            # database_service.capture_db_event(guide_show)
            shows_on.append(guide_episode)

        return shows_on
    
    def get_source_data(self, endpoint: str = None):
        if endpoint:
            try:
                api_client = APIClient()
                schedule = api_client.get(endpoint)
                return schedule
            except Exception as error:
                from services.hermes.hermes import hermes
                hermes.dispatch('guide_data_fetch_failed', str(error))
        else:
            with open(f"dev-data/free_to_air/{self.date.strftime('%Y-%m-%d')}.json") as fd:
                schedule = json.load(fd)
            return schedule
    
    def create_new_guide(self, scheduler: AsyncIOScheduler = None):
        try:
            self.add_guide(session)
            self.fta_shows = self.search_free_to_air(scheduler)
        except OperationalError as error:
            Guide.logger.error(f"Could not create guide: {str(error)}")
            session.rollback()
        except PendingRollbackError as error:
            Guide.logger.error(f"Could not create guide: {str(error)}")
            session.rollback()
        # self.bbc_shows = self.search_bbc_australia()
    
    def get_shows(self, session: Session):
        self.fta_shows = GuideEpisode.get_shows_for_date(self.date, session)


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
    
    def compose_reminder_message(self):
        fta_reminders = [
            show
            for show in self.fta_shows
            if show.reminder is not None and 'notify_time' in show.reminder.__dict__
        ]
        if len(fta_reminders) > 0:
            message = '\n'.join([show.reminder_message() for show in fta_reminders])
        else:
            message = 'There are no reminders scheduled for today'
        
        return message

    def compose_events_message(self):
        fta_events = [f"{show.title} - {show.db_event}" for show in self.fta_shows]

        return "\n".join(fta_events)

    def to_dict(self):
        return {
            'date': self.date.strftime('%d/%m/%Y'),
            'fta': [show.to_dict() for show in self.fta_shows]
        }
