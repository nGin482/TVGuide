import Guide from "../../../database/models/Guide";
import GuideEpisode from "../../../database/models/GuideEpisode";
import Reminder from "../../../database/models/Reminder";
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

  describe("findUpcomingReminders", () => {
    it("finds shows that need reminders", () => {
      const guide = Guide.build({
        date: new Date("2026-10-24T00:00:00"),
      });
  
      const guideEpisodes = testGuideEpisodes([
        { startTime: new Date("2026-10-24T20:30:00") },
        { startTime: new Date("2026-10-24T22:00:00") },
      ]);
      guideEpisodes[0].reminder = Reminder.build({
        show: guideEpisodes[0].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[0].showId,
        warningTime: 3,
      });
      guideEpisodes[1].reminder = Reminder.build({
        show: guideEpisodes[1].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[1].showId,
        warningTime: 5,
      });
      guide.shows = guideEpisodes;
  
      const upcomingReminders = guide.findUpcomingReminders();
  
      expect(upcomingReminders).toEqual([
        {
          show: guideEpisodes[0],
          notifyTime: new Date("2026-10-24T20:27:00"),
        },
        {
          show: guideEpisodes[1],
          notifyTime: new Date("2026-10-24T21:55:00"),
        },
      ]);
    });

    it("filters out shows without a reminder", () => {
      const guide = Guide.build({
        date: new Date("2026-10-24T00:00:00"),
      });
  
      const guideEpisodes = testGuideEpisodes([
        { startTime: new Date("2026-10-24T20:30:00") },
        { startTime: new Date("2026-10-24T22:00:00") },
      ]);
      guideEpisodes[0].reminder = Reminder.build({
        show: guideEpisodes[0].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[0].showId,
        warningTime: 3,
      });
      guide.shows = guideEpisodes;
  
      const upcomingReminders = guide.findUpcomingReminders();
  
      expect(upcomingReminders).toEqual([
        {
          show: guideEpisodes[0],
          notifyTime: new Date("2026-10-24T20:27:00"),
        },
      ]);
    });

    it("filters out shows airing on a HD channel", () => {
      const guide = Guide.build({
        date: new Date("2026-10-24T00:00:00"),
      });
  
      const guideEpisodes = testGuideEpisodes([
        { startTime: new Date("2026-10-24T20:30:00") },
        {
          startTime: new Date("2026-10-24T22:00:00"),
          channel: "ABCHD",
        },
      ]);
      guideEpisodes[0].reminder = Reminder.build({
        show: guideEpisodes[0].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[0].showId,
        warningTime: 3,
      });
      guideEpisodes[1].reminder = Reminder.build({
        show: guideEpisodes[1].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[1].showId,
        warningTime: 5,
      });
      guide.shows = guideEpisodes;
  
      const upcomingReminders = guide.findUpcomingReminders();
  
      expect(upcomingReminders).toEqual([
        {
          show: guideEpisodes[0],
          notifyTime: new Date("2026-10-24T20:27:00"),
        },
      ]);
    });

    it("filters out shows airing before the Guide was created", () => {
      const guide = Guide.build({
        date: new Date("2026-10-24T12:00:00"),
      });
  
      const guideEpisodes = testGuideEpisodes([
        { startTime: new Date("2026-10-24T20:30:00") },
        {
          startTime: new Date("2026-10-24T10:00:00"),
        },
      ]);
      guideEpisodes[0].reminder = Reminder.build({
        show: guideEpisodes[0].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[0].showId,
        warningTime: 3,
      });
      guideEpisodes[1].reminder = Reminder.build({
        show: guideEpisodes[1].title,
        alert: "Before",
        occasions: "all",
        showId: guideEpisodes[1].showId,
        warningTime: 5,
      });
      guide.shows = guideEpisodes;
  
      const upcomingReminders = guide.findUpcomingReminders();
  
      expect(upcomingReminders).toEqual([
        {
          show: guideEpisodes[0],
          notifyTime: new Date("2026-10-24T20:27:00"),
        },
      ]);
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

  describe("composeReminderMessage", () => {
    const guide = Guide.build({
      date: new Date("2026-10-31T00:00:00"),
    });

    it("composes a reminder message for upcoming reminders", () => {
      mockedFormatDate
        .mockReturnValueOnce("20:27")
        .mockReturnValueOnce("20:30")
        .mockReturnValueOnce("21:55")
        .mockReturnValueOnce("22:00")
      const guideEpisodes = testGuideEpisodes([
        { startTime: new Date("2026-10-31T20:30:00") },
        { startTime: new Date("2026-10-31T22:00:00") },
      ]);

      const message = guide.composeReminderMessage([
        {
          show: guideEpisodes[0],
          notifyTime: new Date("2026-10-31T20:27:00"),
        },
        {
          show: guideEpisodes[1],
          notifyTime: new Date("2026-10-31T21:55:00"),
        },
      ]);

      expect(message).toEqual(`## Reminders
REMINDER: Endeavour is on ABC1 at 20:30.
You will be reminded at 20:27
REMINDER: Merlin is on ABC2 at 22:00.
You will be reminded at 21:55`);
    });

    it("composes a reminder message when there's no upcoming reminders", () => {
      const message = guide.composeReminderMessage([]);

      expect(message).toEqual(
        `## Reminders\n\nThere are no reminders scheduled for today`
      );
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
