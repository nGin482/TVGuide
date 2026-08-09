from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import asyncio
import logging
import os

from utils.LoggingFormatter import logging_handler

logger = logging.getLogger("TVGuideScheduler")
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)


class TVGuideScheduler:
    def __init__(self, engine=None):
        self.engine = engine
        self.scheduler: AsyncIOScheduler | None = None

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
        logger.info("TVGuide Scheduler initialized.")

    def get_jobs(self):
        return self.scheduler

    def add_job(self, func, trigger, *args, **kwargs):
        return self.scheduler.add_job(func, trigger, *args, **kwargs)

    def remove_all_jobs(self):
        if self.scheduler:
            self.scheduler.remove_all_jobs()
