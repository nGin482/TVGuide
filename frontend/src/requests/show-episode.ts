
import { deleteRequest, getRequest, putRequest } from "./api-client";
import { ShowEpisode } from "../utils/types";

interface NeedsEpisodeRefresh {
  "needs_refresh": Boolean;
  "latest_season_recorded": number;
  "tvmaze_season_max": number;
}

export const checkEpisodes = async (showName: string) => {
  return await getRequest<NeedsEpisodeRefresh>(
    `/show-episode/check_episodes?show_title=${showName}`
  );
};

export const updateShowEpisode = async (episode: ShowEpisode) => {
  return await putRequest<ShowEpisode, ShowEpisode>(
    `/show-episode/${episode.id}`,
    episode
  );
};

export const deleteShowEpisode = async (episodeId: number) => {
  await deleteRequest(`/show-episode/${episodeId}`);
};
