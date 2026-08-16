from apscheduler.job import Job
from sqlalchemy.orm import Session
import discord

from database.models.GuideEpisode import GuideEpisode
from services.TVGuideScheduler import TVGuideScheduler
from services.hermes.ui_components.ReminderDropdown import ReminderDropdown
from services.hermes.ui_components.GuideEpisodeDropdown import GuideEpisodeDropdown


class DropdownView(discord.ui.View):
    def __init__(
        self,
        tvguide_scheduler: TVGuideScheduler,
        guide_episodes: list[GuideEpisode] | None = None,
        reminders: list[Job] | None = None,
        session: Session | None = None
    ):
        super().__init__()
        if guide_episodes:
            self.add_item(
                GuideEpisodeDropdown(guide_episodes, tvguide_scheduler, session)
            )
        elif reminders:
            self.add_item(
                ReminderDropdown(reminders, tvguide_scheduler)
            )
