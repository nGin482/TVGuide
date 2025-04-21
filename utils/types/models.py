from typing import TypedDict

TGuideEpisode = TypedDict("GuideEpisode", {
    'title': str,
    'start_time': str,
    'end_time': str,
    'channel': str,
    'season_number': int,
    'episode_number': int,
    'episode_title': str,
    'repeat': bool,
    'db_event': str
})

TGuide = TypedDict("Guide", {
    'date': str,
    'fta': list[TGuideEpisode]
})
