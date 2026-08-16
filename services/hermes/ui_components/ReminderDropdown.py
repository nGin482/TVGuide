from apscheduler.job import Job
import discord

from services.TVGuideScheduler import TVGuideScheduler



class ReminderDropdown(discord.ui.Select):
    def __init__(
        self, 
        reminders: list[Job],
        tvguide_scheduler: TVGuideScheduler,
    ):
        options = [
            discord.SelectOption(
                label=f"{reminder.id}",
                value=f"{reminder.id}"
            )
            for reminder in reminders
        ]
        super().__init__(
            placeholder="Select the reminder",
            min_values=1,
            max_values=1, options=options,
            required=True,
        )
        self.tvguide_scheduler = tvguide_scheduler
        self.reminders = reminders

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        job = next(
            (reminder for reminder in self.reminders if str(reminder.id) == selected_option),
            None
        )
        (show_title, _) = self.tvguide_scheduler.parse_job_id(selected_option)
        self.tvguide_scheduler.remove_job(job)
        await interaction.response.send_message(
            f"The reminder for {show_title} has been removed"
        )


class ReminderDropdownView(discord.ui.View):
    def __init__(
        self,
        reminders: list[Job],
        tvguide_scheduler: TVGuideScheduler,
    ):
        super().__init__()
        self.add_item(ReminderDropdown(reminders, tvguide_scheduler))