
import SearchItem from "../../../database/models/SearchItem";
import ShowDetails from "../../../database/models/ShowDetails";
import UserSearchSubscription from "../../../database/models/UserSearchSubscription";



describe("SearchItem Model", () => {

  describe("checkSearchConditions", () => {
    let ignoreSeasons: number[] = [];
    const searchItem = SearchItem.build({
      show: "Vera",
      showId: 1,
      searchActive: true,
      exactTitleMatch: true,
      minSeasonNumber: 1,
      maxSeasonNumber: 13,
      ignoreTitles: [],
      ignoreSeasons: ignoreSeasons,
      ignoreEpisodes: [],
    });

    beforeEach(() => {
      ignoreSeasons = [];
    });

    it("returns true if a show meets the search conditions", () => {
      const result = searchItem.checkSearchConditions({
        title: "Vera",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: 2,
        episode_number: 2,
        episode_title: "Silent Voices",
        repeat: true,
      });

      expect(result).toEqual(true);
    });

    it("returns false if there isn't an exact title match", () => {
      const result = searchItem.checkSearchConditions({
        title: "Verandah Roadshow",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: 2,
        episode_number: 2,
        episode_title: "Silent Voices",
        repeat: true,
      });

      expect(result).toEqual(false);
    });

    it("returns false if the season is ignored", () => {
      const searchItem = SearchItem.build({
        show: "Vera",
        showId: 1,
        searchActive: true,
        exactTitleMatch: true,
        minSeasonNumber: 1,
        maxSeasonNumber: 13,
        ignoreTitles: [],
        ignoreSeasons: [2],
        ignoreEpisodes: [],
      });

      const result = searchItem.checkSearchConditions({
        title: "Vera",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: 2,
        episode_number: 2,
        episode_title: "Silent Voices",
        repeat: true,
      });

      expect(result).toEqual(false);
    });

    it("returns false if the season is outside the min/max range", () => {
      const searchItem = SearchItem.build({
        show: "Vera",
        showId: 1,
        searchActive: true,
        exactTitleMatch: true,
        minSeasonNumber: 1,
        maxSeasonNumber: 4,
        ignoreTitles: [],
        ignoreSeasons: [],
        ignoreEpisodes: [],
      });

      const result = searchItem.checkSearchConditions({
        title: "Vera",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: 5,
        episode_number: 1,
        episode_title: "Changing Tides",
        repeat: true,
      });

      expect(result).toEqual(false);
    });

    it("returns false if the episode title is ignored", () => {
      const searchItem = SearchItem.build({
        show: "Vera",
        showId: 1,
        searchActive: true,
        exactTitleMatch: true,
        minSeasonNumber: 1,
        maxSeasonNumber: 13,
        ignoreTitles: [],
        ignoreSeasons: [],
        ignoreEpisodes: [
          "Changing Tides",
        ],
      });

      const result = searchItem.checkSearchConditions({
        title: "Vera",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: -1,
        episode_number: 1,
        episode_title: "Changing Tides",
        repeat: true,
      });

      expect(result).toEqual(false);
    });

    it("returns true if there's no info about the show", () => {
      const result = searchItem.checkSearchConditions({
        title: "Vera",
        channel: "ABC1",
        start_time: new Date("2026-10-18T20:30:00"),
        end_time: new Date("2026-10-18T22:00:00"),
        season_number: -1,
        episode_number: 1,
        episode_title: "",
        repeat: true,
      });

      expect(result).toEqual(true);
    });
  });

  describe("associate", () => {
    it("associates the SearchIte model to other models", () => {
      const belongsToSpy = jest.spyOn(SearchItem, "belongsTo");
      const hasManySpy = jest.spyOn(SearchItem, "hasMany");

      SearchItem.associate();

      expect(hasManySpy).toHaveBeenCalledWith(
        UserSearchSubscription,
        expect.objectContaining({
          foreignKey: "search_id",
          as: "subscriptions",
        }),
      );
      expect(belongsToSpy).toHaveBeenCalledWith(
        ShowDetails,
        expect.objectContaining({
          foreignKey: "show_id",
          as: "showDetails",
        }),
      );

      belongsToSpy.mockRestore();
      hasManySpy.mockRestore();
    });
  });
});
