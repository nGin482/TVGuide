from aiohttp.client_exceptions import ClientConnectorDNSError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import asyncclick as click
import asyncio
import os

load_dotenv('.env')

from data_validation.validation import Validation
from services.hermes.hermes import hermes


async def send_main_message(
    guide_message: str,
    reminder_message: str,
    events_message: str
):
    """

    :param send_status:
    :return: n/a
    """
    await hermes.wait_until_ready()
    await hermes.send_guide_message(guide_message, reminder_message, events_message)
    await hermes.close()

@click.group()
def local_tvguide():
    pass

@local_tvguide.command()
@click.option('-t', '--tables', multiple=True, help="A list of tables to create")
def create_tables(tables: str):

    from database.models import create_tables
    create_tables(list(tables))

@local_tvguide.command()
@click.option('-t', '--tables', multiple=True, help="A list of tables to drop")
def drop_tables(tables: str):

    from database.models import drop_tables
    drop_tables(list(tables))

@local_tvguide.command()
@click.option(
    '--date',
    default=Validation.get_current_date().strftime('%d-%m-%Y'),
    help='The date to retrieve the TVGuide schedule'
)
@click.option(
    '-d',
    '--discord',
    is_flag=True,
    default=False,
    help='Whether to send the message via Discord'
)
@click.option(
    '-s',
    '--schedule',
    is_flag=True,
    default=False,
    help='Add reminders to the scheduling service'
)
async def run_guide(date: str, discord: bool, schedule: bool):
    from datetime import datetime
    import re
    import sys

    from database import engine
    from database.models.GuideModel import Guide

    session = Session(engine, expire_on_commit=False)

    if re.search(r"\d{2}(-|\/)\d{2}(-|\/)\d{4}", date):
        date = date.replace('/', '-')
    else:
        sys.exit('Please provide a date in the format of DD-MM-YYYY or DD/MM/YYYY')
    
    guide = Guide(datetime.strptime(date, '%d-%m-%Y'), session)
    if schedule:
        from config import tvguide_scheduler
        if not tvguide_scheduler.scheduler_initialised:
            tvguide_scheduler.initialise()
        tvguide_scheduler.remove_all_jobs()
        guide.create_new_guide(tvguide_scheduler)
    else:
        guide.create_new_guide()
    guide_message, reminders_message, events_message = (
        guide.compose_message(),
        guide.compose_reminder_message(),
        guide.compose_events_message()
    )
    if discord:
        try:
            async with hermes:
                hermes.loop.create_task(
                    send_main_message(guide_message, reminders_message, events_message)
                )
                await hermes.start(os.getenv('HERMES'))
        except ClientConnectorDNSError:
            print(guide_message)
            print(reminders_message)
            print()
            print(events_message)
    else:
        print(guide_message)
        print(reminders_message)
        print()
        print(events_message)
    session.close()

@local_tvguide.command()
async def run_discord():
    """Use this for running Hermes commands"""
    try:
        await hermes.start(os.getenv('HERMES'))
    except asyncio.CancelledError:
        print("Hermes exiting")
        await hermes.close()



if __name__ == '__main__':
    local_tvguide()
