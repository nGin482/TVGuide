import GuideEpisode from "../../database/models/GuideEpisode";
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

export const testCreatedShowEpisode = (guideEpisode: GuideEpisode) => {
  return ShowEpisode.build({
    show: guideEpisode.title,
    seasonNumber: guideEpisode.seasonNumber,
    episodeNumber: guideEpisode.episodeNumber,
    episodeTitle: guideEpisode.episodeTitle,
    summary: "",
    alternativeTitles: [],
    airDates: [guideEpisode.startTime],
    channels: [guideEpisode.channel],
    showId: guideEpisode.showId,
  })
}
