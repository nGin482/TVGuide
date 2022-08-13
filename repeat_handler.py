from database.models.GuideShow import GuideShow
from database.models.RecordedShow import RecordedShow
from database.recorded_shows_collection import (
    get_all_recorded_shows, get_one_recorded_show,
    insert_new_recorded_show, insert_new_season, insert_new_episode,
    mark_as_repeat, add_channel, update_recorded_episode
)
from aux_methods.helper_methods import check_show_titles
import json
import os

def get_today_shows_data(list_of_shows):
    all_recorded_shows = get_all_recorded_shows()

    today_shows = [recorded_show for recorded_show in all_recorded_shows if recorded_show['show'] in list_of_shows]
    for show_data in today_shows:
        del show_data['_id']
        with open('shows/' + check_show_titles(show_data['show']) + '.json', 'w+') as file:
            json.dump(show_data, file, indent='\t')

def read_show_data(title: str):
    try:
        with open(f'shows/{title}.json') as filename:
            show_data = RecordedShow(json.load(filename))
        return show_data
    except FileNotFoundError:
        return None

def flag_repeats(show: GuideShow):
    print('running')

    show['title'] = check_show_titles(show)
    check_episode = show.find_recorded_episode()
    if check_episode['status']:
        set_repeat = mark_as_repeat(show)
        channel_add = add_channel(show)
        return {'show': show, 'repeat': set_repeat, 'channel': channel_add}
    else:
        if check_episode['level'] == 'Episode':
            insert_episode = insert_new_episode(show)
            update_JSON_file_episode(show, insert_episode['insert_episode_result']['episode'][0])
            return {'show': show, 'result': insert_episode}
        elif check_episode['level'] == 'Season':
            insert_season = insert_new_season(show)
            update_JSON_file_season(show['title'], insert_season['season'])
            return {'show': show, 'result': insert_season}
        elif check_episode['level'] == 'Show':
            insert_show = insert_new_recorded_show(show)
            return {'show': show, 'result': insert_show}
        # update the JSON file as these happen
        else:
            return {'status': False, 'message': 'Unable to process this episode.'}

def tear_down():
    """
    Remove the JSON files created to read show data from the shows directory 
    """

    for show_file in os.listdir('shows'):
        os.remove('shows/' + show_file)

def update_JSON_file_season(show: str, season: dict):

    data = read_show_data(show)['show']
    
    data['seasons'].append(season)

    with open('shows/' + show + '.json', 'w') as fd:
        json.dump(data, fd, indent='\t')

def update_JSON_file_episode(show: dict, episode: dict):
    
    data = read_show_data(show['title'])['show']

    if 'series_num' in show.keys():
        check_season = list(filter(lambda season: season['season number'] == show['series_num'], data['seasons']))
        if len(check_season) > 0:
            check_episode = list(filter(lambda season: season['episode number'] == show['episode_num'], check_season[0]['episodes']))
            if len(check_episode) == 0:
                check_season[0]['episodes'].append(episode)

    with open('shows/' + show['title'] + '.json', 'w') as fd:
        json.dump(data, fd, indent='\t')
