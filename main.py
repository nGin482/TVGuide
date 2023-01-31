from bs4 import BeautifulSoup
from datetime import datetime
from discord import Client, Message, TextChannel
from dotenv import load_dotenv
from requests import get
import os
import re

from aux_methods.helper_methods import format_time, show_list_message, check_show_titles
from aux_methods.episode_info import search_episode_information
from data_validation.validation import Validation
from database.DatabaseService import DatabaseService
from database.mongo import mongo_client
from exceptions.BBCNotCollectedException import BBCNotCollectedException
from exceptions.DatabaseError import DatabaseError, SearchItemAlreadyExistsError, SearchItemNotFoundError
from guide import run_guide, revert_tvguide
from log import log_discord_message_too_long, log_message_sent
from repeat_handler import get_today_shows_data

load_dotenv('.env')
discord_client = Client()

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
    if imdb_api_status == 200:
        shows_on = [search_episode_information(show) for show in shows_on]
    else:
        print('IMDB API is not available')
    return shows_on


async def send_message():
    """

    :param send_status:
    :return: n/a
    """
    message = run_guide(database_service)
    
    await discord_client.wait_until_ready()
    tvguide_channel: TextChannel = discord_client.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
    try:
        if len(message) > 2000:
            bbc_idx = message.find("BBC: ")

            fta_message = message[:bbc_idx]
            bbc_message = message[bbc_idx:]

            if len(fta_message) > 2000:
                print(len(fta_message))
                
                fta_pm_idx = re.search('12:[0-5][0-9]:', fta_message).start()
                
                fta_am_message = fta_message[:fta_pm_idx] + '\n\n'
                fta_pm_message = fta_message[fta_pm_idx:]

                await tvguide_channel.send(fta_am_message)
                await tvguide_channel.send(fta_pm_message)
                # await tvguide_channel.send(bbc_message)

                log_discord_message_too_long(len(message), len(fta_message))
            else:
                await tvguide_channel.send(fta_message)
                await tvguide_channel.send(bbc_message)


            
            # still too big on Thursday 18/11/21
        else:
            await tvguide_channel.send(message)
    except AttributeError:
        ngin = await discord_client.fetch_user(int(os.getenv('NGIN')))
        await ngin.send('The channel resolved to NoneType so the message could not be sent')
    log_message_sent()
    # log_guide(fta_shows, bbc_shows)
    
    await discord_client.close()

@discord_client.event
async def on_ready():
    print('Logged in as', discord_client.user)

@discord_client.event
async def on_message(message: Message):
    if message.author == discord_client.user:
        return
    if 'tv-guide' in str(message.channel):
        if '$show-list' in message.content:
            await message.channel.send(show_list_message(database_service.get_search_list()))
        if '$add-show' in message.content:
            new_show = message.content.split(' ')[1]
            try:
                database_service.insert_into_showlist_collection(new_show)
                reply = f'{new_show} has been added to the list. The list now includes:\n{show_list_message(database_service.get_search_list())}'
            except SearchItemAlreadyExistsError | DatabaseError as err:
                reply = f'Error: {str(err)}. The List has not been modified.'
            await message.channel.send(reply)
        if '$remove-show' in message.content:
            show_to_remove = message.content[message.content.index('-show')+6:]
            try:
                database_service.remove_show_from_list(show_to_remove)
                reply = f'{show_to_remove} has been removed from the SearchList. The list now includes:\n' + show_list_message(database_service.get_search_list())
            except DatabaseError | SearchItemNotFoundError as err:
                reply = f'{str(err)}. The list remains as:\n' + show_list_message(database_service.get_search_list())

            await message.channel.send(reply)


if __name__ == '__main__':
    
    database_service = DatabaseService(mongo_client().get_database('tvguide'))

    # status = compare_dates()
    # print(status)
    # show_list = search_list()
    imdb_api_status = get('https://imdb-api.com/').status_code
    # clear_imdb_api_results()
    # RecordedShow.backup_recorded_shows()
    # fta_shows = search_free_to_air()
    # bbc_shows = search_bbc_channels()

    discord_client.loop.create_task(send_message())
    discord_client.run(os.getenv('HERMES'))
    # print(compose_message())

    # print(reminders_found())
    # check_reminders_interval()
    # compare_reminder_interval()

    # calculate_reminder_time(show_list)

    # revert_tvguide(database_service)

    # add_show_to_list('Baptiste')
    # delete_latest_entry()

    # send_message(websites, False)
    # print(search_bbc_channels())

    # get_date_from_latest_email()
    # compare_dates()

    # {"id": "content_wrapper_inner"}
