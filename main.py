from apscheduler.triggers.cron import CronTrigger
from discord import TextChannel
from discord.errors import HTTPException
from dotenv import load_dotenv
from requests import get
import os

os.environ['PYTHON_ENV'] = 'production'
from aux_methods.helper_methods import compose_events_message, split_message_by_time
from config import scheduler
from guide import run_guide, search_free_to_air, search_bbc_australia
from services.hermes.hermes import hermes

load_dotenv('.env')

# https://epg.abctv.net.au/processed/events_Sydney_vera.json
# https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177


def find_json(url):
    data = get(url).json()

    return data


def search_vera_series():

    url = 'https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177'

    try:
        data = find_json(url)
        series_num = int(data[-1]['seriesNumber'])
    except ValueError:
        # print(e.msg)
        code = get(url).status_code
        series_num = "ABC's Vera page is responding with " + str(code) + " and is temporarily unavailable"

    return series_num


async def send_main_message():
    """

    :param `database_service`: The service handler for database operations
    :return: n/a
    """
    fta_list = search_free_to_air()
    bbc_list = search_bbc_australia()
    guide_message, reminder_message = run_guide(fta_list, bbc_list, scheduler)
    
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
    ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
    try:
        await tvguide_channel.send(guide_message)
    except HTTPException as error:
        if 'In content: Must be 2000 or fewer in length' in error.text:
            bbc_index = guide_message.find('\nBBC:\n')
            fta_message = guide_message[0:bbc_index]
            bbc_message = guide_message[bbc_index:]
            
            if len(fta_message) > 2000:
                fta_am_message, fta_pm_message = split_message_by_time(fta_message)
                await tvguide_channel.send(fta_am_message)
                await tvguide_channel.send(fta_pm_message)
            else:
                await tvguide_channel.send(fta_message)

            if len(bbc_message) > 2000:
                bbc_am_message, bbc_pm_message = split_message_by_time(bbc_message)
                await tvguide_channel.send(bbc_am_message)
                await tvguide_channel.send(bbc_pm_message)
            else:
                await tvguide_channel.send(bbc_message)
    except AttributeError:
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    finally:
        await tvguide_channel.send(reminder_message)
        await ngin.send(compose_events_message(fta_list + bbc_list))


if __name__ == '__main__':
    
    scheduler.add_job(
        send_main_message,
        CronTrigger(hour=9, timezone='Australia/Sydney'),
        id='TVGuide Message',
        name='Send the TVGuide message',
        misfire_grace_time=None,
        replace_existing=True
    )
    scheduler.start()
    hermes.run(os.getenv('HERMES'))

    # {"id": "content_wrapper_inner"}
