import { ChannelType, Client, GatewayIntentBits } from "discord.js";


export const hermes = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

hermes.once("clientReady", async (client) => {
  console.log(`Logged in as ${client.user.username}`);
  const channel = client.channels.cache.get("1189833076977705062");
  
  if (channel && channel.type === ChannelType.GuildText) {
    await channel.send("Boo")
  }
});
