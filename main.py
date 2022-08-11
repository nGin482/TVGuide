
from aux_methods.helper_methods import format_time, show_list_for_message, remove_doubles, check_show_titles, show_string
from aux_methods.episode_info import morse_episodes, silent_witness_episode, search_episode_information, red_election
from database.models import DoctorWhoGuideShow, GuideShow, TransformersGuideShow
from database.show_list_collection import search_list, insert_into_showlist_collection, remove_show_from_list
from database.recorded_shows_collection import backup_recorded_shows
from exceptions.BBCNotCollectedException import BBCNotCollectedException
from repeat_handler import flag_repeats, search_for_repeats, get_today_shows_data
from log import log_discord_message_too_long, log_message_sent, compare_dates, log_guide, revert_tvguide
from backups import write_to_backup_file
from datetime import datetime, date
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests import get
from reminders import *
import discord
import os
import re

load_dotenv('.env')
client = discord.Client()

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


def search_free_to_air():
    """

    :return:
    """

    current_date = datetime.today().date()
    new_url = 'https://epg.abctv.net.au/processed/Sydney_' + str(current_date) + ".json"
    shows_on: list[GuideShow] = []

    data = find_json(new_url)['schedule']

    for item in data:
        listing = item['listing']

        # print("Listing: " + str(listing))
        for guide_show in listing:
            title = guide_show['title']
            for show in show_list:
                if show in title:
                    show_dict = {}
                    show_date = guide_show['start_time'][:-9]
                    if int(show_date[-2:]) == int(datetime.today().day):
                        episode_info = False
                        season_number = ''
                        episode_number = 0
                        episode_title = ''
                        if 'series_num' in guide_show.keys() and 'episode_num' in guide_show.keys():
                            episode_info = True
                            season_number = str(guide_show['series_num'])
                            episode_number = guide_show['episode_num']
                            if 'episode_title' in guide_show.keys():
                                episode_title = guide_show['episode_title']
                        if 'episode_title' in guide_show.keys():
                            episode_info = True
                            episode_title = guide_show['episode_title']
                        show_object = GuideShow(
                            guide_show['title'],
                            item['channel'],
                            datetime.strptime(guide_show['start_time'][-8:-3], '%H:%M'),
                            episode_info,
                            season_number,
                            episode_number,
                            episode_title
                        )
                        shows_on.append(show_object)

    morse = {}
    remove_idx = []
    show: GuideShow
    for idx, show in enumerate(shows_on):
        if 'New Orleans' in show.title:
            remove_idx.append(idx)
        if 'Doctor Who' in show.title:
            show = DoctorWhoGuideShow.doctor_who_handle(show)
        if 'Vera' in show.title:
            if show.title != 'Vera':
                remove_idx.append(idx)
        if 'Endeavour' in show.title:
            if show.title != 'Endeavour':
                remove_idx.append(idx)
        if 'Lewis' in show.title:
            if show.title != 'Lewis':
                remove_idx.append(idx)
        if 'Morse' in show.title:
            remove_idx.append(idx)
            titles = show.title.split(': ')
            episode = morse_episodes(titles[1])
            morse = GuideShow(
                titles[0], show.time, show.channel,
                True, str(episode[0]), episode[1], episode[2]
            )
        if 'Transformers' in show.title or 'Bumblebee' in show.title:
            show = TransformersGuideShow().transformers_handle()
        if 'Red Election' in show.title:
            show = red_election(show)
        if 'Silent Witness' in show.title:
            silent_witness_status = silent_witness_episode(show)
            if silent_witness_status['status']:
                show = silent_witness_status['show']
            else:
                remove_idx.append(idx)
    for idx in reversed(remove_idx):
        shows_on.pop(idx)

    if morse:
        shows_on.append(morse)
    shows_on.sort(key=lambda show_obj: show_obj.time)
    # check = check_time_sort(shows_on)
    # while check[0] != -1 and check[1] != -1:
    #     sort_shows_by_time(shows_on, check[0], check[1])
    #     check = check_time_sort(shows_on)
    remove_doubles(shows_on)
    print(len(shows_on))
    show_titles = [show.title for show in shows_on]
    get_today_shows_data(show_titles)
    # # if imdb_api_status == 200:
    # #     shows_on = [search_episode_information(show) for show in shows_on]
    # else:
    #     print('IMDB API is not available')
    shows_on = [search_for_repeats(show) for show in shows_on]

    return shows_on


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

    remove_idx = []
    for idx, show in enumerate(shows_on):
        if 'Silent Witness' in show['title']:
            silent_witness_status = silent_witness_episode(show)
            if silent_witness_status['status']:
                show = silent_witness_status['show']
            else:
                remove_idx.append(idx)
    for index in reversed(remove_idx):
        shows_on.pop(index)
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
    shows_on = [search_for_repeats(show) for show in shows_on]
    return shows_on


