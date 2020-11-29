from show import Show, Season, Episode
from datetime import date
import json
import os


def get_shows(channel, superlist):
    for show in channel:
        sublist = []
        if len(superlist) == 0:
            sublist.append(show)
            superlist.append(sublist)
        else:
            inserted = False
            for item in superlist:
                if item[0]['title'] == show['title']:
                    item.append(show)
                    inserted = True
            if inserted is False:
                sublist.append(show)
                superlist.append(sublist)


def convert_to_objects(superlist):

    json_list = []
    for item in superlist:
        show_obj = Show(item[0])
        show_obj.seasons[0].create_episode(item[0])
        i = 1
        while i < len(item):
            idxs = show_obj.find_episode(item[i])
            if idxs[0] == -1:
                season_obj = Season(item[i])
                season_obj.create_episode(item[i])
                show_obj.seasons.append(season_obj)
            else:
                if idxs[1] == -1:
                    episode = Episode()
                    episode.set_episode_num(item[i])
                    episode.set_episode_title(item[i])
                    episode.add_channel(item[i]['channel'])
                    show_obj.seasons[idxs[0]].episodes.append(episode)

            i += 1
        json_list.append(show_obj)
    for json_obj in json_list:
        json_obj.cleanup_unknowns()

    return json_list


def special_cases(show):
    if 'Maigret' in show['title']:
        return 'shows/Maigret.json'
    if 'Revenge Of The Fallen' in show['title'] or 'Dark Of The Moon' in show['title'] \
            or 'Age of Extinction' in show['title'] or 'The Last Knight' in show['title']:
        return 'shows/Transformers.json'
    elif show['title'] == 'Transformers':
        return 'shows/Transformers.json'
    else:
        title = show['title']
        if ':' in title:
            idx = title.rfind(':')
            title = title[:idx] + title[idx+1:]
        return 'shows/' + title + '.json'


def read_file(show):

    title = show['title']
    if 'Transformers' in title or 'Maigret' in title:
        file_name = special_cases(show)
    else:
        if ':' in title:
            idx = title.rfind(':')
            title = title[:idx] + title[idx+1:]
        file_name = 'shows/' + title + '.json'

    try:
        with open(file_name, 'r', encoding='utf-8') as fd:
            file_string = fd.read()
            data = json.loads(file_string)
    except FileNotFoundError:
        with open(file_name, 'w+', encoding='utf-8') as fd:
            data = [{
                'season num': 'Unknown',
                'episodes': [{
                    'episode num': '',
                    'episode title': '',
                    'channels': [show['channel']],
                    'first air date': date.today().strftime('%d-%m-%Y'),
                    'repeat': False
                }]
            }]
            if 'series_num' in show.keys():
                data[0]['season num'] = show['series_num']
            if 'episode_num' in show.keys():
                data[0]['episodes'][0]['episode num'] = show['episode_num']
            if 'episode_title' in show.keys():
                data[0]['episodes'][0]['episode title'] = show['episode_title']
            json.dump(data, fd, ensure_ascii=False, indent=4)
            fd.close()

    return data


def flag_repeats(show):

    file = read_file(show)
    if 'series_num' in show.keys():
        season_found = -1
        for season in file:
            if season['season num'] == show['series_num']:
                season_found = 1
                episodes = season['episodes']
                episode_found = -1
                for episode in episodes:
                    if episode['episode num'] == show['episode_num']:
                        episode_found = 1
                        if episode['first air date'] != date.today().strftime('%d-%m-%y'):
                            if show['channel'] in episode['channels']:
                                if 'ABC1' in show['channel']:
                                    episode['channels'].append('ABCHD')
                                if '10' in show['channel']:
                                    episode['channels'].append('TENHD')
                                episode['repeat'] = True
                            else:
                                if 'ABC1' in show['channel']:
                                    episode['channels'].append('ABCHD')
                                if '10' in show['channel']:
                                    episode['channels'].append('TENHD')
                                episode['channels'].append(show['channel'])
                                episode['repeat'] = True
                if episode_found == -1:
                    obj = {'episode num': show['episode_num'], 'episode title': '', 'channels': [show['channel']],
                           'first air date': date.strftime(date.today(), '%d-%m-%Y'), 'repeat': False}
                    if 'episode_title' in show.keys():
                        obj['episode title'] = show['episode_title']
                    season['episodes'].append(obj)
        if season_found == -1:
            obj = {'season num': show['series_num'], 'episodes': [
                {'episode num': show['episode_num'], 'episode title': '', 'channels': [show['channel']],
                 'first air date': date.strftime(date.today(), '%d-%m-%Y'), 'repeat': False}]}
            if 'episode_title' in show.keys():
                obj['episodes'][0]['episode title'] = show['episode_title']
            if 'ABC1' in show['channel']:
                obj['episodes'][0]['channels'].append('ABCHD')
            if '10' in show['channel']:
                obj['episodes'][0]['channels'].append('TENHD')
            file.append(obj)

    else:
        for season in file:
            episodes = season['episodes']
            found = -1
            for episode in episodes:
                if episode['episode title'] == show['episode_title']:
                    found = 1
                    if episode['first air date'] != date.today().strftime('%d-%m-%y'):
                        if show['channel'] in episode['channels']:
                            episode['repeat'] = True
                        else:
                            episode['channels'].append(show['channel'])
                            episode['repeat'] = True
            if found == -1:
                season['episodes'].append({'episode num': '', 'episode title': show['episode_title'],
                                           'channels': [show['channel']],
                                           'first air date': date.strftime(date.today(), '%d-%m-%Y'),
                                           'repeat': False})

    write_back_to_file({'title': show['title'], 'seasons': file})


def write_back_to_file(data):

    title = data['title']
    if ':' in title:
        idx = title.rfind(':')
        title = title[:idx] + title[idx+1:]
    with open('shows/' + title + '.json', 'w', encoding='utf-8') as fd:
        json.dump(data['seasons'], fd, ensure_ascii=False, indent=4)


def search_for_repeats(show):

    if 'GEM' in show['channel']:
        status = False
    else:
        status = True

    if status:
        file = read_file(show)

        for season in file:
            for episode in season['episodes']:
                if 'episode_title' in show.keys():
                    if episode['episode title'] == show['episode_title']:
                                show['repeat'] = True
                if 'series_num' in show.keys():
                    if season['season num'] == show['series_num']:
                        if episode['episode num'] == show['episode_num']:
                            show['repeat'] = True
