from repeat_handler import get_shows, convert_to_objects, flag_repeats, search_for_repeats
from log import write_to_log_file, compare_dates, delete_latest_entry, status_setting_repeats
from backups import write_to_backup_file
from datetime import datetime, date
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from aux_methods import format_time, format_title, show_list_for_message, doctor_who_episodes, morse_episodes, remove_doubles, write_to_today_file
from requests import get
from reminders import *
from database import get_showlist, insert_into_showlist_collection, remove_show_from_list
import discord
import click
import ssl
import os

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

    schedule = []

    text = get_page(url)
    soup = BeautifulSoup(text, 'html.parser')

    for div in soup('body', {'id': 'schedule'}):
        for article in div('article', {'id': 'bbc-first'}):
            schedule.append(article)
        for article in div('article', {'id': 'bbc-uktv'}):
            schedule.append(article)

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
    shows_on = []

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
                        show_dict['title'] = guide_show['title']
                        show_dict['channel'] = item['channel']
                        show_dict['time'] = datetime.strptime(guide_show['start_time'][-8:-3], '%H:%M')
                        show_dict['episode_info'] = False
                        if 'series_num' in guide_show.keys() and 'episode_num' in guide_show.keys():
                            show_dict['episode_info'] = True
                            show_dict['series_num'] = str(guide_show['series_num'])
                            show_dict['episode_num'] = str(guide_show['episode_num'])
                            if 'episode_title' in guide_show.keys():
                                show_dict['episode_title'] = format_title(guide_show['episode_title'])
                        if 'episode_title' in guide_show.keys():
                            show_dict['episode_info'] = True
                            show_dict['episode_title'] = format_title(guide_show['episode_title'])
                        show_dict['repeat'] = False
                        shows_on.append(show_dict)

    morse = {}
    remove_idx = []
    for idx, show in enumerate(shows_on):
        if 'New Orleans' in show['title']:
            remove_idx.append(idx)
        if 'Doctor Who' in show['title']:
            check_dw_title = doctor_who_episodes(show['title'])
            if show['title'] != check_dw_title:
                show['title'] = 'Doctor Who'
                show['series_num'] = str(check_dw_title[0])
                show['episode_num'] = str(check_dw_title[1])
                show['episode_title'] = check_dw_title[2]
        if 'Vera' in show['title']:
            if show['title'] != 'Vera':
                remove_idx.append(idx)
        if 'Endeavour' in show['title']:
            if show['title'] != 'Endeavour':
                remove_idx.append(idx)
        if 'Lewis' in show['title']:
            if show['title'] != 'Lewis':
                remove_idx.append(idx)
        if 'Morse' in show['title']:
            remove_idx.append(idx)
            titles = show['title'].split(': ')
            episode = morse_episodes(titles[1])
            morse = {'title': titles[0], 'time': show['time'], 'channel': show['channel'],
                     'episode_info': True, 'series_num': str(episode[0]), 'episode_num': str(episode[1]),
                     'episode_title': episode[2], 'repeat': False}
    for idx in reversed(remove_idx):
        shows_on.pop(idx)

    if morse:
        shows_on.append(morse)
    shows_on.sort(key=lambda show_obj: show_obj['time'])
    # check = check_time_sort(shows_on)
    # while check[0] != -1 and check[1] != -1:
    #     sort_shows_by_time(shows_on, check[0], check[1])
    #     check = check_time_sort(shows_on)
    remove_doubles(shows_on)

    return shows_on


def search_bbc_channels():
    """

    :return: list of shows airing on BBC channels during the current day
                list will contain a dict of each show's title, start time, channel and any episode information
    """

    url = 'https://www.bbcstudios.com.au/tv-guide/'

    schedule = find_info(url)
    bbc_first = schedule[0]
    bbc_uktv = schedule[1]

    shows_on = []

    for div in bbc_first('div', class_='event'):
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

                        shows_on.append({'title': title, 'channel': 'BBC First', 'time': start_time,
                                         'episode_info': True, 'series_num': series_num, 'episode_num': episode_num,
                                         'repeat': False})
                    else:
                        start_time = div.find('time').text[:7]
                        start_time = datetime.strptime(format_time(start_time), '%H:%M')

                        shows_on.append({'title': title, 'channel': 'BBC First', 'time': start_time,
                                         'episode_info': False, 'episode_tag': True, 'episode_title': episode_tag,
                                         'repeat': False})

    for div in bbc_uktv('div', class_='event'):
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
                                         'episode_info': False, 'episode_tag': True, 'episode_title': episode_tag,
                                         'repeat': False})

    shows_on.sort(key=lambda show_obj: show_obj['time'])
    # check = check_time_sort(shows_on)
    # while check[0] != -1 and check[1] != -1:
    #     sort_shows_by_time(shows_on, check[0], check[1])
    #     check = check_time_sort(shows_on)
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


