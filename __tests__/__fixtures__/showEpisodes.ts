import ShowEpisode from "../../database/models/ShowEpisode";
import { ShowEpisode as TShowEpisode } from "../../types";

export const testShowEpisodeData: TShowEpisode[] = [
  {
    id: 1,
    show: "Endeavour",
    seasonNumber: 1,
    episodeNumber: 1,
    episodeTitle: "Pilot",
    summary: "",
    alternativeTitles: [],
    airDates: [],
    channels: [],
    showId: 1,
  },
];

export const testShowEpisodes: ShowEpisode[] = testShowEpisodeData.map(
  showEpisode => ShowEpisode.build(showEpisode)
);
