import { ChannelType, Client, GatewayIntentBits } from "discord.js";

import { appConfig } from "../../config";



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
    const isProduction = appConfig.environment === "production";
    const guideChannel = this.getGuideChannel();
    const nginUser = this.users.cache.get(appConfig.nGinUserId);

    if (isProduction && !nginUser) {
      throw Error("NGin user not found");
    }

    await guideChannel.send(guideMessage);
    await guideChannel.send(reminderMessage);
    if (isProduction && nginUser) {
      await nginUser.send(eventsMessage)
    }
    else {
      await guideChannel.send(eventsMessage);
    }
  }

  getGuideChannel() {
    const channel = this.channels.cache.get(appConfig.tvguideChannelId);
  
    if (channel && channel.type === ChannelType.GuildText) {
      return channel;
    }
    else {
      throw Error("Cannot find TVGuide channel");
    }
  }
}

export const hermes = new Hermes();

hermes.once("clientReady", async (client) => {
  console.log(`Logged in as ${client.user.username}`);
});
