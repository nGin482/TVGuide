from datetime import datetime
from typing import TypedDict

ShowData = TypedDict('ShowData', {
    'title': str,
    'channel': str,
    'start_time': datetime,
    'end_time': datetime,
    'season_number': int,
    'episode_number': int,
    'episode_title': str
})

ShowPayloadConditions = TypedDict("ShowPayloadConditions", {
    "min_season_number": int,
    "max_season_number": int,
    "exact_title_match": True,
    "ignore_titles": list[str],
    "ignore_seasons": list[str],
    "ignore_episodes": list[str],
})

ShowPayload = TypedDict("ShowPayload", {
    "name": str,
    "conditions": ShowPayloadConditions,
    "include_specials": bool,
})

NeedsEpisodeRefresh = TypedDict("NeedsEpisodeRefresh", {
    "needs_refresh": bool,
    "latest_season_recorded": int,
    "tvmaze_season_max": int,
})