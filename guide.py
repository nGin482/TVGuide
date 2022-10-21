from datetime import datetime
from requests import get
from aux_methods.helper_methods import remove_doubles

from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from data_validation.validation import Validation
from database.DatabaseService import DatabaseService
from log import clear_events_log, clear_imdb_api_results, compare_dates, delete_latest_entry, log_guide_information

def get_today_shows_data(list_of_shows: list[str], database_service: DatabaseService):
    all_recorded_shows = database_service.get_all_recorded_shows()

    return [recorded_show for recorded_show in all_recorded_shows if recorded_show.title in list_of_shows]


def find_json(url):
    data = get(url).json()

    return data

def search_free_to_air(search_list: list[str], database_service: DatabaseService):
    """

    :return:
    """

    current_date = datetime.today().date()
    new_url = f'https://epg.abctv.net.au/processed/Sydney_{str(current_date)}.json'
    shows_on: list[GuideShow] = []
    shows_data: list[dict] = []

    data = find_json(new_url)['schedule']

    for item in data:
        listing = item['listing']

        # print("Listing: " + str(listing))
        for guide_show in listing:
            title = guide_show['title']
            for show in search_list:
                if show in title:
                    show_date = guide_show['start_time'][:-9]
                    if int(show_date[-2:]) == int(datetime.today().day):
                        season_number = ''
                        episode_number = 0
                        episode_title = ''
                        if 'series_num' in guide_show.keys() and 'episode_num' in guide_show.keys():
                            season_number = str(guide_show['series_num'])
                            episode_number = int(guide_show['episode_num'])
                        else:
                            season_number = 'Unknown'
                        if 'episode_title' in guide_show.keys():
                            episode_title = guide_show['episode_title']
                        shows_data.append({
                            'title': Validation.check_show_titles(guide_show['title']),
                            'channel': item['channel'],
                            'time': datetime.strptime(guide_show['start_time'][-8:-3], '%H:%M'),
                            'season_number': season_number,
                            'episode_number': episode_number,
                            'episode_title': episode_title
                        })

    shows_data = Validation.remove_unwanted_shows(shows_data)
    show_titles = [show['title'] for show in shows_data]
    recorded_shows: list['RecordedShow'] = get_today_shows_data(show_titles, database_service)
    shows_on = [
        GuideShow(
            data['title'],
            data['channel'],
            data['time'],
            data['season_number'],
            data['episode_number'],
            data['episode_title'],
            next((recorded_show for recorded_show in recorded_shows if Validation.check_show_titles(data['title']) == recorded_show.title), None)
        ) for data in shows_data
    ]
    shows_on = list(set(shows_on))
    shows_on.sort(key=lambda show_obj: show_obj.time)
    
    for show in shows_on:
        if show.recorded_show is not None:
            if show.season_number == 'Unknown':
                matching_shows = list(filter(lambda guide_show: guide_show.title == show.title and guide_show.season_number == 'Unknown', shows_on))
                show.update_episode_number_with_guide_list(matching_shows)

    remove_doubles(shows_on)
    return shows_on

def compose_message(fta_shows: list['GuideShow'], bbc_shows: list['GuideShow']):
    """
    toString function that writes the shows, times, channels and episode information (if available) via natural language
    :return: the to-string message
    """
    weekdays = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ]

    message_date = datetime.today().date()
    message = weekdays[message_date.weekday()] + " " + str(message_date.strftime('%d-%m-%Y')) + " TVGuide\n"

    # Free to Air
    message = message + "\nFree to Air:\n"
    if len(fta_shows) == 0:
        message = message + "Nothing on Free to Air today\n"
    else:
        for show in fta_shows:
            message += show.message_string()

    # BBC
    message = message + "\nBBC:\n"
    if len(bbc_shows) == 0 or bbc_shows[0] is []:
        message = message + "Nothing on BBC today\n"
    else:
        for show in bbc_shows:
            message += show.message_string()

    return message

def reminders(guide_list: list['GuideShow'], database_service: DatabaseService):
    print('===================================================================================')
    print('Reminders:')
    reminders = database_service.get_reminders_for_shows(guide_list)
    if len(reminders) > 0:
        for reminder in reminders:
            if reminder.compare_reminder_interval():
                print(f'REMINDER: {reminder.show} is on {reminder.guide_show.channel} at {reminder.guide_show.time.strftime("%H:%M")}')
                print(f'You will be reminded at {reminder.calculate_notification_time().strftime("%H:%M")}')
    else:
        print('There are no reminders scheduled for today')
    print('===================================================================================')

def run_guide(database_service: DatabaseService):

    update_db_flag = compare_dates()
    print(update_db_flag)
    
    clear_imdb_api_results()
    fta_shows = search_free_to_air(database_service.get_search_list(), database_service)
    guide_message = compose_message(fta_shows, [])
    print(guide_message)
    if update_db_flag:
        clear_events_log()
        database_service.backup_recorded_shows()
        
        for guide_show in fta_shows:
            if 'HD' not in guide_show.channel:
                database_service.capture_db_event(guide_show)
        database_service.add_guide_data(fta_shows, [])
        log_guide_information(fta_shows, [])

    reminders(fta_shows, database_service)
    return guide_message

def revert_tvguide(database_service: DatabaseService):
    "Forget sending a message and rollback the database to its previous state"
    delete_latest_entry()
    database_service.rollback_recorded_shows()
    database_service.remove_guide_data(datetime.today().strftime('%d/%m/%Y'))