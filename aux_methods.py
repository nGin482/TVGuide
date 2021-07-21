from datetime import date
from database import get_one_recorded_show
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


def sort_shows_by_time(shows_list, pos1, pos2):

    cur_idx = 0

    if pos1 != -1 and pos2 != -1:
        backup = shows_list[pos1]
        shows_list[pos1] = shows_list[pos2]
        shows_list[pos2] = backup
    else:
        if len(shows_list) > 1:
            while cur_idx < len(shows_list)-1:
                cur = shows_list[cur_idx]
                temp_idx = cur_idx + 1
                while temp_idx < len(shows_list):
                    temp = shows_list[temp_idx]
                    if int(temp['time'][:2]) < int(cur['time'][:2]):
                        backup = temp
                        shows_list[temp_idx] = shows_list[cur_idx]
                        shows_list[cur_idx] = backup
                        cur_idx += 1
                    temp_idx += 1
                cur_idx += 1

    # shows_list = sorted(shows_list, key=lambda i: int(i['time']))

    return shows_list


def check_time_sort(shows_list):
    cur_idx = 0

    if len(shows_list) > 1:
        while cur_idx < len(shows_list)-1:
            cur = shows_list[cur_idx]
            temp_idx = cur_idx + 1
            while temp_idx < len(shows_list):
                temp = shows_list[temp_idx]
                if cur['time'].hour > temp['time'].hour:
                    return [temp_idx, cur_idx]
                elif cur['time'].hour == temp['time'].hour and cur['time'].minute > temp['time'].minute:
                    return [temp_idx, cur_idx]
                temp_idx += 1
            cur_idx += 1

    return [-1, -1]


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

    if ', The' in title:
        idx_the = title.find(', The')
        title = 'The ' + title[0:idx_the]
    if ', A' in title:
        idx_a = title.find(', A')
        title = 'A ' + title[0:idx_a]

    return title


def morse_episodes(guide_title):
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


def get_show_list():

    with open('shows.txt') as fd:
        shows = fd.read().splitlines()

    return shows


def show_list_for_message():
    shows_from_file = get_show_list()
    show_list = ''
    for show in shows_from_file:
        show_list = show_list + show + '\n'
    return show_list


def add_show_to_list(new_show):

    with open('shows.txt') as fd:
        shows = fd.read().splitlines(True)
    shows.append(new_show + '\n')

    with open('shows.txt', 'w') as fd:
        for show in shows:
            fd.write(show)


def remove_show_from_list(show):

    with open('shows.txt') as fd:
        shows = fd.read().splitlines(False)
    
    if show in shows:
        shows.remove(show)

        with open('shows.txt', 'w') as fd:
            for show in shows:
                fd.write(show + '\n')
        return {'status': True}
    else:
        return {'status': False, 'message': show + ' was not found in the list.'}


def write_to_today_file(today_viewing):
    viewing_list = []

    for show in today_viewing:
        viewing_list.append(show.to_dict())

    if not os.path.isdir('today_viewings'):
        os.mkdir('today_viewings')

    files = {
        'count': 0,
        'filenames': []
    }
    for filename in os.listdir('today_viewings'):
        files['count'] += 1
        files['filenames'].append('today_viewings/' + filename)
        
    if files['count'] >= 1:
        if os.path.exists(files['filenames'][0]):
            os.remove(files['filenames'][0])

    filename = 'today_viewings/' + date.strftime(date.today(), '%d-%m-%Y') + '.json'
    with open(filename, 'w+', encoding='utf-8') as fd:
        json.dump(viewing_list, fd, ensure_ascii=False, indent=4)

def valid_reminder_fields():
    return ['show', 'reminder time', 'interval']
