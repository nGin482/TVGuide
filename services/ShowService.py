from sqlalchemy.orm import Session
from typing import TypedDict

from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from services.tvmaze import tvmaze_api

NeedsEpisodeRefresh = TypedDict("NeedsEpisodeRefresh", {
    "needs_refresh": bool,
    "latest_season_recorded": int,
    "tvmaze_season_max": int,
})

class ShowService:

    def get_show_by_title(self, show_name: str, session: Session):
        show = ShowDetails.get_show_by_title(show_name, session)
        return show

    def needs_episode_refresh(self, show: ShowDetails) -> NeedsEpisodeRefresh:
        show_episodes = show.show_episodes
        recorded_season_numbers = [
            show_episode.season_number
            for show_episode in show_episodes
        ]
        latest_season_recorded = max(recorded_season_numbers)

        season_list = tvmaze_api.get_show_seasons(show.tvmaze_id)
        tvmaze_season_max = max(season_list)

        return {
            "needs_refresh": True if latest_season_recorded < tvmaze_season_max else False,
            "latest_season_recorded": latest_season_recorded,
            "tvmaze_season_max": tvmaze_season_max,
        }

    def fetch_latest_episodes(self, show: ShowDetails):
        pass