import axios from "axios";
import dayjs from "dayjs";

import Guide from "../../database/models/Guide";
import GuideEpisode from "../../database/models/GuideEpisode";
import SearchItem from "../../database/models/SearchItem";
import ShowDetails from "../../database/models/ShowDetails";
import ShowEpisode from "../../database/models/ShowEpisode";
import GuideService from "../../services/GuideService";
import { convertDate, formatDate } from "../../utils";

import { testABCGuide } from "../__fixtures__/abcGuide";
import { testGuideEpisodes } from "../__fixtures__/guideEpisodes";
import { testSearchItems } from "../__fixtures__/searchItems";
import { testShowDetails } from "../__fixtures__/showDetails";
import { testShowEpisodeData, testShowEpisodes } from "../__fixtures__/showEpisodes";

jest.mock("axios");
jest.mock("../../utils", () => {
  const actualUtils = jest.requireActual("../../utils");
  return {
    ...actualUtils,
    convertDate: jest.fn(),
    formatDate: jest.fn(),
  };
});

const mockedAxios = jest.mocked(axios);

const mockedConvertDate = jest.mocked(convertDate);
const mockedFormatDate = jest.mocked(formatDate);


describe("GuideService", () => {
  const guideService = new GuideService();

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe("createNewGuide", () => {
    beforeEach(() => {
      jest.spyOn(console, "log").mockImplementation();
    });

    it("creates a new guide", async () => {
      const date = dayjs("2026-10-25T09:00:00");
      const testGuide = Guide.build({
        date: date.toDate(),
      });

      const searchFTAGuideSpy = jest.spyOn(
        GuideService.prototype,
        "searchFTAGuide"
      ).mockResolvedValueOnce(undefined);
      const mockReload = jest
        .spyOn(Guide.prototype, "reload")
        .mockImplementationOnce(() => {
          testGuide.shows = testGuideEpisodes([
            { dbEvent: "Season 1, Episode 2 has aired today" },
            { dbEvent: "Season 1, Episode 1 (The Dragon's Call) has been inserted" },
          ]);
          return Promise.resolve(testGuide);
        });
      jest.spyOn(Guide, "create").mockResolvedValueOnce(testGuide);
      jest.spyOn(Guide.prototype, "findUpcomingReminders").mockReturnValueOnce([]);
      mockedFormatDate.mockReturnValueOnce(date.format("DD MM YYYY"));
      
      await guideService.createNewGuide(date);

      expect(searchFTAGuideSpy).toHaveBeenCalled();
      expect(mockReload).toHaveBeenCalled();
    });

    it("logs the guide messages", async () => {
      const date = dayjs("2026-10-25T09:00:00");
      const testGuide = Guide.build({
        date: date.toDate(),
      });

      const reminderMessage = `## Reminders
REMINDER: Endeavour is on ABC1 at 20:30.
You will be reminded at 20:27
REMINDER: Merlin is on ABC2 at 22:00.
You will be reminded at 21:55`;

      jest.spyOn(GuideService.prototype, "searchFTAGuide").mockResolvedValueOnce();
      jest.spyOn(Guide.prototype, "reload")
        .mockImplementationOnce(() => {
          testGuide.shows = testGuideEpisodes([
            { dbEvent: "Season 1, Episode 2 has aired today" },
            { dbEvent: "Season 1, Episode 1 (The Dragon's Call) has been inserted" },
          ]);
          return Promise.resolve(testGuide);
        });
      jest.spyOn(Guide, "create").mockResolvedValueOnce(testGuide);
      jest.spyOn(Guide.prototype, "composeReminderMessage")
        .mockReturnValueOnce(reminderMessage);
      mockedFormatDate
        .mockReturnValueOnce(date.format("dddd DD MM YYYY"))
        .mockReturnValueOnce(date.format("dddd DD MM YYYY"));
      const consoleSpy = jest.spyOn(console, "log");
      
      await guideService.createNewGuide(date);

      expect(consoleSpy).toHaveBeenNthCalledWith(
        1,
        `# Sunday 25 10 2026 TVGuide

Free to Air:
* 20:30: Endeavour is on ABC1 (Season 1, Episode 2: Fugue) (Repeat)
* 22:57: Merlin is on ABC2 (Season 1, Episode 1: The Dragon's Call) (Repeat)
`
      );
      expect(consoleSpy).toHaveBeenNthCalledWith(
        3,
        reminderMessage
      );
      expect(consoleSpy).toHaveBeenNthCalledWith(
        5,
        `# Events - Sunday 25 10 2026
* Endeavour - Season 1, Episode 2 has aired today
* Merlin - Season 1, Episode 1 (The Dragon's Call) has been inserted`
      );
    });
  });

  describe("searchFTAGuide", () => {
    it("searches the ABC guide for what shows are on", async () => {
      const guideEpisodes = testGuideEpisodes();
      const showDetails = testShowDetails();
      mockedAxios.get.mockResolvedValueOnce({ data: testABCGuide });
      mockedConvertDate.mockReturnValueOnce(new Date("2026-10-25T09:00:00"));
      jest.spyOn(SearchItem, "findAll").mockResolvedValueOnce(
        testSearchItems().filter(searchItem => searchItem.searchActive === true)
      );
      jest.spyOn(ShowEpisode, "findShowEpisode")
        .mockResolvedValueOnce(testShowEpisodeData[1] as ShowEpisode)
        .mockResolvedValueOnce(testShowEpisodeData[1] as ShowEpisode)
        .mockResolvedValueOnce(testShowEpisodeData[0] as ShowEpisode);

      jest.spyOn(SearchItem.prototype, "checkSearchConditions")
        .mockReturnValueOnce(true)
        .mockReturnValueOnce(true);
      const guideEpisodeCreate = jest.spyOn(GuideEpisode, "create")
        .mockResolvedValueOnce(guideEpisodes[0])
        .mockResolvedValueOnce(guideEpisodes[0])
        .mockResolvedValueOnce(guideEpisodes[1]);
      const captureDBEventSpy = jest.spyOn(GuideEpisode.prototype, "captureDBEvent");
      jest.spyOn(GuideEpisode.prototype, "update")
        .mockImplementationOnce(() => {
          return Promise.resolve(guideEpisodes[0])
        })
        .mockImplementationOnce(() => {
          return Promise.resolve(guideEpisodes[0])
        });
      jest.spyOn(ShowDetails, "findOne")
        .mockResolvedValueOnce({
          ...showDetails[0],
          id: 1,
        } as ShowDetails)
        .mockResolvedValueOnce({
          ...showDetails[0],
          id: 1,
        } as ShowDetails)
        .mockResolvedValueOnce({
          ...showDetails[1],
          id: 2,
        } as ShowDetails);
      jest.spyOn(GuideEpisode.prototype, "reload")
        .mockImplementationOnce(() => {
          guideEpisodes[0].showEpisode = testShowEpisodes[0];
          return Promise.resolve(guideEpisodes[0]);
        })
        .mockImplementationOnce(() => {
          guideEpisodes[0].showEpisode = testShowEpisodes[0];
          return Promise.resolve(guideEpisodes[0]);
        })
        .mockImplementationOnce(() => {
          guideEpisodes[1].showEpisode = testShowEpisodes[1];
          return Promise.resolve(guideEpisodes[1]);
        });
      jest.spyOn(ShowEpisode.prototype, "save")
        .mockResolvedValueOnce(testShowEpisodes[1])
        .mockResolvedValueOnce(testShowEpisodes[1])
        .mockResolvedValueOnce(testShowEpisodes[0]);

      await guideService.searchFTAGuide(1, dayjs("2026-10-25T09:00:00"));

      expect(guideEpisodeCreate).toHaveBeenNthCalledWith(
        1,
        {
          title: "Endeavour",
          channel: "ABC1",
          startTime: new Date("2026-10-25T20:30:00"),
          endTime: new Date("2026-10-25T22:00:00"),
          seasonNumber: 1,
          episodeNumber: 1,
          episodeTitle: "Pilot",
          repeat: false,
          dbEvent: null,
          guideId: 1,
          showId: 1,
          episodeId: 66,
          reminderId: null,
        }
      );
      expect(guideEpisodeCreate).toHaveBeenNthCalledWith(
        2,
        {
          title: "Endeavour",
          channel: "ABCHD",
          startTime: new Date("2026-10-25T20:30:00"),
          endTime: new Date("2026-10-25T22:00:00"),
          seasonNumber: 1,
          episodeNumber: 1,
          episodeTitle: "Pilot",
          repeat: false,
          dbEvent: null,
          guideId: 1,
          showId: 1,
          episodeId: 66,
          reminderId: null,
        }
      );
      expect(guideEpisodeCreate).toHaveBeenNthCalledWith(
        3,
        {
          title: "Merlin",
          channel: "ABC2",
          dbEvent: null,
          startTime: new Date("2026-10-25T11:57:00.000Z"),
          endTime: new Date("2026-10-25T12:44:00.000Z"),
          seasonNumber: 1,
          episodeNumber: 1,
          episodeTitle: "The Dragon's Call",
          repeat: false,
          guideId: 1,
          showId: 2,
          episodeId: 1,
          reminderId: null,
        }
      );
      expect(captureDBEventSpy).toHaveBeenCalledTimes(2);
    });
  });

  describe("buildShowData", () => {
    it("creates showData for a show", () => {
      const result = guideService.buildShowData({
        title: "Endeavour",
        channel: "ABC1",
        start_time: new Date("2026-10-25T20:30:00"),
        end_time: new Date("2026-10-25T22:00:00"),
        season_number: 1,
        episode_number: 3,
        episode_title: "Fugue",
      });

      expect(result).toHaveLength(1);
      expect(result[0]).toEqual({
        title: "Endeavour",
        channel: "ABC1",
        start_time: new Date("2026-10-25T20:30:00"),
        end_time: new Date("2026-10-25T22:00:00"),
        season_number: 1,
        episode_number: 3,
        episode_title: "Fugue",
      });
    });

    it("splits a Bumblebee Cyberverse show", () => {
      const result = guideService.buildShowData({
        title: "Bumblebee Cyberverse",
        channel: "GEM",
        start_time: new Date("2026-10-25T10:00:00"),
        end_time: new Date("2026-10-25T10:28:00"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Fractured/Memory",
      });

      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        title: "Bumblebee Cyberverse",
        channel: "GEM",
        start_time: new Date("2026-10-25T10:00:00"),
        end_time: new Date("2026-10-25T10:14:00"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Fractured",
      });
      expect(result[1]).toEqual({
        title: "Bumblebee Cyberverse",
        channel: "GEM",
        start_time: new Date("2026-10-25T10:14:00"),
        end_time: new Date("2026-10-25T10:28:00"),
        season_number: 1,
        episode_number: 2,
        episode_title: "Memory",
      });
    });
  });
});