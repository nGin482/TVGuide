from __future__ import annotations
from typing import TYPE_CHECKING
import os

from config import database_service
from database.models.Guide import Guide

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler


def run_guide(scheduler: AsyncIOScheduler=None):
    
    if os.environ['PYTHON_ENV'] == 'production':
        database_service.backup_recorded_shows()
    
    guide = Guide.from_runtime()
    database_service.add_guide_data(guide)

    guide_message = guide.compose_message()
    reminders_message = guide.schedule_reminders(database_service, scheduler)
    events_message = guide.compose_events_message()
    print(guide_message)
    return guide_message, reminders_message, events_message