def check_site():
    """

    :return: a dictionary of shows on, where key is based on url and value is the list of scheduled shows
    """

    shows_on = {'BBC': search_bbc_channels(),
                'FTA': search_free_to_air(),
                'Latest Vera Series': search_vera_series()
                }

    return shows_on


def compose_message():
    """
    toString function that writes the shows, times, channels and episode information (if available) via natural language
    :return: the to-string message
    """
    weekdays = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ]

    message_date = datetime.today().date()
    message = weekdays[message_date.weekday()] + " " + str(message_date.strftime('%d-%m-%Y')) + " TVGuide\n"

    # Free to Air
    message = message + "\nFree to Air:\n"
    if len(fta_shows) == 0:
        message = message + "Nothing on Free to Air today\n"
    else:
        for show in fta_shows:
            message += show.message_string()

    # BBC
    message = message + "\nBBC:\n"
    if len(bbc_shows) == 0 or bbc_shows[0] is []:
        message = message + "Nothing on BBC today\n"
    else:
        for show in bbc_shows:
            show['time'] = show['time'].strftime('%H:%M')
            message = message + show_string(show)

    return message


async def send_message():
    """

    :param send_status:
    :return: n/a
    """
    message = compose_message()
    print(message)
    
    if status:
        await client.wait_until_ready()
        tvguide_channel = client.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
        try:
            if len(message) > 2000:
                bbc_idx = message.find("BBC: ")

                fta_message = message[:bbc_idx]
                bbc_message = message[bbc_idx:]

                if len(fta_message) > 2000:
                    print(len(fta_message))
                    
                    fta_pm_idx = re.search('[1][2]:[0-5][0-9]:', fta_message).start()
                    
                    fta_am_message = fta_message[:fta_pm_idx] +  '\n\n'
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
            ngin = await client.fetch_user(int(os.getenv('NGIN')))
            await ngin.send('The channel resolved to NoneType so the message could not be sent')
        log_message_sent()
        log_guide(fta_shows, bbc_shows)
    
    await client.close()

@client.event
async def on_ready():
    print('Logged in as', client.user)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if 'tv-guide' in str(message.channel):
        if '$show-list' in message.content:
            await message.channel.send(show_list_for_message(show_list))
        if '$add-show' in message.content:
            new_show = message.content.split(' ')[1]
            insert_into_showlist_collection(new_show)
            new_message = new_show + ' has been added to the list. The list now includes:\n' + show_list_for_message(show_list)
            await message.channel.send(new_message)
        if '$remove-show' in message.content:
            show_to_remove = message.content[message.content.index('-show')+6:]
            remove_show = remove_show_from_list(show_to_remove)
            if remove_show['status']:
                reply = remove_show['message'] + ' The list now includes:\n' + show_list_for_message(show_list)
            else:
                reply = remove_show['message'] + ' The list remains as:\n' + show_list_for_message(show_list)
            await message.channel.send(reply)


if __name__ == '__main__':
    status = compare_dates()
    print(status)
    show_list = search_list()
    imdb_api_status = get('https://imdb-api.com/').status_code
    fta_shows = search_free_to_air()
    bbc_shows = search_bbc_channels()

    # backup_recorded_shows()
    
    # client.loop.create_task(send_message())
    # client.run(os.getenv('HERMES'))
    print(compose_message())

    # print(reminders_found())
    # check_reminders_interval()
    # compare_reminder_interval()
    calculate_reminder_time()

    # revert_tvguide()

    # add_show_to_list('Baptiste')
    # delete_latest_entry()

    # send_message(websites, False)
    # print(search_bbc_channels())

    # get_date_from_latest_email()
    # compare_dates()

    # {"id": "content_wrapper_inner"}
