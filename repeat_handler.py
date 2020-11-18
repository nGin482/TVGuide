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

    # print('-------------------------------------------------------------------------------')
    # prac = []
    # misc = []
    # for show in channel:
    #     sublist = sorted(channel, key=lambda show_obj: show_obj['title'] if show_obj['title'] == show['title']
    #                      else misc.append(show_obj))
    #     print(sublist)
    #     prac.append(sublist)
    # print(prac)
    # print('-------------------------------------------------------------------------------')
    
    # channel_sorted = sorted(channel, key=lambda show_obj: show_obj['title'])
    # channel_list = []
    # print(channel_sorted)
    # print(len(channel_sorted))
    # show_title = channel_sorted[0]['title']
    # show_list = []
    # for idx, s in enumerate(channel_sorted):
    #     print(str(idx) + ': ' + str(s))
    #     if s['title'] == show_title:
    #         show_list.append(s)
    #     else:
    #         show_list = []
    #         show_title = s['title']
    #     channel_list.append(show_list)
    # print('----------------------------------')
    # for c in channel_list:
    #     print(c)


def convert_to_objects(superlist):

    json_list = []
    # print('--------------------------------------------------------------------------------------------')
    for item in superlist:
        # print(item)
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
    # print('--------------------------------------------------------------------------------------------')
    # print('JSON list')
    for json_obj in json_list:
        json_obj.cleanup_unknowns()
        # print(json_obj.to_string())

    return json_list

# --------------------------------- FUNCTIONS BELOW THIS LINE AREN'T USED ----------------------------------------------


def collate_file_data(info):

    superlist = []
    get_shows(info, superlist)

    return superlist


def create_files(shows):

    paths = []
    for show in shows:
        title = show.title
        path = os.path.join('shows', title + ".json")
        if ':' in title:
            idx = path.rfind(':')
            path = path[:idx] + path[idx+1:]
        print(path)
        if os.path.exists(path):
            print(title + " exists")
        else:
            print(title + " doesn't exist")
            open(path, 'w+')
        paths.append(path)

    return paths


def write_to_files(shows):

    paths = create_files(shows)
    i = 0
    # print('--------------------------------------------------------------------------------------------')
    for show in shows:
        print(show.to_string())
        print('--------------------')
        if "GEM" not in show.title:
            show_dict = show.to_dict()
            seasons = show_dict['seasons']
            with open(paths[i], 'w', encoding='utf-8') as fd:
                json.dump(seasons, fd, ensure_ascii=False, indent=4)
            i += 1


def read_files():

    paths = os.listdir('shows')
    file_data = []
    i = 0
    while i < len(paths):
        with open('shows/' + paths[i], 'r') as fd:
            data = json.load(fd)

        data_list = []
        print(data)
        title = paths[i][:-5]
        for season in data:
            for episode in season['episodes']:
                obj = {
                    'title': title,
                    'series_num': season['season num'],
                    'episode_num': episode['episode num'],
                    'episode_title': episode['episode title'],
                    'channel': episode['channels']
                }
                data_list.append(obj)

        shows_list = collate_file_data(data_list)
        print()
        objects = convert_to_objects(shows_list)
        file_data.append(objects[0])
        i += 1

    return file_data

# def search_for_repeat(data):
#     file_data = read_file()
#     today_bbc = data['BBC']
#     today_fta = data['FTA']
#
#     print(file_data)
#     for obj in file_data:
#         for episode in today_bbc:
#             idx = obj.find_episode(episode)
#             if idx[1] != -1:
#                 obj.seasons[idx[0]].episodes[idx[1]].set_repeat()
#                 episode['repeat'] = True
#             elif idx[0] != -1 and idx[1] == -1:
#                 obj.seasons[idx[0]].create_episode(episode)
#         for episode in today_fta:
#             idx = obj.find_episode(episode)
#             if idx[1] != -1:
#                 obj.seasons[idx[0]].episodes[idx[1]].set_repeat()
#                 episode['repeat'] = True
#             elif idx[0] != -1 and idx[1] == -1:
#                 obj.seasons[idx[0]].create_episode(episode)
#
#     return file_data


# def file_to_object(dict_obj):
#
#     for season in dict_obj:
#         season_obj = Season(season)

# --------------------------------- FUNCTIONS ABOVE THIS LINE AREN'T USED ----------------------------------------------


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
                    'channels': show['channel'],
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

    # print('********************************************')
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
                        if 'Baptiste' in show['title']:
                            print('This is being printed to serve a reminder for Baptiste repeats for BBC First')
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
    # print(show['title'] + ' file written')


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
        # else:
        #     for season in file:
        #         if season['season num'] == 'Unknown':
        #             episodes = season['episodes']
        #             for episode in episodes:
        #                 
