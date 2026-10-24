import Guide from "../../../database/models/Guide";
import GuideEpisode from "../../../database/models/GuideEpisode";
import Reminder from "../../../database/models/Reminder";
import ShowDetails from "../../../database/models/ShowDetails";
import ShowEpisode from "../../../database/models/ShowEpisode";
import { convertDate } from "../../../utils";

import { testCreatedShowEpisode, testShowEpisodes } from "../../__fixtures__/showEpisodes";

jest.mock("../../../utils", () => ({
  convertDate: jest.fn(),
}));

const mockedConvertDate = jest.mocked(convertDate);


describe("GuideEpisode", () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  describe("associate", () => {
    it("associates the ShowEpisode model to other models", () => {
      const belongsToSpy = jest.spyOn(GuideEpisode, "belongsTo");

      GuideEpisode.associate();

      expect(belongsToSpy).toHaveBeenCalledWith(
        Guide,
        expect.objectContaining({
          foreignKey: "guide_id",
        }),
      );
      expect(belongsToSpy).toHaveBeenCalledWith(
        ShowDetails,
        expect.objectContaining({
          foreignKey: "show_id",
          as: "showDetails",
        }),
      );
      expect(belongsToSpy).toHaveBeenCalledWith(
        ShowEpisode,
        expect.objectContaining({
          foreignKey: "episode_id",
          as: "showEpisode",
        }),
      );
      expect(belongsToSpy).toHaveBeenCalledWith(
        Reminder,
        expect.objectContaining({
          foreignKey: "reminder_id",
          as: "reminder",
        }),
      );
    });
  });

  describe("captureDBEvent", () => {
    const startTime = new Date("2026-10-22T20:30:00");
    const testGuideEpisode = GuideEpisode.build({
      title: "Endeavour",
      channel: "ABC1",
      startTime: startTime,
      endTime: new Date("2026-10-22T22:00:00"),
      seasonNumber: 1,
      episodeNumber: 2,
      episodeTitle: "Fugue",
      repeat: true,
      guideId: 1,
      showId: 2,
    });

    it("adds the air date and checks the show's channel", async () => {
      mockedConvertDate.mockReturnValueOnce(startTime);
      const updateSpy = jest.spyOn(GuideEpisode.prototype, "update")
        .mockImplementationOnce(() => {
          return Promise.resolve(testGuideEpisode)
        });
      const setSpy = jest.spyOn(ShowEpisode.prototype, "set");
      jest.spyOn(ShowEpisode.prototype, "save")
        .mockResolvedValueOnce(testShowEpisodes[0]);
      const checkChannelSpy = jest.spyOn(ShowEpisode.prototype, "checkChannel")
        .mockReturnValueOnce([]);
      testGuideEpisode.showEpisode = testShowEpisodes[0];

      await testGuideEpisode.captureDBEvent();
      
      expect(updateSpy).toHaveBeenCalledWith({
        dbEvent: "Season 1, Episode 2: Fugue has aired today",
      });
      expect(setSpy).toHaveBeenNthCalledWith(
        1,
        "airDates",
        [startTime],
      );
      expect(checkChannelSpy).toHaveBeenCalledWith("ABC1");
    });

    it("adds channels to the ShowEpisode", async () => {
      mockedConvertDate.mockReturnValueOnce(startTime);
      const updateSpy = jest.spyOn(GuideEpisode.prototype, "update")
        .mockImplementationOnce(() => {
          return Promise.resolve(testGuideEpisode)
        });
      const setSpy = jest.spyOn(ShowEpisode.prototype, "set");
      jest.spyOn(ShowEpisode.prototype, "save")
        .mockResolvedValueOnce(testShowEpisodes[0]);
      testGuideEpisode.showEpisode = testShowEpisodes[0];

      await testGuideEpisode.captureDBEvent();
      
      expect(updateSpy).toHaveBeenCalledWith({
        dbEvent: "ABC1 has been added to the channel list",
      });
      expect(setSpy).toHaveBeenNthCalledWith(
        2,
        "channels",
        ["ABC1"],
      );
    });

    it("creates a new ShowEpisode if one isn't linked", async () => {
      mockedConvertDate.mockReturnValueOnce(startTime);
      const updateSpy = jest.spyOn(GuideEpisode.prototype, "update")
        .mockImplementationOnce(() => {
          return Promise.resolve(testGuideEpisode)
        });
      const createSpy = jest.spyOn(ShowEpisode, "create")
        .mockImplementationOnce(() => {
          return Promise.resolve({
            ...testCreatedShowEpisode(testGuideEpisode),
            id: 1,
          });
        }
      );
      testGuideEpisode.showEpisode = null;

      await testGuideEpisode.captureDBEvent();
      
      expect(updateSpy).toHaveBeenCalledWith({
        dbEvent: "Season 1, Episode 2: Fugue has been inserted",
        episodeId: 1,
      });
      expect(createSpy).toHaveBeenCalledWith({
        show: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "Fugue",
        summary: "",
        alternativeTitles: [],
        airDates: [startTime],
        channels: ["ABC1"],
        showId: 2,
      });
    });
  });

  describe("getMessageString", () => {
    const guideEpisode = GuideEpisode.build({
      title: "Endeavour",
      channel: "ABC1",
      startTime: new Date("2026-10-22T20:30:00"),
      endTime: new Date("2026-10-22T22:00:00"),
      seasonNumber: 1,
      episodeNumber: 2,
      episodeTitle: "Fugue",
      repeat: false,
      guideId: 1,
      showId: 2,
    });

    it("returns the message for the show", () => {
      const message = guideEpisode.getMessageString();

      expect(message).toEqual(
        "20:30: Endeavour is on ABC1 (Season 1, Episode 2: Fugue)"
      );
    });

    it("tags an episode as a repeat in the message", () => {
      const testGuideEpisode = GuideEpisode.build({
        title: "Endeavour",
        channel: "ABC1",
        startTime: new Date("2026-10-22T20:30:00"),
        endTime: new Date("2026-10-22T22:00:00"),
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "Fugue",
        repeat: true,
        guideId: 1,
        showId: 2,
      });
      
      const message = testGuideEpisode.getMessageString();

      expect(message).toEqual(
        "20:30: Endeavour is on ABC1 (Season 1, Episode 2: Fugue) (Repeat)"
      );
    });
  });

  describe("getEpisodeString", () => {
    it("returns the episode portion of a guide episode's message", () => {
      const testGuideEpisode = GuideEpisode.build({
        title: "Endeavour",
        channel: "ABC1",
        startTime: new Date("2026-10-22T20:30:00"),
        endTime: new Date("2026-10-22T22:00:00"),
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "Fugue",
        repeat: true,
        guideId: 1,
        showId: 2,
      });

      const episodeMessage = testGuideEpisode.getEpisodeString();

      expect(episodeMessage).toEqual("Season 1, Episode 2: Fugue");
    });

    it("handles when an episode doesn't have a title", () => {
      const testGuideEpisode = GuideEpisode.build({
        title: "Endeavour",
        channel: "ABC1",
        startTime: new Date("2026-10-22T20:30:00"),
        endTime: new Date("2026-10-22T22:00:00"),
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "",
        repeat: true,
        guideId: 1,
        showId: 2,
      });

      const episodeMessage = testGuideEpisode.getEpisodeString();

      expect(episodeMessage).toEqual("Season 1, Episode 2");
    });

    it("returns the episode portion in a user-friendly format", () => {
      const testGuideEpisode = GuideEpisode.build({
        title: "Endeavour",
        channel: "ABC1",
        startTime: new Date("2026-10-22T20:30:00"),
        endTime: new Date("2026-10-22T22:00:00"),
        seasonNumber: -1,
        episodeNumber: 2,
        episodeTitle: "Fugue",
        repeat: true,
        guideId: 1,
        showId: 2,
      });

      const episodeMessage = testGuideEpisode.getEpisodeString();

      expect(episodeMessage).toEqual("Season Unknown, Episode 2: Fugue");
    });

    it("overrides the unknown default", () => {
      const testGuideEpisode = GuideEpisode.build({
        title: "Endeavour",
        channel: "ABC1",
        startTime: new Date("2026-10-22T20:30:00"),
        endTime: new Date("2026-10-22T22:00:00"),
        seasonNumber: -1,
        episodeNumber: 2,
        episodeTitle: "Fugue",
        repeat: true,
        guideId: 1,
        showId: 2,
      });

      const episodeMessage = testGuideEpisode.getEpisodeString(true);

      expect(episodeMessage).toEqual("Season -1, Episode 2: Fugue");
    });
  });
});
