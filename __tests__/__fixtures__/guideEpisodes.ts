import GuideEpisode from "../../database/models/GuideEpisode";
import { GuideEpisode as TGuideEpisode } from "../../types";


export const testGuideEpisodeData: TGuideEpisode[] = [
  {
    id: 1,
    title: "Endeavour",
    channel: "ABC1",
    startTime: new Date("2026-10-22T20:30:00"),
    endTime: new Date("2026-10-22T22:00:00"),
    seasonNumber: 1,
    episodeNumber: 2,
    episodeTitle: "Fugue",
    repeat: true,
    dbEvent: null,
    guideId: 1,
    showId: 2,
    episodeId: 68,
    reminderId: 2,
  },
  {
    id: 2,
    title: "Merlin",
    channel: "ABC2",
    startTime: new Date("2026-10-22T22:57:00"),
    endTime: new Date("2026-10-22T23:44:00"),
    seasonNumber: 1,
    episodeNumber: 1,
    episodeTitle: "The Dragon's Call",
    repeat: true,
    dbEvent: null,
    guideId: 1,
    showId: 1,
    episodeId: 1,
    reminderId: 1,
  },
];


export const testGuideEpisodes = (
  overrides?: Partial<TGuideEpisode>[] | Partial<TGuideEpisode>
) => {
  return testGuideEpisodeData.map((guideEpisode, index) => {
    // 1. Determine if there is a specific override for this array index
    const indexOverride = Array.isArray(overrides) ? overrides[index] : overrides;

    // 2. Merge the base data with any overrides provided
    const mergedData = {
      ...guideEpisode,
      ...indexOverride,
    };

    // 3. Build and return the model
    return GuideEpisode.build({
      title: mergedData.title,
      channel: mergedData.channel,
      startTime: mergedData.startTime,
      endTime: mergedData.endTime,
      seasonNumber: mergedData.seasonNumber,
      episodeNumber: mergedData.episodeNumber,
      episodeTitle: mergedData.episodeTitle,
      repeat: mergedData.repeat,
      dbEvent: mergedData.dbEvent,
      guideId: mergedData.guideId,
      showId: mergedData.showId,
      episodeId: mergedData.episodeId,
      reminderId: mergedData.reminderId,
    });
  });
};
