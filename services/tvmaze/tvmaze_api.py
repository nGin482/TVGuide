from services.APIClient import APIClient
from services.tvmaze.tvmaze_helpers import format_episode_title, group_seasons, map_seasons
from tvguide_types.tvmaze import TVMazeEpisode, TVMazeShow

api_client = APIClient()

def get_show(show: str):
    show_data: TVMazeShow = api_client.get(f'https://api.tvmaze.com/singlesearch/shows?q={show}')

    return show_data

def get_show_episodes(tvmaze_id: str, season_start: int = 0, season_end: int = None, include_specials: bool = False):
    if include_specials:
        api_data: list[TVMazeEpisode] = api_client.get(
            f'https://api.tvmaze.com/shows/{tvmaze_id}/episodes?specials=1'
        )
    else:
        api_data: list[TVMazeEpisode] = api_client.get(
            f'https://api.tvmaze.com/shows/{tvmaze_id}/episodes'
        )

    if api_data[0]['season'] > 1:
        api_data = map_seasons(api_data)
    show_episodes = [episode for episode in api_data if episode['season'] >= season_start]

    if season_end:
        show_episodes = [episode for episode in show_episodes if episode['season'] <= season_end]

    for idx, show_episode in enumerate(show_episodes):
        episode = {
            'show': show_episode['_links']['show']['name'],
            'season_number': show_episode['season'],
            'episode_number': show_episode['number'],
            'episode_title': show_episode['name'],
            'summary': show_episode['summary']
        }
        show_episodes[idx] = episode

    return show_episodes

def get_show_data(show: str, tvmaze_id: str, season_start: int = 0, include_specials: bool = False):
    if include_specials:
        api_data = APIClient.get(f'https://api.tvmaze.com/shows/{tvmaze_id}/episodes?specials=1')
    else:
        api_data = APIClient.get(f'https://api.tvmaze.com/shows/{tvmaze_id}/episodes')
    episode_list = []
    show_details = {
        'show': show,
        'seasons': [],
        'tvmaze_id': tvmaze_id
    }
    for api_episode in api_data:
        if api_episode['season'] >= season_start:
            episode = {
                'season_number': api_episode['season'],
                'episode_number': api_episode['number'],
                'episode_title': format_episode_title(api_episode['name']),
                'alternative_titles': [],
                'summary': api_episode['summary'],
                'channels': [],
                'air_dates': []
            }
            episode_list.append(episode)

    if api_data[0]['season'] != 1 and season_start == 0:
        season_start = api_data[0]['season'] - 1

    show_details['seasons'] = group_seasons(episode_list, api_data[-1]['season'], season_start)
    return show_details

