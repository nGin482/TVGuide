from database.reminder_collection import get_all_reminders, get_one_reminder
from database.recorded_shows_collection import get_one_recorded_show
from aux_methods.helper_methods import get_today_date, check_show_titles
from datetime import datetime, timedelta, date
import json

def load_reminders():
    with open('reminders.json', 'r') as fd:
        reminders = json.load(fd)
    return reminders

def get_reminders_set():
    return get_all_reminders()

def read_guide_data():
    try:
        filename = 'today_guide/' + get_today_date('string') + '.json'
        with open(filename) as fd:
            guide = json.load(fd)
        return guide
    except FileNotFoundError:
        return []

def get_shows_on_today():
    shows_on_today = []
    guide = read_guide_data()

    for key in guide:
        shows_on_today.extend(guide[key])
    return shows_on_today

def get_guide_titles():
    return [check_show_titles(show['title']) for show in get_shows_on_today()]

def reminders_found():
    return [reminder for reminder in get_reminders_set() if reminder['show'] in get_guide_titles()]
    # return list(filter(lambda reminder: reminder['show'] in get_guide_titles(), get_reminders_set()))

def get_shows_for_reminders():
    guide = read_guide_data()
    shows_to_remind = []
    
    for reminder in reminders_found():
        reminder_notice = {
            'reminder': reminder,
            'episodes': []
        }
        for show in get_shows_on_today():
            if reminder['show'] in show['title']:
                reminder_notice['episodes'].append(show)
        shows_to_remind.append(reminder_notice)
    
    print(shows_to_remind)
    return shows_to_remind

def compare_reminder_interval():
    shows_to_remind = get_shows_for_reminders()
    interval_cleared_reminders = []
    for show in shows_to_remind:
        interval = show['reminder']['interval']
        if interval == 'All':
            # send message
            show_episodes = show['episodes']
            for show_episode in show_episodes:
                print('REMINDER: {title} is on {channel} at {time}'.format(**show_episode))
                interval_cleared_reminders.append(show)
        elif interval == 'Latest':
            find_show_data = get_one_recorded_show(show['reminder']['show'])
            if find_show_data['status']:
                show_data = find_show_data['show']
                seasons = [int(season['season number']) for season in show_data['seasons']]
                print(seasons)
                latest_season_number = max(seasons)
                print(latest_season_number)
                show_episodes = show['episodes']
                latest_episode_reminders = []
                for show_episode in show_episodes:
                    if int(show_episode['series_num']) >= latest_season_number:
                        print('reminder needed for this')
                        latest_episode_reminders.append(show_episode)
                show['episodes'] = latest_episode_reminders
                interval_cleared_reminders.append(show)
        elif interval == 'Once':
            pass
    
    return interval_cleared_reminders

def calculate_reminder_time():     
    # need to get time from guide data
    reminders = compare_reminder_interval()
    times_to_remind = []
    
    # remove any duplicates
    correct_reminders = [i for n, i in enumerate(reminders) if i not in reminders[n+1:]]
    
    # get the times from the episode dictionaries
    for show in correct_reminders:
        show_times = [episode['time'] for episode in show['episodes']]
        times_to_remind.extend(show_times)
    print(times_to_remind)

    # convert each time to a datetime object and take off the specified minutes
    times_to_remind = [datetime.strptime(time, '%H:%M') - timedelta(minutes=int(show['reminder']['reminder time'])) for time in times_to_remind]
    print(times_to_remind)
    for time in times_to_remind:
        print('You will be reminded at ' + date.strftime(time, '%H:%M'))
    
    episodes = [episode for reminder in correct_reminders for episode in reminder['episodes']]
    print()
    print('==========================    EPISODES    ==========================')
    print(episodes)
    print('====================================================================')
    print()
    
    return times_to_remind, episodes
