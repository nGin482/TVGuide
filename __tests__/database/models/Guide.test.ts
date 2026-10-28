import Guide from "../../../database/models/Guide";
import GuideEpisode from "../../../database/models/GuideEpisode";
import { formatDate } from "../../../utils";

import { testGuideEpisodes } from "../../__fixtures__/guideEpisodes";

jest.mock("../../../utils", () => ({
  formatDate: jest.fn(),
}));

const mockedFormatDate = jest.mocked(formatDate);



describe("Guide model", () => {
  describe("associate", () => {
    it("creates association between GuideEpisode model", () => {
      const belongsToSpy = jest.spyOn(Guide, "hasMany");

      Guide.associate();

      expect(belongsToSpy).toHaveBeenCalledWith(
        GuideEpisode,
        expect.objectContaining({
          foreignKey: "guide_id",
          as: "shows",
        }),
      );
    });
  });

  describe("composeMessage", () => {
    const guide = Guide.build({
      date: new Date("2026-10-24T00:00:00"),
    });

    it("composes the Guide message", () => {
      mockedFormatDate.mockReturnValueOnce("Saturday 24-October-2026");
      guide.shows = testGuideEpisodes();
      
      const message = guide.composeMessage();

      expect(message).toEqual(`# Saturday 24-October-2026 TVGuide

Free to Air:
* 20:30: Endeavour is on ABC1 (Season 1, Episode 2: Fugue) (Repeat)
* 22:57: Merlin is on ABC2 (Season 1, Episode 1: The Dragon's Call) (Repeat)
`);
    });

    it("composes the Guide message with no shows airing", () => {
      mockedFormatDate.mockReturnValueOnce("Saturday 24-October-2026");
      guide.shows = [];
      
      const message = guide.composeMessage();

      expect(message).toEqual(`# Saturday 24-October-2026 TVGuide

Free to Air:
Nothing on Free to Air today
`);
    });
  });

  describe("composeEventsMessage", () => {
    const guide = Guide.build({
      date: new Date("2026-10-24T00:00:00"),
    });

    it("composes the events message", () => {
      mockedFormatDate.mockReturnValueOnce("Saturday 24-October-2026");
      guide.shows = testGuideEpisodes([
        { dbEvent: "Season 1, Episode 2 has aired today" },
        { dbEvent: "Season 1, Episode 1 (The Dragon's Call) has been inserted" },
      ]);

      const eventsMessage = guide.composeEventsMessage();

      expect(eventsMessage).toEqual(`# Events - Saturday 24-October-2026
* Endeavour - Season 1, Episode 2 has aired today
* Merlin - Season 1, Episode 1 (The Dragon's Call) has been inserted`
      );
    });

    it("composes the events message with no shows airing", () => {
      mockedFormatDate.mockReturnValueOnce("Saturday 24-October-2026");
      guide.shows = [];
      
      const message = guide.composeEventsMessage();

      expect(message).toEqual(`# Events - Saturday 24-October-2026
No events occurred today`
      );
    });
  });
});
