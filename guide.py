from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from requests import get
import pytz

from data_validation.validation import Validation
from database.DatabaseService import DatabaseService
from database.models.GuideShow import GuideShow
from log import clear_events_log, compare_dates, delete_latest_entry, log_guide_information

def find_json(url):
    return dict(get(url).json())

def search_free_to_air(database_service: DatabaseService):
    """

    :return:
    """

    date = datetime.now(pytz.timezone('Australia/Sydney')).date()

    new_url = f'https://epg.abctv.net.au/processed/Sydney_{str(date)}.json'
    shows_on: list[GuideShow] = []
    shows_data: list[dict] = []

    data = find_json(new_url)['schedule']
    search_list = database_service.get_search_list()

    for channel_data in data:
        for guide_show in channel_data['listing']:
            title = guide_show['title']
            for show in search_list:
                if show in title:
                    show_date = datetime.strptime(guide_show['start_time'], '%Y-%m-%dT%H:%M:%S')
                    if show_date.day == date.day:
                        season_number = 'Unknown'
                        episode_number = 0
                        episode_title = ''
                        if 'series_num' in guide_show.keys() and 'episode_num' in guide_show.keys():
                            season_number = str(guide_show['series_num'])
                            episode_number = int(guide_show['episode_num'])
                        if 'episode_title' in guide_show.keys():
                            episode_title = guide_show['episode_title']
                        episodes = Validation.build_episode(
                            guide_show['title'],
                            channel_data['channel'],
                            show_date,
                            season_number,
                            episode_number,
                            episode_title
                        )
                        for episode in episodes:
                            shows_data.append(episode)

    shows_data = Validation.remove_unwanted_shows(shows_data)

    for show in shows_data:
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
            episode_number = Validation.get_unknown_episode_number(shows_on, title, episode_title)
            if episode_number is None:
                episode_number = 0
            guide_show = GuideShow.unknown_season(
                title,
                (show['channel'], show['time']),
                episode_title,
                recorded_show,
                episode_number
            )
        shows_on.append(guide_show)

    shows_on = list(set(shows_on))
    shows_on.sort(key=lambda show_obj: (show_obj.time, show_obj.channel))
    
    return shows_on

def compose_message(
        fta_shows: list['GuideShow'],
        bbc_shows: list['GuideShow'],
        message_date: datetime = datetime.now(pytz.timezone('Australia/Sydney')).date()
    ):
    """
    toString function that writes the shows, times, channels and episode information (if available) via natural language
    :return: the to-string message
    """
    
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
            message += show.message_string()

    return message

def reminders(guide_list: list['GuideShow'], database_service: DatabaseService, scheduler: AsyncIOScheduler = None):
    print('===================================================================================')
    print('Reminders:')
    reminders = database_service.get_reminders_for_shows(guide_list)
    if len(reminders) > 0:
        reminders_message = '\n'.join([reminder.general_message() for reminder in reminders if reminder.compare_reminder_interval() and 'HD' not in reminder.guide_show.channel])
        if scheduler is not None:
            from apscheduler.triggers.date import DateTrigger
            from services.hermes.utilities import send_message
        
            for reminder in reminders:
                if reminder.compare_reminder_interval() and 'HD' not in reminder.guide_show.channel:
                    scheduler.add_job(send_message, DateTrigger(run_date=reminder.notify_time, timezone='Australia/Sydney'), [reminder.notification()])
        print(reminders_message)
        print('===================================================================================')
        return reminders_message
    else:
        print('There are no reminders scheduled for today')
        print('===================================================================================')
        return 'There are no reminders scheduled for today'

def run_guide(database_service: DatabaseService, guide_list: list['GuideShow'], scheduler: AsyncIOScheduler=None):

    latest_guide = database_service.get_latest_guide()
    print(latest_guide.date)
    
    update_db_flag = compare_dates(latest_guide.date)
    print(update_db_flag)
    
    guide_message = compose_message(guide_list, [])
    print(guide_message)
    if update_db_flag:
        clear_events_log()
        database_service.backup_recorded_shows()
        
        for guide_show in guide_list:
            if 'HD' not in guide_show.channel:
                guide_show.db_event = str(database_service.capture_db_event(guide_show)['result'])
        database_service.add_guide_data(guide_list, [])
        log_guide_information(guide_list, [])

    reminders_message = reminders(guide_list, database_service, scheduler)
    return guide_message, reminders_message

def revert_database_tvguide(database_service: DatabaseService):
    "Forget sending a message and rollback the database to its previous state"
    delete_latest_entry()
    database_service.rollback_recorded_shows()
    database_service.remove_guide_data(datetime.now(pytz.timezone('Australia/Sydney')).strftime('%d/%m/%Y'))