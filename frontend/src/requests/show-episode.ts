
import { deleteRequest, getRequest, putRequest } from "./api-client";
import { ShowEpisode } from "../utils/types";

export const checkEpisodes = async (showName: string) => {
  return await getRequest<{ needs_refresh: boolean }>(
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
