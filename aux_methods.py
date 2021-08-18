from datetime import date, datetime
import json
import os

def format_time(time):
    """
    format a show's start time to 24 hour time
    :param time: show start_time to format that will be passed as string
    :return: the formatted time string
    """

    idx = time.find(':')

    if " " in time:
        time = time[1:7]
    if len(time) == 6:
        time = '0' + time
    if 'pm' in time:
        time = time[:-2]
        if time[:idx] != '12':
            hour = int(time[:idx]) + 12
            time = str(hour) + time[idx:]
    if 'am' in time:
        time = time[:-2]
        if time[:idx] == '12':
            hour = int(time[:idx]) - 12
            time = str(hour) + '0' + time[idx:]

    return time


def remove_doubles(shows_list):

    idx_1 = 0
    if len(shows_list) > 1:
        while idx_1 < len(shows_list)-1:
            show_1 = shows_list[idx_1]
            idx_2 = idx_1 + 1
            while idx_2 < len(shows_list):
                show_2 = shows_list[idx_2]
                if show_1['channel'] == show_2['channel'] and show_1['time'] == show_2['time']:
                    shows_list.remove(show_2)
                idx_2 += 1
            idx_1 += 1


def format_title(title):
    """
    Format a show's given title into a more reader-friendly appearance
    """

    if ', The' in title:
        idx_the = title.find(', The')
        title = 'The ' + title[0:idx_the]
    if ', A' in title:
        idx_a = title.find(', A')
        title = 'A ' + title[0:idx_a]

    return title


def morse_episodes(guide_title):
    """
    Given an episode's title, return the season number, episode number and correct episode title of an Inspector Morse episode
    """

    morse_titles = [
        {'Episodes': ['The Dead Of Jericho', 'The Silent World Of Nicholas Quinn', 'Service Of All The Dead']},
        {'Episodes':
            ['The Wolvercote Tongue', 'Last Seen Wearing', 'The Settling Of The Sun', 'Last Bus To Woodstock']},
        {'Episodes': ['Ghost In The Machine', 'The Last Enemy', 'Deceived By Flight', 'The Secret Of Bay 5B']},
        {'Episodes': ['The Infernal Spirit', 'The Sins Of The Fathers', 'Driven To Distraction',
                      'The Masonic Mysteries']},
        {'Episodes':
            ['Second Time Around', 'Fat Chance', 'Who Killed Harry Field?', 'Greeks Bearing Gifts', 'Promised Land']},
        {'Episodes': ['Dead On Time', 'Happy Families', 'The Death Of The Self', 'Absolute Conviction',
                      'Cherubim And Seraphim']},
        {'Episodes': ['Deadly Slumber', 'The Day Of The Devil', 'Twilight Of The Gods']},
        {'Episodes': ['The Way Through The Woods', 'The Daughters Of Cain', 'Death Is Now My Neighbour',
                      'The Wench Is Dead', 'The Remorseful Day']}]

    if 'Service Of All' in guide_title:
        return 1, 3, 'Service Of All The Dead'
    if 'Infernal Spirit' in guide_title:
        return 4, 1, 'The Infernal Serpent'
    if 'In Australia' in guide_title:
        return 5, 4, 'Promised Land'
    if 'Death Is' in guide_title:
        return 8, 3, 'Death Is Now My Neighbour'
    else:
        for season_idx, season in enumerate(morse_titles):
            for episode_idx, title in enumerate(season['Episodes']):
                if 'The' in guide_title and 'The' not in title:
                    title = 'The ' + title
                if guide_title in title:
                    return season_idx+1, episode_idx+1, title


def show_list_for_message(shows_list):
    show_list = ''
    for show in shows_list:
        show_list = show_list + show + '\n'
    return show_list

def valid_reminder_fields():
    """
    Returns the fields only valid for a reminder document
    """
    return ['show', 'reminder time', 'interval']

def check_show_titles(show):
    if type(show) is str:
        if 'Maigret' in show:
            return 'Maigret'
        if 'Revenge Of The Fallen' in show or 'Dark Of The Moon' in show \
                or 'Age of Extinction' in show or 'The Last Knight' in show:
            return 'Transformers'
        elif show == 'Transformers':
            return 'Transformers'
        else:
            title = show
            if ':' in title:
                idx = title.rfind(':')
                title = title[:idx] + title[idx+1:]
            return title
    else:
        if 'Maigret' in show['title']:
            return 'Maigret'
        if 'Revenge Of The Fallen' in show['title'] or 'Dark Of The Moon' in show['title'] \
                or 'Age of Extinction' in show['title'] or 'The Last Knight' in show['title']:
            return 'Transformers'
        elif show['title'] == 'Transformers':
            return 'Transformers'
        else:
            title = show['title']
            if ':' in title:
                idx = title.rfind(':')
                title = title[:idx] + title[idx+1:]
            return title

def doctor_who_episodes(show_title):
    """
    Given an episode's title, return the season number, episode number and correct episode title of a Doctor Who episode
    """
    
    if show_title == 'Doctor Who':
        return show_title
    
    tennant_specials = ['The Next Doctor', 'Planet of the Dead', 'The Waters of Mars', 'The End of Time - Part 1', 'The End of Time - Part 2']
    smith_specials = ['The Snowmen', 'The Day of the Doctor', 'The Time of the Doctor']

    if 'Doctor Who: ' in show_title:
        show_title = show_title.split(': ')[1]
    
    for idx, tennant_special in enumerate(tennant_specials):
        if show_title in tennant_special:
            return 'Tennant Specials', idx+1, tennant_special
    for idx, smith_special in enumerate(smith_specials):
        if show_title in smith_special:
            return 'Smith Specials', idx+1, smith_special
    
    if 'Christmas Invasion' in show_title:
        return 2, 0, 'The Christmas Invasion'
    elif 'Runaway Bride' in show_title:
        return 3, 0, 'The Runaway Bride'
    elif 'Voyage of the Damned' in show_title:
        return 4, 0, 'Voyage of the Damned'
    elif 'Christmas Carol' in show_title:
        return 6, 0, 'A Christmas Carol'
    elif 'Wardrobe' in show_title:
        return 7, 0, 'The Doctor, the Widow and the Wardrobe'
    elif 'Last Christmas' in show_title:
        return 9, 0, 'Last Christmas'
    elif 'Husbands of River Song' in show_title:
        return 9, 13, 'The Husbands of River Song'
    elif 'Return of Doctor Mysterio' in show_title:
        return 10, 0, 'The Return of Doctor Mysterio'
    elif 'Twice Upon a Time' in show_title:
        return 10, 13, 'Twice Upon a Time'
    elif 'Resolution' in show_title:
        return 11, 11, 'Resolution'
    elif 'Revolution of the Daleks' in show_title:
        return 12, 11, 'Revolution of the Daleks'
    else:
        return show_title
    
def get_today_date(return_type):
    if return_type == 'string':
        return date.today().strftime('%d-%m-%Y')
    else:
        return date.today()

def get_today_date_for_logging():
    return date.today().strftime('%d-%m-%y')

def convert_date_string_to_object(given_date):
    return datetime.strptime(given_date, '%d-%m-%y')

def get_current_time(return_type):
    if return_type == 'string':
        return datetime.now().strftime('%H:%M')