from discord.ext import commands
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
        print("creating options")
        options = [
            discord.SelectOption(
                label=f"{guide_episode.title} at {guide_episode.start_time} on {guide_episode.channel}",
                value=f"{guide_episode.id}"
            )
            for guide_episode in guide_episodes
        ]
        print("options", options)
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
        print("selected_option", selected_option)
        print("self.episodes", self.episodes)
        selected_episode = next(
            (episode for episode in self.episodes if str(episode.id) == selected_option),
            None
        )
        print("selected_episode", selected_episode)
        await interaction.followup.send(
            f"You selected {selected_episode.title} airing at {selected_episode.start_time}!"
        )

class DropdownView(discord.ui.View):
    def __init__(
            self,
            guide_episodes: list[GuideEpisode],
            tvguide_scheduler: TVGuideScheduler
        ):
        super().__init__()
        print("adding dropdown")
        self.add_item(GuideEpisodeDropdown(guide_episodes, tvguide_scheduler))
        print("dropdown added")