from apscheduler.triggers.cron import CronTrigger
from discord import TextChannel
from discord.errors import HTTPException
from dotenv import load_dotenv
from requests import get
from sqlalchemy.orm import Session
import os

os.environ['PYTHON_ENV'] = 'production'
from aux_methods.helper_methods import split_message_by_time
from config import scheduler
from data_validation.validation import Validation
from database import engine
from database.models.GuideModel import Guide
from exceptions.tvguide_errors import GuideNotCreatedError
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
    Create the TVGuide and send the messages
    """
    date = Validation.get_current_date()
    session = Session(engine, expire_on_commit=False)
    
    guide = Guide(date, session)
    
    await hermes.wait_until_ready()
    ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
    try:
        guide.create_new_guide(scheduler)
        guide_message = guide.compose_message()
        reminder_message = guide.compose_reminder_message()
        events_message = guide.compose_events_message()

        await hermes.send_guide_message(
            guide_message,
            reminder_message,
            events_message
        )
    except HTTPException as error:
        await ngin.send(f"There was a problem sending the TVGuide messages. Error: {str(error)}")
    except GuideNotCreatedError as error:
        await ngin.send(f"The TVGuide could not be created properly. Error: {str(error)}")
    except (AttributeError, TypeError, ValueError) as error:
        await ngin.send(f"There was a problem sending the TVGuide. Error: {str(error)}")
    finally:
        session.close()


if __name__ == '__main__':
    
    scheduler.add_job(
        send_main_message,
        CronTrigger(hour=9, timezone='Australia/Sydney'),
        id='TVGuide Message',
        name='Send the TVGuide message',
        misfire_grace_time=None,
        replace_existing=True
    )
    hermes.run(os.getenv('HERMES'))

    # {"id": "content_wrapper_inner"}