def compose_message(status):
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

    bbc_shows = search_bbc_channels()
    fta_shows = search_free_to_air()

    # Free to Air
    message = message + "\nFree to Air:\n"
    if len(fta_shows) == 0:
        message = message + "Nothing on Free to Air today\n"
    else:
        for show in fta_shows:
            if status is True and show['episode_info']:
                search_for_repeats(show)
            time = show['time'].strftime('%H:%M')
            message = message + time + ': ' + show['title'] + " is on " + show['channel'] + "\n\n"
            if show['episode_info']:
                if 'series_num' in show.keys() and 'episode_num' in show.keys():
                    message = message[:-2] + " (Season " + str(show['series_num']) + ", Episode " + \
                              str(show['episode_num']) + ")\n\n"
                    if 'episode_title' in show.keys():
                        message = message[:-3] + ": " + show['episode_title'] + ")\n\n"
                if 'episode_title' in show.keys() and 'series_num' not in show.keys():
                    message = message[:-2] + " (" + show['episode_title'] + ")\n\n"
            if show['repeat']:
                message = message[:-2] + "(Repeat)\n\n"

    # BBC
    message = message + "\nBBC:\n"
    if len(bbc_shows) == 0 or bbc_shows[0] is []:
        message = message + "Nothing on BBC today\n"
    else:
        for show in bbc_shows:
            if status is True:
                search_for_repeats(show)
            time = show['time'].strftime('%H:%M')
            if show['episode_info']:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (Series " + show['series_num'] + ", Episode " + show['episode_num'] + ")\n\n"
            else:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (" + show['episode_title'] + ")\n\n"
            if show['repeat']:
                message = message[:-2] + "(Repeat)\n\n"

    return message


async def send_message(send_status):
    """

    :param send_status:
    :return: n/a
    """
    message = compose_message(send_status)
    print(message)
    
    if send_status:
        await client.wait_until_ready()
        tvguide_channel = client.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
        try:
            await tvguide_channel.send(message)
        except AttributeError:
            ngin = await client.fetch_user(int(os.getenv('NGIN')))
            await ngin.send('The channel resolved to NoneType so the message could not be sent')
        write_to_log_file()
        add_to_files()
    
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
            await message.channel.send(show_list_for_message())
        if '$add-show' in message.content:
            new_show = message.content.split(' ')[1]
            insert_into_showlist_collection(new_show)
            new_message = new_show + ' has been added to the list. The list now includes:\n' + show_list_for_message()
            await message.channel.send(new_message)
        if '$remove-show' in message.content:
            show_to_remove = message.content[message.content.index('-show')+6:]
            remove_show = remove_show_from_list(show_to_remove)
            if remove_show['status']:
                reply = remove_show['message'] + ' The list now includes:\n' + show_list_for_message()
            else:
                reply = remove_show['message'] + ' The list remains as:\n' + show_list_for_message()
            await message.channel.send(reply)


@click.group()
def cli():
    pass


@cli.command()
def send_email():
    """
    Searches the TV guides for the list of shows and sends the results in an email
    """
    status = compare_dates()
    print(status)
    send_message(status)


@cli.command()
def delete_log_entry():
    """
    Deletes the latest log entry
    """
    delete_latest_entry()


@cli.command()
def add_show():
    """
    Adds the given show into the list of shows
    """
    insert_into_showlist_collection()


@cli.command()
def show_list():
    """
    Displays the current list of shows that the TVGuide is searching for
    """
    for show in get_showlist:
        print(show)


def collate_today_data():

    superlist = []
    data = check_site()

    get_shows(data['FTA'], superlist)
    get_shows(data['BBC'], superlist)

    return superlist


def add_to_files():

    todays_viewings = convert_to_objects(collate_today_data())
    write_to_backup_file(todays_viewings)
    write_to_today_file(todays_viewings)
    
    for show in search_free_to_air():
        if 'HD' not in show['channel'] and 'GEM' not in show['channel'] and show['episode_info']:
            log_repeats = flag_repeats(show)
            status_setting_repeats(log_repeats)
    for show in search_bbc_channels():
        log_repeats = flag_repeats(show)
        status_setting_repeats(log_repeats)


if __name__ == '__main__':
    status = compare_dates()
    print(status)
    show_list = get_showlist()
    client.loop.create_task(send_message(status))
    client.run(os.getenv('HERMES'))

    # add_show_to_list('Baptiste')
    # delete_latest_entry()

    # send_message(websites, False)
    # search_free_to_air()

    # get_date_from_latest_email()
    # compare_dates()

    # {"id": "content_wrapper_inner"}
