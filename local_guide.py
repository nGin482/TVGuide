from aiohttp.client_exceptions import ClientConnectorError
from discord import TextChannel
import click
import os

from database.DatabaseService import DatabaseService


async def send_main_message(guide_message: str, reminder_message: str, events_message: str):
    """

    :param send_status:
    :return: n/a
    """
    from services.hermes.hermes import hermes
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
    database_service = DatabaseService(database_connection, database)
    database_service.import_data(resource)

@local_tvguide.command()
@click.option('--local-db', default=True, help='The database connection to use')
def tear_down_data(local_db: bool):
    if local_db:
        database_connection = os.getenv('LOCAL_DB')
    else:
        database_connection = os.getenv('TVGUIDE_DB')
    database_service = DatabaseService(database_connection, 'development')
    database_service.tear_down_data()

@local_tvguide.command()
@click.option('--local-db', default=True, help='The database to connect to')
@click.option('--discord', default=True, help='Whether to send the message via Discord')
def run_guide(local_db: bool, discord: bool):
    from aux_methods.helper_methods import compose_events_message
    from dotenv import load_dotenv

    if local_db:
        os.environ['PYTHON_ENV'] = 'development'
        load_dotenv('.env.local.dev')
    else:
        os.environ['PYTHON_ENV'] = 'production'
    
    from guide import run_guide, search_free_to_air, search_bbc_australia
    from services.hermes.hermes import hermes

    fta_list = search_free_to_air()
    bbc_list = search_bbc_australia()
    guide_message, reminders_message = run_guide(fta_list, bbc_list)
    events_message = compose_events_message(fta_list + bbc_list)
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
            
