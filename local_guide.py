from discord import TextChannel
from aiohttp.client_exceptions import ClientConnectorError
from os import getenv
import sys

from guide import run_guide, search_free_to_air, search_bbc_australia, revert_database_tvguide
from log import log_message_sent
from services.hermes.hermes import hermes


def get_guide_data():
    fta_list = search_free_to_air(database_service)
    bbc_list = search_bbc_australia(database_service)
    return run_guide(database_service, fta_list, bbc_list)

async def send_main_message():
    """

    :param send_status:
    :return: n/a
    """
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(getenv('TVGUIDE_CHANNEL')))
    try:
        await tvguide_channel.send(guide_message)
        await tvguide_channel.send(reminder_message)
    except AttributeError:
        ngin = await hermes.fetch_user(int(getenv('NGIN')))
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    log_message_sent()
    # log_guide(fta_shows, bbc_shows)
    
    await hermes.close()

def local_message():
    fta_list = search_free_to_air(database_service)
    bbc_list = search_bbc_australia(database_service)
    guide_message, reminder_message = run_guide(database_service, fta_list, bbc_list)

    print(guide_message)
    print(reminder_message)

if __name__ == '__main__':
    from config import database_service
    if len(sys.argv):
        if '--revert-tvguide' in sys.argv[1]:
            from config import database_service
            revert_database_tvguide(database_service)
        elif '--no-discord' in sys.argv[1]:
            local_message()
    else:
        guide_message, reminder_message = get_guide_data()
        try:
            hermes.loop.create_task(send_main_message())
            hermes.run(getenv('HERMES'))
        except ClientConnectorError:
            print(guide_message)
            print(reminder_message)
            
