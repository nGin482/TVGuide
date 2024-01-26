from discord import TextChannel
from aiohttp.client_exceptions import ClientConnectorError
from os import getenv
import sys

from guide import run_guide, search_free_to_air, search_bbc_australia, revert_database_tvguide
from aux_methods.helper_methods import compose_events_message
from services.hermes.hermes import hermes


def get_guide_data():
    fta_list = search_free_to_air(database_service)
    bbc_list = search_bbc_australia(database_service)
    guide_message, reminders_message = run_guide(database_service, fta_list, bbc_list)
    events_message = compose_events_message(fta_list + bbc_list)
    return guide_message, reminders_message, events_message

async def send_main_message():
    """

    :param send_status:
    :return: n/a
    """
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(getenv('DEV_CHANNEL')))
    ngin = await hermes.fetch_user(int(getenv('NGIN')))
    try:
        await tvguide_channel.send(guide_message)
    except AttributeError:
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    finally:
        await tvguide_channel.send(reminder_message)
        await ngin.send(events_message)
    
    await hermes.close()

def local_message():
    guide_message, reminder_message, events_message = get_guide_data()

    print(guide_message)
    print(reminder_message)
    print(events_message)

if __name__ == '__main__':
    from config import database_service
    if '--local-db' in sys.argv:
        print(database_service)
        if '--no-discord' in sys.argv:
            local_message()
        elif '--import' in sys.argv:
            database_service.import_data()
        elif '--tear-down' in sys.argv:
            database_service.tear_down_data()
        else:
            guide_message, reminder_message, events_message = get_guide_data()
            try:
                hermes.loop.create_task(send_main_message())
                hermes.run(getenv('HERMES'))
            except ClientConnectorError:
                print(guide_message)
                print(reminder_message)
    elif '--import' in sys.argv:
        database_service.import_data()
    elif '--tear-down' in sys.argv:
        database_service.tear_down_data()
    elif '--revert-tvguide' in sys.argv:
        revert_database_tvguide(database_service)
    else:
        print('Invalid options have been provided')
        print('\n'.join(sys.argv))
            
