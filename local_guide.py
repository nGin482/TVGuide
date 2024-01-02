from discord import TextChannel
from os import getenv

from config import database_service
from guide import run_guide, search_free_to_air, revert_database_tvguide
from services.hermes.hermes import hermes


async def send_main_message():
    """

    :param send_status:
    :return: n/a
    """
    fta_list = search_free_to_air(database_service)
    guide_message, reminder_message = run_guide(database_service, fta_list)
    
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(getenv('TVGUIDE_CHANNEL')))
    try:
        await tvguide_channel.send(guide_message)
        await tvguide_channel.send(reminder_message)
    except AttributeError:
        ngin = await hermes.fetch_user(int(getenv('NGIN')))
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    # log_guide(fta_shows, bbc_shows)
    
    await hermes.close()

if __name__ == '__main__':
    hermes.loop.create_task(send_main_message())
    hermes.run(getenv('HERMES'))
    # revert_database_tvguide(database_service)