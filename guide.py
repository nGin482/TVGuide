from datetime import datetime
import json

def sort_shows_by_title(fta_shows, bbc_shows):
    """
    Bundles the episodes together according to their show title
    """
    all_shows = []

    all_shows.extend(fta_shows)
    all_shows.extend(bbc_shows)

    list_sorted_shows = []
    new_list = []
    for show in all_shows:
        if show['title'] not in list_sorted_shows:
            temp_filter = list(filter(lambda shows_discovered: shows_discovered['title'] == show['title'], all_shows))
            new_list.append(temp_filter)
            list_sorted_shows.append(show['title'])

    return new_list

def organise_guide(fta_shows, bbc_shows):
    sorted_shows = sort_shows_by_title(fta_shows, bbc_shows)

    guide = []
    for show in sorted_shows:
        # organise_seasons(show)
        show_object = {
            'title': show[0]['title'],
            'seasons': []
        }
        for episode in show:
            if 'series_num' not in episode.keys():
                episode['series_num'] = 'Unknown'
            if 'episode_num' not in episode.keys():
                episode['episode_num'] = ''
            if 'episode_title' not in episode.keys():
                episode['episode_title'] = ''
                    
            season_idx = find_season(show_object['seasons'], episode['series_num'])
            if season_idx == -1:
                season_object = {
                    'season num': episode['series_num'],
                    'episodes': [{
                        'episode num': episode['episode_num'],
                        'episode title': episode['episode_title'],
                        'time': episode['time'],
                        'channels': [episode['channel']],
                        'first air date': datetime.strftime(datetime.today(), '%d-%m-%Y'),
                        'repeat': episode['repeat']
                    }]
                }
                show_object['seasons'].append(season_object)
            else:
                episode_idx = find_episode(show_object['seasons'][season_idx]['episodes'], episode['episode_num'], episode['episode_title'])
                if episode_idx == -1:
                    episode_object = {
                        'episode num': episode['episode_num'],
                        'episode title': episode['episode_title'],
                        'time': episode['time'],
                        'channels': [episode['channel']],
                        'first air date': datetime.strftime(datetime.today(), '%d-%m-%Y'),
                        'repeat': episode['repeat']
                    }
                    show_object['seasons'][season_idx]['episodes'].append(episode_object)
                else:
                    channels = show_object['seasons'][season_idx]['episodes'][episode_idx]['channels']
                    if not check_channel(channels, episode['channel']):
                        show_object['seasons'][season_idx]['episodes'][episode_idx]['channels'].append(episode['channel'])
                    show_object['seasons'][season_idx]['episodes'][episode_idx]['repeat'] = True
            check_unknown_season(show_object['seasons'], episode)
        cleanup_unknown_season(show_object['seasons'])
        guide.append(show_object)

    return guide

def find_season(seasons, season_number):
    for idx, season in enumerate(seasons):
        if season_number in season['season num']:
            return idx
    return -1

def find_episode(episodes, episode_number, episode_title):
    if episode_title == '':
        for idx, episode in enumerate(episodes):
            if episode_number in episode['episode num']:
                return idx
        return -1
    elif episode_number == '':
        for idx, episode in enumerate(episodes):
            if episode_title in episode['episode title']:
                return idx
        return -1
    else:
        return False

def check_channel(channels, episode_channel):
    for channel in channels:
        if episode_channel in channel:
            return True
    return False

def check_unknown_season(seasons, ep):
    if len(seasons) > 1:
        find_unknown_season = list(filter(lambda season: season['season num'] == 'Unknown', seasons))
        if len(find_unknown_season) > 0:
            unknown_season = find_unknown_season[0]
            for idx, unknown_episode in enumerate(unknown_season['episodes']):
                for season in seasons:
                    does_episode_exist = find_episode(season['episodes'], unknown_episode['episode num'], unknown_episode['episode title'])
                    if does_episode_exist != -1:
                        if check_channel(season['episodes'][does_episode_exist]['channels'], unknown_episode['channels'][0]):
                            ep['repeat'] = True
                        else:
                            season['episodes'][does_episode_exist]['channels'].append(ep['channel'])
                        unknown_episode['copy exists'] = True

def cleanup_unknown_season(seasons):
    copy_count = 0
    unknown_idx = -1
    find_unknown_season = None
    for idx, season in enumerate(seasons):
        if season['season num'] == 'Unknown':
            unknown_idx = idx
            find_unknown_season = season
            for episode in season['episodes']:
                if 'copy exists' in episode.keys():
                    copy_count += 1
    if unknown_idx != -1 and copy_count == len(find_unknown_season['episodes']):
        seasons.pop(unknown_idx)


# possible alternative to organise seasons
# all episodes are listed with their respective seasons
# the same episodes are listed multiple times if episode is shown more than once
def organise_seasons(episodes):
    show_seasons = []
    available_seasons = []
    for episode in episodes:
        season = episode['series_num']
        if season not in available_seasons:
            available_seasons.append(season)
    print(available_seasons)
    for season in available_seasons:
        season_list = list(filter(lambda episode: episode['series_num'] == season, episodes)) 
        # print(season_list)
        season_object = {
            'season number': season_list[0]['series_num'],
            'episodes': []
        }
        for episode in season_list:
            episode_object = {
                'episode number': episode['episode_num'],
                'episode title': episode['episode_title'],
                'time': episode['time'],
                'channels': [episode['channel']],
                'first air date': datetime.strftime(datetime.today(), '%d-%m-%Y'),
                'repeat': False
            }
            season_object['episodes'].append(episode_object)
        print(season_object)
        print()
    # seasons = list(filter(lambda episode: episode['series_num'] == show['title'], episodes))
