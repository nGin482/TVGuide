from apscheduler.triggers.cron import CronTrigger
from discord import Intents, TextChannel
from discord.ext.commands import Bot, DefaultHelpCommand
import os

from aux_methods.helper_methods import split_message_by_time
from guide import create_guide
from services.TVGuideScheduler import TVGuideScheduler

class Hermes(Bot):
    
    def __init__(self, command_prefix, help_command=..., description=None, **options):
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            intents=intents,
            **options
        )

    async def schedule_guide_job(self, tvguide_scheduler: TVGuideScheduler):
        tvguide_scheduler.add_job(
            create_guide,
            CronTrigger(hour=9, timezone='Australia/Sydney'),
            id='TVGuide Message',
            name='Send the TVGuide message',
            misfire_grace_time=None,
            replace_existing=True
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
                fta_am_message, fta_pm_message = split_message_by_time(guide_message)

                await channel.send(fta_am_message)
                await channel.send(fta_pm_message)
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

        if os.getenv("PYTHON_ENV") != "production":
            channel_id = int(os.getenv("DEV_CHANNEL"))
        else:
            channel_id = int(os.getenv("TVGUIDE_CHANNEL"))

        return self.get_channel(channel_id)

environment = os.getenv("PYTHON_ENV")
command_prefix = "$" if environment == "production" else "!" 
hermes = Hermes(command_prefix=command_prefix, help_command=DefaultHelpCommand())


from services.hermes import events
from services.hermes import commands
