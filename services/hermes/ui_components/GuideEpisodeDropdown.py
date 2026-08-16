from apscheduler.jobstores.base import ConflictingIdError
from datetime import timedelta
from sqlalchemy.orm import Session
import discord
import pytz

from database.models.GuideEpisode import GuideEpisode
from data_validation.validation import Validation
from services.TVGuideScheduler import TVGuideScheduler

class NotifyTimeModal(discord.ui.Modal):

    def __init__(self, guide_episode: GuideEpisode, scheduler: TVGuideScheduler):
        super().__init__(title="What time would you like to be reminded?")
        self.guide_episode = guide_episode
        self.scheduler = scheduler
        self.notify_time_input = discord.ui.TextInput(
            label="Notify Time",
            default="3",
            required=True
        )
        self.add_item(self.notify_time_input)

    async def on_submit(self, interaction: discord.Interaction):
        value = int(self.notify_time_input.value)
        notify_time = self.guide_episode.start_time - timedelta(minutes=value)
        try:
            self.scheduler.add_reminder_job(self.guide_episode, notify_time)
            await interaction.response.send_message(
                self.guide_episode.reminder_message(notify_time)
            )
        except ConflictingIdError:
            await interaction.response.send_message(
                "There is already a reminder set for this show"
            )


class GuideEpisodeDropdown(discord.ui.Select):
    scheduler: TVGuideScheduler
    episodes: list[GuideEpisode]

    def __init__(
        self,
        guide_episodes: list[GuideEpisode],
        tvguide_scheduler: TVGuideScheduler,
        session: Session,
    ):
        options = [
            discord.SelectOption(
                label=f"{guide_episode.title} at {guide_episode.start_time} on {guide_episode.channel}",
                value=f"{guide_episode.id}"
            )
            for guide_episode in guide_episodes
            if pytz.timezone("Australia/Sydney").localize(guide_episode.start_time)
                >= Validation.get_current_date()
        ]
        self.scheduler = tvguide_scheduler
        self.episodes = guide_episodes
        self.session = session
        super().__init__(
            placeholder="Select the episode",
            min_values=1,
            max_values=1,
            options=options,
            required=True,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        selected_episode = next(
            (episode for episode in self.episodes if str(episode.id) == selected_option),
            None
        )
        if selected_episode and selected_episode.reminder:
            notify_time = selected_episode.reminder.calculate_notification_time(
                selected_episode.start_time
            )
            self.scheduler.add_reminder_job(selected_episode, notify_time)
            await interaction.response.send_message(
                selected_episode.reminder_message(notify_time)
            )
        elif selected_episode and not selected_episode.reminder:
            await interaction.response.send_modal(
                NotifyTimeModal(selected_episode, self.scheduler)
            )
        else:
            await interaction.response.send_message(
                "Unable to find the selected episode"
            )
        self.session.close()
