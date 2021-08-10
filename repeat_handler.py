from datetime import date
from database import get_one_recorded_show, insert_new_recorded_show, insert_new_season, insert_new_episode, mark_as_repeat, add_channel
from aux_methods import check_show_titles

def flag_repeats(show):

    show['title'] = check_show_titles(show)
    check_episode = find_recorded_episode(show)
    if check_episode['status']:
        set_repeat = mark_as_repeat(show)
        channel_add = add_channel(show)
        return {'show': show, 'repeat': set_repeat, 'channel': channel_add}
    else:
        if check_episode['level'] == 'Episode':
            insert_episode = insert_new_episode(show)
            return {'show': show, 'result': insert_episode}
        elif check_episode['level'] == 'Season':
            insert_season = insert_new_season(show)
            return {'show': show, 'result': insert_season}
        elif check_episode['level'] == 'Show':
            insert_show = insert_new_recorded_show(show)
            return {'show': show, 'result': insert_show}
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

    return show
