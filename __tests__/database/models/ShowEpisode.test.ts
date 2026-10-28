import GuideEpisode from "../../../database/models/GuideEpisode";
import ShowDetails from "../../../database/models/ShowDetails";
import ShowEpisode from "../../../database/models/ShowEpisode";

import { testShowEpisodes } from "../../__fixtures__/showEpisodes";


describe("ShowEpisodeModel", () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  describe("associate", () => {
    it("associates the ShowEpisode model to other models", () => {
      const belongsToSpy = jest.spyOn(ShowEpisode, "belongsTo");
      const hasManySpy = jest.spyOn(ShowEpisode, "hasMany");

      ShowEpisode.associate();

      expect(belongsToSpy).toHaveBeenCalledWith(
        ShowDetails,
        expect.objectContaining({
          foreignKey: "show_id",
          as: "showDetails",
        }),
      );
      expect(hasManySpy).toHaveBeenCalledWith(
        GuideEpisode,
        expect.objectContaining({
          foreignKey: "episode_id",
          as: "guideEpisodes",
        }),
      );
    });
  });

  describe("findShowEpisode", () => {
    it("finds a show episode by season/episode numbers", async () => {
      const spy = jest.spyOn(ShowEpisode, "findOne")
        .mockResolvedValueOnce(testShowEpisodes[0]);

      const showEpisode = await ShowEpisode.findShowEpisode({
        title: "Endeavour",
        channel: "ABC1",
        start_time: new Date("2026-10-21T20:30:00"),
        end_time: new Date("2026-10-21T22:00:00"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Pilot",
      });

      expect(ShowEpisode.findOne).toHaveBeenCalledWith({
        where: {
          show: "Endeavour",
          seasonNumber: 1,
          episodeNumber: 1,
        },
      })
      expect(showEpisode).toEqual(testShowEpisodes[0]);
    });

    it("finds a show episode by episode title", async () => {
      const spy = jest.spyOn(ShowEpisode, "findOne")
        .mockResolvedValueOnce(testShowEpisodes[0]);

      const showEpisode = await ShowEpisode.findShowEpisode({
        title: "Endeavour",
        channel: "ABC1",
        start_time: new Date("2026-10-21T20:30:00"),
        end_time: new Date("2026-10-21T22:00:00"),
        season_number: -1,
        episode_number: 0,
        episode_title: "Pilot",
      });

      expect(ShowEpisode.findOne).toHaveBeenCalledWith({
        where: {
          show: "Endeavour",
          episodeTitle: "Pilot",
        },
      })
      expect(showEpisode).toEqual(testShowEpisodes[0]);

      spy.mockRestore();
    });

    it("returns null when show data doesn't have episode info", async () => {
      const showEpisode = await ShowEpisode.findShowEpisode({
        title: "Death In Paradise",
        channel: "GEM",
        start_time: new Date("2026-10-21T19:30:00"),
        end_time: new Date("2026-10-21T20:30:00"),
        season_number: -1,
        episode_number: 0,
        episode_title: "",
      });

      expect(showEpisode).toBeNull();
    });
  });

  describe("checkChannel", () => {
    it("returns an empty array if the channel is not missing", () => {
      const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: ["7TWO"],
        showId: 1,
      });

      const result = showEpisode.checkChannel("7TWO");

      expect(result).toHaveLength(0);
    });

    it("returns an array with the channel if it's missing", () => {
      const showEpisode = ShowEpisode.build({
        show: "Merlin",
        seasonNumber: 4,
        episodeNumber: 6,
        episodeTitle: "A Servant of Two Masters",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: [],
        showId: 1,
      });

      const result = showEpisode.checkChannel("ABC2");

      expect(result).toEqual(["ABC2"]);
    });

    it("checks ABCHD if the channel is ABC1", () => {
       const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: ["ABC1"],
        showId: 1,
      });

      const result = showEpisode.checkChannel("ABC1");

      expect(result).toEqual(["ABCHD"]);
    });

    it("checks SBSHD if the channel is SBS", () => {
       const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: ["SBS"],
        showId: 1,
      });

      const result = showEpisode.checkChannel("SBS");

      expect(result).toEqual(["SBSHD"]);
    });

    it("checks TENHD if the channel is 10", () => {
       const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: ["10"],
        showId: 1,
      });

      const result = showEpisode.checkChannel("10");

      expect(result).toEqual(["TENHD"]);
    });
  });

  describe("addChannels", () => {
    it("adds channels to the show episode", async () => {
      const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: [],
        showId: 1,
      });
      const setSpy = jest.spyOn(ShowEpisode.prototype, "set");

      const result = showEpisode.addChannels(["ABC1"]);

      expect(showEpisode.channels).toContain("ABC1");
      expect(setSpy).toHaveBeenCalledWith("channels", ["ABC1"]);
      expect(result).toEqual("ABC1 has been added to the channel list");
    });

    it("adds multiple channels to the show episode", async () => {
      const showEpisode = ShowEpisode.build({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
        summary: "",
        alternativeTitles: [],
        airDates: [],
        channels: [],
        showId: 1,
      });
      const setSpy = jest.spyOn(ShowEpisode.prototype, "set");

      const result = showEpisode.addChannels(["ABC1", "ABCHD"]);

      expect(showEpisode.channels).toContain("ABC1");
      expect(showEpisode.channels).toContain("ABCHD");
      expect(setSpy).toHaveBeenCalledWith("channels", ["ABC1", "ABCHD"]);
      expect(result).toEqual("ABC1, ABCHD have been added to the channel list");
    });
  });
});
