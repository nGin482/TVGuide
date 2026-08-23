from apscheduler.job import Job
from sqlalchemy.orm import Session
import discord
import logging
import os
import traceback

from database.models.GuideEpisode import GuideEpisode
from services.hermes.hermes import hermes
from services.TVGuideScheduler import TVGuideScheduler
from utils.LoggingFormatter import logging_handler

logger = logging.getLogger("reschedule_reminder_command")
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)

class RescheduleModal(discord.ui.Modal):

    def __init__(self,
        job: Job,
        scheduler: TVGuideScheduler,
        guide_episode: GuideEpisode,
    ):
        super().__init__(title="What time would you like to be reminded?")
        self.job = job
        self.tvguide_scheduler = scheduler
        self.guide_episode = guide_episode
        self.hour_input = discord.ui.TextInput(label="Hour (24h)", required=True)
        self.minute_input = discord.ui.TextInput(label="Minute", required=True)
        self.add_item(self.hour_input)
        self.add_item(self.minute_input)

    async def on_submit(self, interaction: discord.Interaction):
        hour_value = int(self.hour_input.value)
        minute_value = int(self.minute_input.value)
        (_, start_time) = self.tvguide_scheduler.parse_job_id(self.job.id)
        notify_time = start_time.replace(hour=hour_value, minute=minute_value)
        self.tvguide_scheduler.reschedule_job(self.job, notify_time)
        await interaction.response.send_message(
            self.guide_episode.reminder_message(notify_time)
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Catches errors raised inside on_submit."""
        logger.error(f"Error rescheduling job: {error}")
        logger.error(
            f"Error rescheduling job '{error}'",
            exc_info=(type(error), error, error.__traceback__)
        )

        error_message = f"An error occurred rescheduling the reminder '{self.job.id}'"
    
        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
        tb_text = ''.join(tb_lines)
    
        if len(tb_text) > 1000:
            tb_text = tb_text[:997] + "..."
    
        formatted_traceback = f"```py\n{tb_text}\n```"
    
        embed = discord.Embed(
            title="Command Error!",
            description=error_message,
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="Error", value=error)
        embed.add_field(name="Original Message", value=interaction.message.content)
        embed.add_field(name="Author", value=interaction.message.author)
        embed.add_field(name="Traceback", value=formatted_traceback, inline=False)
    
        if os.getenv("PYTHON_ENV") == "production":
            await interaction.response.send_message(error_message)
            ngin_id = os.getenv("NGIN")
            ngin = await hermes.fetch_user(ngin_id)
            await ngin.send(embed=embed)
        else:
            await interaction.response.send_message(error_message, embed=embed)
    
    


class RescheduleReminderDropdown(discord.ui.Select):

    def __init__(
        self,
        reminders: list[Job],
        tvguide_scheduler: TVGuideScheduler,
        guide_episodes: list[GuideEpisode],
        session: Session,
    ):
        options = [
            discord.SelectOption(
                label=f"{reminder.id}",
                value=f"{reminder.id}"
            )
            for reminder in reminders
        ]
        super().__init__(
            placeholder="Select the reminder...",
            min_values=1,
            max_values=1,
            options=options,
            required=True,
        )
        self.reminders = reminders
        self.tvguide_scheduler = tvguide_scheduler
        self.guide_episodes = guide_episodes
        self.session = session

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        job = next(
            (reminder for reminder in self.reminders if str(reminder.id) == selected_option),
            None
        )
        if job:
            (show, start_time) = self.tvguide_scheduler.parse_job_id(job.id)
            guide_episode = next(
                (
                    episode
                    for episode in self.guide_episodes
                    if episode.title == show and episode.start_time == start_time
                ),
                None
            )
            await interaction.response.send_modal(
                RescheduleModal(job, self.tvguide_scheduler, guide_episode)
            )
        else:
            await interaction.response.send_message(
                "Unable to find the selected reminder"
            )
        self.session.close()
