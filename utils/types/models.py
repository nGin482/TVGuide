from datetime import datetime
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

TShowEpisode = TypedDict("TShowEpisode", {
    'id': str,
    'show': str,
    'season_number': int,
    'episode_number': int,
    'episode_title': str,
    'summary': str,
    'alternative_titles': list[str],
    'channels': list[str],
    'air_dates': list[datetime]
})

TSearchConditions = TypedDict("TSearchConditions", {
    'min_season_number': int,
    'max_season_number': int,
    'ignore_titles': list[str],
    'ignore_seasons': list[int],
    'ignore_episodes': list[str]
})

TSearchItem = TypedDict("TSearchItem", {
    'id': int,
    'show': str,
    'search_active': bool,
    'exact_title_match': bool,
    'conditions': TSearchConditions
})

TReminder = TypedDict("TReminder", {
    'show': str,
    'alert': str,
    'warning_time': int,
    'occasions': str
})

TShowDetails = TypedDict("TShowDetails", {
    'title': str,
    'description': str,
    'tvmaze_id': str,
    'genres': list[str],
    'image': str
})

TShowData = TypedDict("TShowData", {
    "show_name": str,
    "show_details": TShowDetails,
    "search_item": TSearchItem | None,
    "show_episodes": list[TShowEpisode],
    "reminder": TReminder | None
})
