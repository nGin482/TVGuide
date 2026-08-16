from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import asyncio
import logging
import re
import os

from database.models.GuideEpisode import GuideEpisode
from utils.LoggingFormatter import logging_handler

logger = logging.getLogger("TVGuideScheduler")
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)


class TVGuideScheduler:
    def __init__(self, engine=None):
        self.engine = engine
        self.scheduler: AsyncIOScheduler | None = None
        self.scheduler_initialised = False

    def initialise(self):
        """Configures and starts the scheduler based on the active environment."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        self.scheduler = AsyncIOScheduler(event_loop=loop)
        
        if self.engine:
            jobstore = SQLAlchemyJobStore(
                engine=self.engine,
                tablename='Jobs',
                tableschema=os.getenv('DB_SCHEMA')
            )
            self.scheduler.add_jobstore(jobstore)
        else:
            logger.error("No database connection string to create JobStore")
            
        self.scheduler.start()
        self.scheduler_initialised = True
        logger.info("TVGuide Scheduler initialized.")

    def get_jobs(self) -> list[Job]:
        return self.scheduler.get_jobs()

    def add_reminder_job(
        self,
        show: GuideEpisode,
        notify_time: datetime
    ):
        from services.hermes.utilities import send_channel_message
        self.scheduler.add_job(
            send_channel_message,
            DateTrigger(run_date=notify_time, timezone='Australia/Sydney'),
            [show.reminder_notification()],
            id=f'reminder-{show.title}-{show.start_time}',
            name=f'Send the reminder message for {show.title}',
            misfire_grace_time=None
        )

    def add_job(self, func, trigger, *args, **kwargs):
        return self.scheduler.add_job(func, trigger, *args, **kwargs)

    def remove_job(self, job: Job):
        job.remove()

    def remove_all_jobs(self):
        if self.scheduler:
            self.scheduler.remove_all_jobs()

    def parse_job_id(self, job_id: str):
        pattern = r"reminder-(.+)-(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        match = re.match(pattern, job_id)

        if not match:
            raise ValueError(f"Unable to parse the job_id {job_id}")

        show_title = match.group(1)
        start_time = match.group(2)

        return (show_title, start_time)
