from show import Show, Season, Episode
from datetime import date
from database import get_one_recorded_show, insert_new_recorded_show, insert_new_season, insert_new_episode, mark_as_repeat, add_channel
from aux_methods import check_show_titles
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


def flag_repeats(show):

    show['title'] = check_show_titles(show)
    check_episode = find_recorded_episode(show)
    if check_episode['status']:
        set_repeat = mark_as_repeat(show)
        channel_add = add_channel(show)
        return {'repeat': set_repeat, 'channel': channel_add}
    else:
        if check_episode['level'] == 'Episode':
            insert_episode = insert_new_episode(show)
            return insert_episode
        elif check_episode['level'] == 'Season':
            insert_season = insert_new_season(show)
            return insert_season
        elif check_episode['level'] == 'Show':
            insert_show = insert_new_recorded_show(show)
            return insert_show
        else:
            return {'status': False, 'message': 'Unable to process this episode.'}

def find_recorded_episode(show):
    check_show = get_one_recorded_show(show['title'])
    if check_show['status']:
        show_information = check_show['show']
        if 'series_num' in show.keys():
            show_season = list(filter(lambda season: season['season number'] == show['series_num'], show_information['seasons']))
            if len(show_season) > 0:
                episode_recorded = list(filter(lambda season: season['episode number'] == show['episode_num'], show_season[0]['episodes']))
                if len(episode_recorded) > 0:
                    return {'status': True, 'episode': episode_recorded[0]}
                else:
                    return {'status': False, 'level': 'Episode'}
            else:
                return {'status': False, 'level': 'Season'}
        else:
            show_season = list(filter(lambda season: season['season number'] == 'Unknown', show_information['seasons']))
            if len(show_season) > 0:
                episode_recorded = list(filter(lambda season: season['episode title'] == show['episode_title'], show_season[0]['episodes']))
                if len(episode_recorded) > 0:
                    return {'status': True, 'episode': episode_recorded[0]}
                else:
                    return {'status': False, 'level': 'Episode'}
            else:
                return {'status': False, 'level': 'Season'}
    else:
        return {'status': False, 'level': 'Show'}


def search_for_repeats(show):

    if 'GEM' in show['channel']:
        status = False
    else:
        status = True

    if status:
        check_episode = find_recorded_episode(show)
        if check_episode['status']:
            show['repeat'] = True
