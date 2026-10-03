import axios from "axios";

import { checkEpisodes, deleteShowEpisode, fetchLatestEpisodes, updateShowEpisode } from "../../src/requests";
import { ShowEpisode } from "../../src/utils/types";

jest.mock("axios");

const mockAxios = jest.mocked(axios);



describe(`Requests to "/api/show-episode" endpoint`, () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe("checkEpisodes", () => {
    it("returns a check on a show's episodes", async () => {
      mockAxios.get.mockResolvedValueOnce({
        data: {
          needs_refresh: true,
          latest_season_recorded: 1,
          tvmaze_season_max: 4,
        },
      });

      const episodeCheck = await checkEpisodes("Doctor Who");

      expect(episodeCheck).toEqual({
        needs_refresh: true,
        latest_season_recorded: 1,
        tvmaze_season_max: 4,
      });
    });
  });

  describe("fetchLatestEpisodes", () => {
    it("fetches a show's latest episodes", async () => {
      mockAxios.post.mockResolvedValueOnce({
        data: {
          episodes_added: 18,
        },
      });

      const episodeCheck = await fetchLatestEpisodes(
        "Doctor Who",
        {
          needs_refresh: true,
          latest_season_recorded: 1,
          tvmaze_season_max: 4,
        }
      );

      expect(episodeCheck).toEqual({
        episodes_added: 18,
      });
    });
  });

  describe("updateShowEpisode", () => {
    it("updates an episode", async () => {
      const newEpisodeData: ShowEpisode = {
        id: 1,
        show: "Doctor Who",
        season_number: 1,
        episode_number: 1,
        episode_title: "Rose",
        summary: "",
        channels: [
          "ABC2",
        ],
        air_dates: [],
        alternative_titles: [],
      };
      mockAxios.put.mockResolvedValueOnce({
        data: newEpisodeData,
      });

      const updatedEpisode = await updateShowEpisode(newEpisodeData);

      expect(updatedEpisode).toEqual(newEpisodeData);
    });
  });

  describe("deleteShowEpisode", () => {
    it("deletes an episode", async () => {
      await deleteShowEpisode(1);

      expect(mockAxios.delete).toHaveBeenCalledWith(
        "https://tvguide-ng-test.com/api/show-episode/1",
        {
          "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRF-Token": undefined,
          },
          "withCredentials": true,
        },
      );
    });
  });
});
