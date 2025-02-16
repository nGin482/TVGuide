from tvguide_types.tvmaze import TVMazeEpisode

def format_episode_title(episode_title: str):
    if '(Part ' in episode_title:
        episode_title = episode_title.replace('(Part ', 'Part ')
        episode_title = episode_title.replace(')', '')
    if 'Part I' in episode_title and 'Part II' not in episode_title:
        episode_title = episode_title.replace('I', '1')
    if 'Part II' in episode_title:
        episode_title = episode_title.replace('II', '2')

    return episode_title

def group_seasons(episode_list: list, num_of_seasons: int, season_start: int = 0):
    grouped_seasons = []
    for num in range(season_start, num_of_seasons):
        season_list = [episode for episode in episode_list if episode['season_number'] == num+1]
        season_obj = {
            'season_number': num+1,
            'episodes': season_list
        }
        grouped_seasons.append(season_obj)
        
    for season in grouped_seasons:
        for ep in season['episodes']:
            del ep['season_number']

    return grouped_seasons

def map_seasons(episode_list: list[TVMazeEpisode]):

    season_numbers = list(set([episode['season'] for episode in episode_list]))

    season_map = {}
    for idx, season in enumerate(season_numbers):
        season_map[str(season)] = idx + 1
    print(season_map)

    for episode in episode_list:
        episode['season'] = season_map[str(episode['season'])]

    return episode_list