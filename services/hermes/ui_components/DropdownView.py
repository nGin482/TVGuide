from apscheduler.job import Job
from sqlalchemy.orm import Session
from typing import Literal
import discord

from database.models.GuideEpisode import GuideEpisode
from services.TVGuideScheduler import TVGuideScheduler
from services.hermes.ui_components.GuideEpisodeDropdown import GuideEpisodeDropdown
from services.hermes.ui_components.ReminderDropdown import ReminderDropdown
from services.hermes.ui_components.RescheduleReminder import RescheduleReminderDropdown

CREATE_REMINDER = Literal["create_reminder"]
RESCHEDULE_REMINDER = Literal["reschedule_reminder"]
REMOVE_REMINDER = Literal["remove_reminder"]

class DropdownView(discord.ui.View):
    def __init__(
        self,
        tvguide_scheduler: TVGuideScheduler,
        command: CREATE_REMINDER | RESCHEDULE_REMINDER | REMOVE_REMINDER,
        guide_episodes: list[GuideEpisode] | None = None,
        reminders: list[Job] | None = None,
        session: Session | None = None
    ):
        super().__init__()
        if command == "create_reminder":
            self.add_item(
                GuideEpisodeDropdown(guide_episodes, tvguide_scheduler, session)
            )
        elif command == "reschedule_reminder":
            self.add_item(
                RescheduleReminderDropdown(
                    reminders,
                    tvguide_scheduler,
                    guide_episodes,
                    session=session
                )
            )
        elif command == "remove_reminder":
            self.add_item(
                ReminderDropdown(reminders, tvguide_scheduler)
            )
