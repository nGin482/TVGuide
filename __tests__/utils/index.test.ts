import * as utils from "../../utils";


describe("Utility functions", () => {

  describe("formatEpisodeTitle", () => {
    it("formats an episode title ending in ', A'", () => {
      const episodeTitle = utils.formatEpisodeTitle("Convenient Truth, A");

      expect(episodeTitle).toEqual("A Convenient Truth");
    });

    it("leaves Kolcheck, A. as-is", () => {
      const episodeTitle = utils.formatEpisodeTitle("Kolcheck, A.");

      expect(episodeTitle).toEqual("Kolcheck, A.");
    });

    it("formats an episode title ending in ', The'", () => {
      const episodeTitle = utils.formatEpisodeTitle("Inconvenient Truth, The");

      expect(episodeTitle).toEqual("The Inconvenient Truth");
    });
  });

  describe("formatSBSEpisode", () => {
    it("formats a regular SBS show", () => {
      const formattedSBSShow = utils.formatSBSEpisode(
        "Red Election",
        "Afsnit 1"
      );
  
      expect(formattedSBSShow).toEqual({
        title: "Red Election",
        episodeTitle: "Afsnit 1",
      });
    });
    
    it("formats an SBS show containing SBS's episode title style", () => {
      const formattedSBSShow = utils.formatSBSEpisode(
        "Red Election",
        "Red Election Series 1 Ep 1"
      );
  
      expect(formattedSBSShow).toEqual({
        title: "Red Election",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Red Election Series 1 Ep 1",
      });
    });
  });

  describe("parseShow", () => {
    it("parses a show that doesn't require any special handling", () => {
      const parsedShow = utils.parseShow({
        title: "Endeavour",
        channel: "ABC1",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T22:00"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Pilot",
      });

      expect(parsedShow).toEqual({
        title: "Endeavour",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Pilot",
      });
    });

    it("parses a show with a title containing ':'", () => {
      // TODO: should also check for a show like NCIS: Los Angeles
      const parsedShow = utils.parseShow({
        title: "Doctor Who: The Next Doctor",
        channel: "ABC2",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:17"),
        season_number: 4,
        episode_number: 14,
        episode_title: "",
      });

      expect(parsedShow).toEqual({
        title: "Doctor Who",
        seasonNumber: 4,
        episodeNumber: 14,
        episodeTitle: "The Next Doctor",
      });
    });

    it("parses a show with a title containing '-'", () => {
      const parsedShow = utils.parseShow({
        title: "Doctor Who - The Next Doctor",
        channel: "ABC2",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:17"),
        season_number: 4,
        episode_number: 14,
        episode_title: "",
      });

      expect(parsedShow).toEqual({
        title: "Doctor Who",
        seasonNumber: 4,
        episodeNumber: 14,
        episodeTitle: "The Next Doctor",
      });
    });

    it("removes the show's title from the episode title", () => {
      const parsedShow = utils.parseShow({
        title: "Red Election",
        channel: "ABC1",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:30"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Red Election - Afsnit 1",
      });

      expect(parsedShow).toEqual({
        title: "Red Election",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Afsnit 1",
      });
    });

    it("parses a show on SBS", () => {
      const formatSBSSpy = jest.spyOn(utils, "formatSBSEpisode");

      const parsedShow = utils.parseShow({
        title: "Red Election",
        channel: "SBS",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:30"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Red Election Series 1 Ep 2",
      });

      expect(parsedShow).toEqual({
        title: "Red Election",
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "Red Election Series 1 Ep 2",
      });
      expect(formatSBSSpy).toHaveBeenCalledWith(
        "Red Election",
        "Red Election Series 1 Ep 2"
      );

      formatSBSSpy.mockRestore();
    });

    it("parses a Maigret episode", () => {
      const parsedShow = utils.parseShow({
        title: "Maigret in Montmartre",
        channel: "ABC1",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T22:00"),
        season_number: 1,
        episode_number: 2,
        episode_title: "Maigret in Montmartre",
      });

      expect(parsedShow).toEqual({
        title: "Maigret",
        seasonNumber: 1,
        episodeNumber: 2,
        episodeTitle: "Maigret in Montmartre",
      });
    });

    it("parses a Death In Paradise episode", () => {
      const parsedShow = utils.parseShow({
        title: "Death in Paradise",
        channel: "ABC1",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:30"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Maigret in Montmartre",
      });

      expect(parsedShow).toEqual({
        title: "Death In Paradise",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Maigret in Montmartre",
      });
    });

    it("parses a Grantchester Christmas Special episode", () => {
      const parsedShow = utils.parseShow({
        title: "Grantchester Christmas Special",
        channel: "ABC1",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:30"),
        season_number: 1,
        episode_number: 1,
        episode_title: "",
      });

      expect(parsedShow).toEqual({
        title: "Grantchester",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "",
      });
    });

    it("parses an NCIS Encore episode", () => {
      const parsedShow = utils.parseShow({
        title: "NCIS Encore",
        channel: "10",
        start_time: new Date("2026-10-17T20:30"),
        end_time: new Date("2026-10-17T21:30"),
        season_number: 1,
        episode_number: 1,
        episode_title: "Yankee White",
      });

      expect(parsedShow).toEqual({
        title: "NCIS",
        seasonNumber: 1,
        episodeNumber: 1,
        episodeTitle: "Yankee White",
      });
    });
  });
});
