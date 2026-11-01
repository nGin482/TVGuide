import { ChannelType, Client, GatewayIntentBits } from "discord.js";



class Hermes extends Client {

  constructor() {
    super({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
      ],
    });
  }

  async sendGuideMessage(
    guideMessage: string,
    reminderMessage: string,
    eventsMessage: string
  ) {
    const guideChannel = await this.getGuideChannel();
    if (!process.env.NGIN) {
      throw Error("Environment variable for NGin user not set");
    }
    const nginUser = this.users.cache.get(process.env.NGIN);

    if (guideChannel) {
      await guideChannel.send(guideMessage);
      await guideChannel.send(reminderMessage);
      if (process.env.NODE_ENV !== "development" && nginUser) {
        await nginUser.send(eventsMessage)
      }
      else {
        await guideChannel.send(eventsMessage);
      }
    }
  }

  async getGuideChannel() {
    let guideChannelId: string;
    if (process.env.NODE_ENV === "development") {
      if (!process.env.DEV_CHANNEL) {
        throw Error("Environment variable for DEV channel not set");
      }
      guideChannelId = process.env.DEV_CHANNEL;
    }
    else {
      if (!process.env.TVGUIDE_CHANNEL) {
        throw Error("Environment variable for TVGuide channel not set");
      }
      guideChannelId = process.env.TVGUIDE_CHANNEL;
    }
    const channel = this.channels.cache.get(guideChannelId);
  
    if (channel && channel.type === ChannelType.GuildText) {
      return channel;
    }
  }
}

export const hermes = new Hermes();

hermes.once("clientReady", async (client) => {
  console.log(`Logged in as ${client.user.username}`);
});
