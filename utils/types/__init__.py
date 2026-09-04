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