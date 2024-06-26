from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from requests import get
import os

from aux_methods.helper_methods import build_episode, convert_utc_to_local
from config import database_service
from data_validation.validation import Validation
from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from log import compare_dates

def find_json(url):
    headers = {
        'User-Agent': 'Chrome/119.0.0.0'
    }
    request = get(url, headers=headers)
    
    return request.json()

def search_free_to_air():
    """

    :return:
    """

    date = Validation.get_current_date().date()

    new_url = f"https://epg.abctv.net.au/processed/Sydney_{date.strftime('%Y-%m-%d')}.json"
    shows_data: list[dict] = []

    environment = os.getenv('PYTHON_ENV')
    if environment == 'production' or environment == 'testing':
        schedule = dict(find_json(new_url))['schedule']
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
        guide_show = build_guide_show(show, unknown_episodes)
        if 'HD' not in guide_show.channel:
            database_service.capture_db_event(guide_show)
        shows_on.append(guide_show)
    
    return shows_on

def search_bbc_australia():

    current_date = Validation.get_current_date().date()
    search_date = current_date.strftime('%Y-%m-%d')
    
    environment = os.getenv('PYTHON_ENV')
    if environment == 'production':
        bbc_first_data = find_json(f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-first?timezone=Australia%2FSydney&date={search_date}')
        bbc_uktv_data = find_json(f'https://www.bbcstudios.com.au/smapi/schedule/au/bbc-uktv?timezone=Australia%2FSydney&date={search_date}')
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
        guide_show = build_guide_show(show, show_list)
        database_service.capture_db_event(guide_show)
        shows_on.append(guide_show)

    return shows_on

def build_guide_show(show: dict, unknown_episodes: list[dict]):
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

def compose_message(fta_shows: list['GuideShow'], bbc_shows: list['GuideShow'], date_provided: datetime = None):
    """
    toString function that writes the shows, times, channels and episode information (if available) via natural language
    :return: the to-string message
    """
    
    message_date = date_provided if date_provided is not None else Validation.get_current_date()
    message = f"{message_date.strftime('%A %d-%m-%Y')} TVGuide\n"

    # Free to Air
    message += "\nFree to Air:\n"
    if len(fta_shows) == 0:
        message += "Nothing on Free to Air today\n"
    else:
        for show in fta_shows:
            message += f'{show.message_string()}\n'

    # BBC
    message = message + "\nBBC:\n"
    if len(bbc_shows) == 0 or bbc_shows[0] is []:
        message = message + "Nothing on BBC today\n"
    else:
        for show in bbc_shows:
            message += f'{show.message_string()}\n'

    return message

def reminders(guide_list: list['GuideShow'], scheduler: AsyncIOScheduler = None):
    print('===================================================================================')
    print('Reminders:')
    for guide_show in guide_list:
        guide_show.create_reminder(database_service)
    reminders = [guide_show.reminder for guide_show in guide_list if guide_show.reminder is not None]

    if len(reminders) > 0:
        reminders_message = '\n'.join([reminder.general_message() for reminder in reminders])
        if scheduler is not None:
            from apscheduler.triggers.date import DateTrigger
            from services.hermes.utilities import send_message
            for reminder in reminders:
                scheduler.add_job(
                    send_message,
                    DateTrigger(run_date=reminder.notify_time, timezone='Australia/Sydney'),
                    [reminder.notification()],
                    id=f'reminder-{reminder.show}-{Validation.get_current_date()}',
                    name=f'Send the reminder message for {reminder.show}'
                )
        return reminders_message
    else:
        print('There are no reminders scheduled for today')
        print('===================================================================================')
        return 'There are no reminders scheduled for today'

def run_guide(fta_list: list['GuideShow'], bbc_list: list['GuideShow'], scheduler: AsyncIOScheduler=None):

    latest_guide = database_service.get_latest_guide()
    if latest_guide:
        print(latest_guide.date)
        update_db_flag = compare_dates(latest_guide.date)
    else:
        update_db_flag = True
    print(update_db_flag)
    
    guide_list = fta_list + bbc_list
    
    guide_message = compose_message(fta_list, bbc_list)
    print(guide_message)
    if update_db_flag:
        database_service.backup_recorded_shows()
        database_service.add_guide_data(fta_list, bbc_list)

    reminders_message = reminders(guide_list, scheduler)
    return guide_message, reminders_message

def revert_database_tvguide(database_service: DatabaseService):
    "Forget sending a message and rollback the database to its previous state"
    database_service.rollback_recorded_shows()
    database_service.remove_guide_data(Validation.get_current_date().strftime('%d/%m/%Y'))