import discord

from database.models.GuideEpisode import GuideEpisode
from services.TVGuideScheduler import TVGuideScheduler


class GuideEpisodeDropdown(discord.ui.Select):
    scheduler: TVGuideScheduler
    episodes: list[GuideEpisode]

    def __init__(
            self,
            guide_episodes: list[GuideEpisode],
            tvguide_scheduler: TVGuideScheduler
        ):
        options = [
            discord.SelectOption(
                label=f"{guide_episode.title} at {guide_episode.start_time} on {guide_episode.channel}",
                value=f"{guide_episode.id}"
            )
            for guide_episode in guide_episodes
        ]
        self.scheduler = tvguide_scheduler
        self.episodes = guide_episodes
        super().__init__(
            placeholder="Select the episode",
            min_values=1,
            max_values=1,
            options=options,
            required=True,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

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
            await interaction.followup.send(
                selected_episode.reminder_message(notify_time)
            )
        elif selected_episode and not selected_episode.reminder:
            await interaction.followup.send(
                f"{selected_episode.title} does not have a reminder set"
            )
        else:
            await interaction.followup.send(
                "Unable to find the selected episode"
            )

class DropdownView(discord.ui.View):
    def __init__(
            self,
            guide_episodes: list[GuideEpisode],
            tvguide_scheduler: TVGuideScheduler
        ):
        super().__init__()
        self.add_item(GuideEpisodeDropdown(guide_episodes, tvguide_scheduler))