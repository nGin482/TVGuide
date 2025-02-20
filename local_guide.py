from aiohttp.client_exceptions import ClientConnectorError
from discord import TextChannel
from dotenv import load_dotenv
import click
import os

load_dotenv('.env')

from data_validation.validation import Validation
from services.hermes.hermes import hermes


async def send_main_message(guide_message: str, reminder_message: str, events_message: str):
    """

    :param send_status:
    :return: n/a
    """
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(os.getenv('DEV_CHANNEL')))
    ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
    try:
        await tvguide_channel.send(guide_message)
    except AttributeError:
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    finally:
        await tvguide_channel.send(reminder_message)
        await tvguide_channel.send(events_message)
    
    await hermes.close()

@click.group()
def local_tvguide():
    pass

@local_tvguide.command()
@click.option('--resource', default='all', help='The data to import into the database')
@click.option('--local-db', default=True, help='The database to connect to')
@click.option('--database', default='development', help='The database to import data into')
def import_data(resource: str, local_db: bool, database: str):
    if local_db:
        database_connection = os.getenv('LOCAL_DB')
    else:
        database_connection = os.getenv('TVGUIDE_DB')
    from database.DatabaseService import DatabaseService
    database_service = DatabaseService(database_connection, database)
    database_service.import_data(resource)

@local_tvguide.command()
@click.option('--local-db', default=True, help='The database connection to use')
def tear_down_data(local_db: bool):
    if local_db:
        database_connection = os.getenv('LOCAL_DB')
    else:
        database_connection = os.getenv('TVGUIDE_DB')
    from database.DatabaseService import DatabaseService
    database_service = DatabaseService(database_connection, 'development')
    database_service.tear_down_data()

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
def migrate_data():
    from database.migration import db_migrate
    db_migrate()

@local_tvguide.command()
@click.option('--date', default=Validation.get_current_date().strftime('%d-%m-%Y'), help='The date to retrieve the TVGuide schedule')
@click.option('-d', '--discord', is_flag=True, default=False, help='Whether to send the message via Discord')
@click.option('-s', '--schedule', is_flag=True, default=False, help='Add reminders to the scheduling service')
def run_guide(date: str, discord: bool, schedule: bool):
    from datetime import datetime
    import re
    import sys

    from config import scheduler
    from database.models.GuideModel import Guide

    if re.search(r"\d{2}(-|\/)\d{2}(-|\/)\d{4}", date):
        date = date.replace('/', '-')
    else:
        sys.exit('Please provide a date in the format of DD-MM-YYYY or DD/MM/YYYY')
    
    guide = Guide(datetime.strptime(date, '%d-%m-%Y'))
    if schedule:
        scheduler.remove_all_jobs()
        guide.create_new_guide(scheduler)
    else:
        guide.create_new_guide()
    guide_message, reminders_message, events_message = (
        guide.compose_message(),
        guide.compose_reminder_message(),
        guide.compose_events_message()
    )
    if discord:
        try:
            hermes.loop.create_task(send_main_message(guide_message, reminders_message, events_message))
            hermes.run(os.getenv('HERMES'))
        except ClientConnectorError:
            print(guide_message)
            print(reminders_message)
            print(events_message)
    else:
        print(guide_message)
        print(reminders_message)
        print(events_message)


if __name__ == '__main__':
    local_tvguide()
    # from config import database_service
    # if '--local-db' in sys.argv:
    #     print(database_service)
    #     if '--no-discord' in sys.argv:
    #         local_message()
    #     elif '--import' in sys.argv:
    #         database_service.import_data()
    #     elif '--tear-down' in sys.argv:
    #         database_service.tear_down_data()
    #     else:
    #         guide_message, reminder_message, events_message = get_guide_data()
    #         try:
    #             hermes.loop.create_task(send_main_message())
    #             hermes.run(getenv('HERMES'))
    #         except ClientConnectorError:
    #             print(guide_message)
    #             print(reminder_message)
    # elif '--import' in sys.argv:
    #     database_service.import_data()
    # elif '--tear-down' in sys.argv:
    #     database_service.tear_down_data()
    # elif '--revert-tvguide' in sys.argv:
    #     revert_database_tvguide(database_service)
    # else:
    #     print('Invalid options have been provided')
    #     print('\n'.join(sys.argv))
            
