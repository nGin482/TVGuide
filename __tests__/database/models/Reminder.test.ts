import GuideEpisode from "../../../database/models/GuideEpisode";
import Reminder from "../../../database/models/Reminder";
import ShowDetails from "../../../database/models/ShowDetails";


describe("Reminder model", () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  describe("associate", () => {
    it("associates the Reminder model to other models", () => {
      const belongsToSpy = jest.spyOn(Reminder, "belongsTo");
      const hasManySpy = jest.spyOn(Reminder, "hasMany");

      Reminder.associate();

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
          foreignKey: "reminder_id",
          as: "guideEpisodes",
        }),
      );
    });
  });

  describe("calculateNotificationTime", () => {
    const startTime = new Date("2026-10-31T20:30:00");

    it("calculates notification time for reminder with 'during' alert", () => {
      const reminder = Reminder.build({
        show: "Endeavour",
        alert: "During",
        occasions: "all",
        warningTime: 0,
        showId: 2,
      });

      const notifyTime = reminder.calculateNotificationTime(startTime);

      expect(notifyTime).toEqual(startTime);
    });

    it("calculates notification time for reminder with 'before' alert", () => {
      const reminder = Reminder.build({
        show: "Endeavour",
        alert: "Before",
        occasions: "all",
        warningTime: 3,
        showId: 2,
      });

      const notifyTime = reminder.calculateNotificationTime(startTime);

      expect(notifyTime).toEqual(new Date("2026-10-31T20:27:00"));
    });

    it("calculates notification time for reminder with 'after' alert", () => {
      const reminder = Reminder.build({
        show: "Endeavour",
        alert: "After",
        occasions: "all",
        warningTime: 3,
        showId: 2,
      });

      const notifyTime = reminder.calculateNotificationTime(startTime);

      expect(notifyTime).toEqual(new Date("2026-10-31T20:33:00"));
    });
  });
});
