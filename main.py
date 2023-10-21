from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup
from datetime import datetime
from discord import TextChannel
from dotenv import load_dotenv
from requests import get
import os

from aux_methods.helper_methods import format_time, check_show_titles, compose_events_message
from config import database_service, scheduler
from data_validation.validation import Validation
from database.DatabaseService import DatabaseService
from exceptions.tvguide_errors import BBCNotCollectedException
from guide import run_guide, search_free_to_air
from repeat_handler import get_today_shows_data
from services.hermes.hermes import hermes

load_dotenv('.env')

# https://epg.abctv.net.au/processed/events_Sydney_vera.json
# https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177


def get_page(url):
    """Download the given webpage and decode it"""

    headers = {
        'User-Agent': 'Chrome/90.0.4430.212'
    }
    fd = get(url, headers=headers)
    content = fd.text
    fd.close()

    return content


def find_info(url):
    """Searches the page for information"""

    schedule = [
        {
            'channel': 'BBC First',
            'schedule': []
        },
        {
            'channel': 'BBC UKTV',
            'schedule': []
        }
    ]

    bbc_first_flag = True
    bbc_uktv_flag = True

    text = get_page(url)
    soup = BeautifulSoup(text, 'html.parser')

    channel_block: BeautifulSoup
    channel_blocks: BeautifulSoup = soup.find_all('div', class_='channel-block')
    # print(channel_blocks)
    for channel_block in channel_blocks:
        # print(channel_block.find('div', class_='channel-patch').attrs)
        if 'bbc-first' in channel_block.find('div', class_='channel-patch').attrs['class'][1]:
            # for window in channel_block.find_('div', class_='channel-window'):
            #     print(window)
            channel_window: BeautifulSoup = channel_block.find('div', class_='channel-window')
            if 'no-events' in channel_window.attrs['class']:
                bbc_first_flag = False
            else:
                print(channel_window)
                channel_container: BeautifulSoup = channel_window.find('div', class_='channel-container')
                schedule[0]['schedule'].append(channel_container)
        if 'bbc-uktv' in channel_block.find('div', class_='channel-patch').attrs['class'][1]:
            channel_window: BeautifulSoup = channel_block.find('div', class_='channel-window')
            if 'no-events' in channel_window.attrs['class']:
                bbc_uktv_flag = False
            else:
                print(channel_block)
                print(channel_window)
                channel_container: BeautifulSoup = channel_window.find('div', class_='channel-container')
                schedule[1]['schedule'].append(channel_container)

    if not bbc_first_flag and not bbc_uktv_flag:
        raise BBCNotCollectedException('BBC Guide data can not be collected at this time.')
    print()
    print(schedule)
    return schedule
    # except urllib.error.URLError:
    #     return schedule.append({'error': 'Error accessing page'})


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


def search_bbc_channels():
    """

    :return: list of shows airing on BBC channels during the current day
                list will contain a dict of each show's title, start time, channel and any episode information
    """

    url = 'https://www.bbcstudios.com.au/tv-guide/'

    try:
        schedule = find_info(url)
    except BBCNotCollectedException:
        # TODO: Need a way to notify if this is raised
        return []
    bbc_first = schedule[0]['schedule']
    bbc_uktv = schedule[1]['schedule']

    shows_on = []

    if len(bbc_first) > 0:
        for div in bbc_first[0]('div', class_='event-block'):
            title = div.find('h4').text
            episode_tag = div.find('h5').text
            for show in show_list:
                if show in title:
                    if show[0] == title[0]:
                        if 'Series' in episode_tag:
                            series_num = episode_tag[7:8]
                            episode_num = episode_tag[-1:]

                            start_time = div.find('time').text[:7]
                            start_time = datetime.strptime(format_time(start_time), '%H:%M')

                            shows_on.append({'title': title, 'channel': 'BBC First', 'time': start_time,
                                            'episode_info': True, 'series_num': series_num, 'episode_num': episode_num,
                                            'repeat': False})
                        else:
                            start_time = div.find('time').text[:7]
                            start_time = datetime.strptime(format_time(start_time), '%H:%M')

                            shows_on.append({'title': title, 'channel': 'BBC First', 'time': start_time,
                                            'episode_info': True, 'episode_title': episode_tag,
                                            'repeat': False})

    if len(bbc_uktv) > 0:
        for div in bbc_uktv[0]('div', class_='event'):
            title = div.find('h3').text
            episode_tag = div.find('h4').text
            for show in show_list:
                if show in title:
                    if show[0] == title[0]:
                        if 'Series' in episode_tag:
                            series_num = episode_tag[7:8]
                            episode_num = episode_tag[-1:]

                            start_time = div.find('time').text[:7]
                            start_time = datetime.strptime(format_time(start_time), '%H:%M')

                            shows_on.append({'title': title, 'channel': 'UKTV', 'time': start_time,
                                            'episode_info': True, 'series_num': series_num, 'episode_num': episode_num,
                                            'repeat': False})
                        else:
                            start_time = div.find('time').text[:7]
                            start_time = datetime.strptime(format_time(start_time), '%H:%M')

                            shows_on.append({'title': title, 'channel': 'UKTV', 'time': start_time,
                                            'episode_info': True, 'episode_title': episode_tag,
                                            'repeat': False})

    shows_on = Validation.remove_unwanted_shows(shows_on)
    shows_on.sort(key=lambda show_obj: show_obj['time'])
    # check = check_time_sort(shows_on)
    # while check[0] != -1 and check[1] != -1:
    #     sort_shows_by_time(shows_on, check[0], check[1])
    #     check = check_time_sort(shows_on)
    show_titles = [check_show_titles(show['title']) for show in shows_on]
    get_today_shows_data(show_titles)
    
    return shows_on

async def send_main_message(database_service: DatabaseService):
    """

    :param send_status:
    :return: n/a
    """
    fta_list = search_free_to_air(database_service)
    guide_message, reminder_message = run_guide(database_service, fta_list, scheduler)
    
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
    ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
    try:
        await tvguide_channel.send(guide_message)
        await tvguide_channel.send(reminder_message)
        await ngin.send(compose_events_message())
    except AttributeError:
        await ngin.send('The channel resolved to NoneType so the message could not be sent')


if __name__ == '__main__':
    
    scheduler.add_job(send_main_message, CronTrigger(hour=9, timezone='Australia/Sydney'), [database_service], misfire_grace_time=None)
    scheduler.start()
    hermes.run(os.getenv('HERMES'))

    # {"id": "content_wrapper_inner"}
