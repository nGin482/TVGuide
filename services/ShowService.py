from sqlalchemy.orm import Session
import logging

from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from database.models.SearchItemModel import SearchItem
from services.tvmaze import tvmaze_api
from exceptions.service_error import HTTPRequestError
from exceptions.DatabaseError import ShowAlreadyExistsError
from utils.logging_formatter import logging_handler
from utils.types import NeedsEpisodeRefresh, ShowPayload
from utils.types.models import TShowData

logger = logging.getLogger("ShowService")
logger.addHandler(logging_handler)

class ShowService:

    def get_show_by_title(self, show_name: str, session: Session):
        show = ShowDetails.get_show_by_title(show_name, session)
        return show

    def add_show(self, body: ShowPayload, session: Session) -> TShowData:
        if self.get_show_by_title(body["name"], session):
            raise ShowAlreadyExistsError
    
        try:
            tvmaze_details = tvmaze_api.get_show(body["name"])
        except HTTPRequestError as error:
            raise HTTPRequestError(
                f"Could not find {body['name']} on TVMaze: {error}",
                error.status_code,
                error.status_text
            ) from error
        
        show_detail = ShowDetails(
            tvmaze_details["name"],
            tvmaze_details["summary"],
            tvmaze_details["id"],
            tvmaze_details["genres"],
            tvmaze_details["image"]["original"]
        )
        show_detail.add_show(session)
        
        conditions = body["conditions"]
        tvmaze_episodes = tvmaze_api.get_show_episodes(
            tvmaze_details["id"],
            conditions["min_season_number"],
            conditions["max_season_number"],
            True
            # NOTE: Currently including the specials as well by default
            # No way to set this from frontend
        )
        show_episodes: list[ShowEpisode] = []
        for episode in tvmaze_episodes:
            try:
                show_episode = ShowEpisode(
                    tvmaze_details["name"],
                    episode["season_number"],
                    episode["episode_number"],
                    episode["episode_title"],
                    episode["summary"],
                    show_id=show_detail.id
                )
                show_episodes.append(show_episode)
            except KeyError as error:
                logger.error(
                    f"Unable to add an episode for {tvmaze_details['name']}: {error}"
                )
                logger.error(episode)
        ShowEpisode.add_all_episodes(show_episodes, session)
    
        try:
            search_criteria = SearchItem(
                tvmaze_details["name"],
                conditions["exact_title_match"],
                conditions["max_season_number"],
                conditions,
                show_id=show_detail.id
            )
            search_criteria.add_search_item(session)
        except KeyError as error:
            logger.error(
                f"Unable to add search criteria for {tvmaze_details['name']}: {error}"
            )
    
        return {
            "show_name": show_detail.title,
            "show_details": show_detail.to_dict(),
            "show_episodes": [episode.to_dict() for episode in show_episodes],
            "search_item": search_criteria.to_dict() if search_criteria else None,
            "reminder": None
        }

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

    def fetch_latest_episodes(
        self,
        show: ShowDetails,
        episode_check: NeedsEpisodeRefresh,
        session: Session,
    ):
        episodes = tvmaze_api.get_show_episodes(
            show.tvmaze_id,
            episode_check["latest_season_recorded"] + 1,
            episode_check["tvmaze_season_max"],
        )

        show_episodes = [
            ShowEpisode(
                show.title,
                episode["season_number"],
                episode["episode_number"],
                episode["episode_title"],
                episode["summary"],
                [],
                [],
                [],
                show.id
            )
            for episode in episodes
        ]
        ShowEpisode.add_all_episodes(show_episodes, session)

        return {
            "episodes_added": len(episodes),
        }