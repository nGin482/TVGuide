from discord import Intents, TextChannel
from discord.ext.commands import Bot, DefaultHelpCommand
import os

from aux_methods.helper_methods import split_message_by_time

class Hermes(Bot):
    
    def __init__(self, command_prefix, help_command=..., description=None, **options):
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            intents=Intents.default(),
            **options
        )


    async def send_guide_message(
        self,
        guide_message: str,
        reminder_message: str,
        events_message: str
    ):
        await self.wait_until_ready()

        channel = await self.get_hermes_channel()
        ngin = await hermes.fetch_user(int(os.getenv('NGIN')))

        try:
            if len(guide_message) > 2000:
                bbc_index = guide_message.find('\nBBC:\n')
                fta_message = guide_message[0:bbc_index]
                bbc_message = guide_message[bbc_index:]

                if len(fta_message) > 2000:
                    fta_am_message, fta_pm_message = split_message_by_time(fta_message)
                    await channel.send(fta_am_message)
                    await channel.send(fta_pm_message)
                else:
                    await channel.send(fta_message)
                
                if len(bbc_message) > 2000:
                    bbc_am_message, bbc_pm_message = split_message_by_time(bbc_message)
                    await channel.send(bbc_am_message)
                    await channel.send(bbc_pm_message)
                else:
                    await channel.send(bbc_message)
            else:
                await channel.send(guide_message)
            await channel.send(reminder_message)
            if os.getenv("PYTHON_ENV") != "development":
                await ngin.send(events_message)
            else:
                await channel.send(events_message)
        except AttributeError as error:
            await ngin.send(f"There was an error sending the guide message: {str(error)}")


    async def send_message(self, message: str):
        await self.wait_until_ready()

        channel = await self.get_hermes_channel()
        
        if channel is not None:
            await channel.send(message)
        else:
            ngin = await self.fetch_user(int(os.getenv('NGIN')))
            await ngin.send(message)
            await ngin.send(
                "Hermes was also unable to send this message through the TVGuide channel"
            )

    async def get_hermes_channel(self) -> TextChannel:
        await self.wait_until_ready()

        if os.getenv("PYTHON_ENV") == "development" or os.getenv("PYTHON_ENV") == "testing":
            channel_id = int(os.getenv("DEV_CHANNEL"))
        else:
            channel_id = int(os.getenv("TVGUIDE_CHANNEL"))

        return self.get_channel(channel_id)
    
hermes = Hermes(command_prefix="$", help_command=DefaultHelpCommand())


from services.hermes import events
from services.hermes import commands
