import {
  createMockTextChannel,
  createMockUser,
  mockGetChannels,
  mockGetUsers,
  mockSend,
} from "../__mocks__/discord.js";

import { hermes } from "../../services/hermes/Hermes";


describe("Hermes", () => {

  describe("sendGuideMessage", () => {
    let originalEnv: string | undefined;

    beforeEach(() => {
      jest.clearAllMocks();
      originalEnv = process.env.NODE_ENV;
    });

    afterEach(() => {
      process.env.NODE_ENV = originalEnv;
    });

    it("sends the TVGuide messages", async () => {
      mockGetChannels.mockReturnValueOnce(createMockTextChannel({
        name: "tvguide",
      }));
  
      await hermes.sendGuideMessage(
        "TVGuide message",
        "Reminder message",
        "Events message",
      );
  
      expect(mockSend).toHaveBeenNthCalledWith(1, "TVGuide message");
      expect(mockSend).toHaveBeenNthCalledWith(2, "Reminder message");
      expect(mockSend).toHaveBeenNthCalledWith(3, "Events message");
    });

    it("sends events message to nGin user in production", async () => {
      process.env.NODE_ENV = "production";
      mockGetChannels.mockReturnValueOnce(createMockTextChannel({
        name: "tvguide",
      }));
      mockGetUsers.mockReturnValueOnce(createMockUser({
        name: "nGin",
      }));

      await hermes.sendGuideMessage(
        "TVGuide message",
        "Reminder message",
        "Events message",
      );
  
      expect(mockSend).toHaveBeenNthCalledWith(1, "TVGuide message");
      expect(mockSend).toHaveBeenNthCalledWith(2, "Reminder message");
      expect(mockSend).toHaveBeenNthCalledWith(3, "Events message");
    });
  });

  describe("getGuideChannel", () => {
    it("finds and returns the TVGuide channel", async () => {
      mockGetChannels.mockReturnValueOnce(createMockTextChannel({
        name: "tvguide",
      }));

      const channel = hermes.getGuideChannel();

      expect(channel.name).toEqual("tvguide");
    });

    it("throws an error if the channel is not found", () => {
      mockGetChannels.mockReturnValueOnce(undefined);

      expect(() => hermes.getGuideChannel()).toThrow(
        "Cannot find TVGuide channel"
      );
    });
  });
});
