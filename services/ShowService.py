from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from services.tvmaze import tvmaze_api

class ShowService:

    def get_show_by_title(self, show_name: str, session: Session):
        show = ShowDetails.get_show_by_title(show_name, session)
        return show

    def needs_episode_refresh(self, show: ShowDetails):
        show_episodes = show.show_episodes
        recorded_season_numbers = [
            show_episode.season_number
            for show_episode in show_episodes
        ]
        latest_season_recorded = max(recorded_season_numbers)

        season_list = tvmaze_api.get_show_seasons(show.tvmaze_id)
        tvmaze_season_max = max(season_list)

        if latest_season_recorded < tvmaze_season_max:
            return True
        return False