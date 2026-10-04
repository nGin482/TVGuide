from services.APIClient import APIClient
from services.tvmaze.tvmaze_helpers import map_seasons
from utils.types.models import TShowEpisode
from tvguide_types.tvmaze import TVMazeEpisode, TVMazeSeason, TVMazeShow

api_client = APIClient()

def get_show(show: str):
    show_data: TVMazeShow = api_client.get(
        f'https://api.tvmaze.com/singlesearch/shows?q={show}'
    )

    return show_data

def get_show_seasons(tvmaze_id: str):
    api_data: list[TVMazeSeason] = api_client.get(
        f"https://api.tvmaze.com/shows/{tvmaze_id}/seasons"
    )

    return [season["number"] for season in api_data]

def get_show_episodes(
    tvmaze_id: str,
    season_start: int = 0,
    season_end: int = None,
    include_specials: bool = False
):
    url = f"https://api.tvmaze.com/shows/{tvmaze_id}/episodes"
    if include_specials:
        url += "?specials=1"
    tvmaze_episodes: list[TVMazeEpisode] = api_client.get(url)

    if tvmaze_episodes[0]['season'] > 1:
        tvmaze_episodes = map_seasons(tvmaze_episodes)

    tvmaze_episodes = [
        episode
        for episode in tvmaze_episodes
        if episode['season'] >= season_start
    ]

    if season_end is not None and season_end != 0:
        tvmaze_episodes = [
            episode
            for episode in tvmaze_episodes
            if episode['season'] <= season_end
        ]

    show_episodes: list[TShowEpisode] = []
    for show_episode in tvmaze_episodes:
        episode: TShowEpisode = {
            'show': show_episode['_links']['show']['name'],
            'season_number': show_episode['season'],
            'episode_number': show_episode['number'],
            'episode_title': show_episode['name'],
            'summary': show_episode['summary']
        }
        show_episodes.append(episode)

    return show_episodes
