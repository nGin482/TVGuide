from repeat_handler import get_shows, convert_to_objects, flag_repeats, search_for_repeats
from log import write_to_log_file, compare_dates, delete_latest_entry
from backups import write_to_backup_file
from datetime import datetime, date
# from urllib.request import urlopen
# from dotenv import load_dotenv
from bs4 import BeautifulSoup
from aux_methods import *
from requests import get
# from urllib import error
import smtplib
import imaplib
import email
import click
# import json
import ssl
import os

# load_dotenv()

"https://epg.abctv.net.au/processed/events_Sydney_vera.json"
"https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177"


def get_page(url):
    """Download the given webpage and decode it"""

    fd = get(url)
    content = fd.text
    fd.close()

    return content


def find_info(url):
    """Searches the page for information"""

    schedule = []

    text = get_page(url)
    soup = BeautifulSoup(text, 'html.parser')

    for div in soup('div', class_='mask js-init-opacity-0'):
        for article in div('article', {"id": "bbc-first"}):
            schedule.append(article)
        for article in div('article', {"id": "bbc-uktv"}):
            schedule.append(article)

    return schedule
    # except urllib.error.URLError:
    #     return schedule.append({'error': 'Error accessing page'})


def find_json(url):
    # print(response)
    # try:
    #     response = urlopen(url)
    #     data = json.loads(response.read().decode())
    # except UnicodeDecodeError:
    #     data = get(url).json()
    #     data = json.loads(response.read().decode(errors='ignore'))
    #     data = json.loads(gzip.decompress(get(url).content))
    data = get(url).json()
    # print(data)

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
            for show in get_show_list():
                if show in title:
                    show_dict = {}
                    show_date = guide_show['start_time'][:-9]
                    if int(show_date[-2:]) == int(datetime.today().day):
                        show_dict['title'] = guide_show['title']
                        show_dict['channel'] = item['channel']
                        # print(guide_show['start_time'][-8:-3])
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
            if show['title'] != 'Doctor Who':
                remove_idx.append(idx)
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

    url = 'https://www.bbcaustralia.com/tv-guide/'

    schedule = find_info(url)
    bbc_first = schedule[0]
    bbc_uktv = schedule[1]

    shows_on = []

    for div in bbc_first('div', class_='event'):
        title = div.find('h3').text
        episode_tag = div.find('h4').text
        for show in get_show_list():
            if show in title:
                if show[0] == title[0]:
                    if 'Series' in episode_tag:
                        series_num = episode_tag[7:8]
                        episode_num = episode_tag[-1:]
                        # print("Series: " + series_num + " Episode " + episode_num)

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
                if 'Baptiste' in title:
                    print('This is being printed to serve a reminder for Baptiste repeats for BBC First')

    for div in bbc_uktv('div', class_='event'):
        title = div.find('h3').text
        episode_tag = div.find('h4').text
        for show in get_show_list():
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
            message = message + time + ': ' + show['title'] + " is on " + show['channel'] + "\n"
            if show['episode_info']:
                if 'series_num' in show.keys() and 'episode_num' in show.keys():
                    message = message[:-1] + " (Season " + str(show['series_num']) + ", Episode " + \
                              str(show['episode_num']) + ")\n"
                    if 'episode_title' in show.keys():
                        message = message[:-2] + ": " + show['episode_title'] + ")\n"
                if 'episode_title' in show.keys() and 'series_num' not in show.keys():
                    message = message[:-1] + " (" + show['episode_title'] + ")\n"
            if show['repeat']:
                message = message[:-1] + "(Repeat)\n"

    # BBC
    message = message + "\nBBC:\n"
    if len(bbc_shows) == 0:
        message = message + "Nothing on BBC today\n"
    else:
        for show in bbc_shows:
            if status is True:
                search_for_repeats(show)
            time = show['time'].strftime('%H:%M')
            if show['episode_info']:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (Series " + show['series_num'] + ", Episode " + show['episode_num'] + ")\n"
            else:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (" + show['episode_title'] + ")\n"
            if show['repeat']:
                message = message[:-1] + "(Repeat)\n"
    # message = message + "\nThe latest Vera series on the ABC is " + str(shows_on['Latest Vera Series'])

    return message


def send_message(send_status):
    """

    :param send_status:
    :return:
    """
    # try:
    #     print("hello")
    # except smtplib.SMTPAuthenticationError:
    #     print("try again")

    # print(os.environ.get('EMAIL'))
    if send_status:
        port = 465
        pw = input("Type your password: ")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            sender = "nGinTest259@gmail.com"
            receiver = sender
            try:
                server.login(sender, pw)
            except smtplib.SMTPAuthenticationError:
                pw = input('The password was incorrect. Try again: ')
                server.login(sender, pw)
            message = "From: " + sender + " TVGuide-main.py\nTo: " + receiver + \
                      "\nSubject: TV Guide \n\n" + compose_message(send_status)
            server.sendmail(sender, receiver, message)
            server.quit()
        print(message + "\nAn email was sent")
        write_to_log_file()
        add_to_files()
    else:
        print(compose_message(send_status))


def search_emails():
    # not used, deprecated

    address = 'nGinTest259@gmail.com'
    pw = input('Password: ')

    mail = imaplib.IMAP4_SSL('imap.gmail.com')

    mail.login(address, pw)
    mail.select('Inbox')

    search = '(SINCE "' + date.strftime(date.today(), '%d-%b-%Y') + '")'
    print(search)
    response, data = mail.search(None, search)
    print(data)
    mail_ids = data[0]

    id_list = mail_ids.split()
    print(id_list)
    if len(id_list) == 0:
        return True
    else:
        latest_id = id_list[-1]

    data = mail.fetch(latest_id, '(RFC822)')
    for response_part in data:
        if isinstance(response_part[0], tuple):
            msg = email.message_from_string(response_part[0][1].decode('utf-8'))
            if date.strftime(date.today(), '%d-%m-%Y') + ' TVGuide' not in str(msg):
                mail.logout()
                return True
            else:
                mail.logout()
                return False

    # email headers --> https://pymotw.com/2/imaplib/#whole-messages


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
    add_show_to_list()


@cli.command()
def show_list():
    """
    Displays the current list of shows that the TVGuide is searching for
    """
    for show in get_show_list():
        print(show)


def collate_today_data():

    superlist = []
    data = check_site()

    get_shows(data['BBC'], superlist)
    get_shows(data['FTA'], superlist)

    return superlist


def add_to_files():

    data = convert_to_objects(collate_today_data())
    write_to_backup_file(data)
    for show in search_free_to_air():
        if 'HD' not in show['channel'] and 'GEM' not in show['channel'] and show['episode_info']:
            flag_repeats(show)
    for show in search_bbc_channels():
        flag_repeats(show)


if __name__ == '__main__':
    # findInfo('https://www.abc.net.au/tv/epg/index.html#')
    # findInfo('https://www.abc.net.au/tv/programs/vera/#/episode/ZW1684A001S00')
    # findJSON('https://www.abc.net.au/tv/epg/index.html#')
    # findJSON('https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177')
    # findJSON('https://epg.nbcu-paint.io/13au/18-04-2019.json')
    # print(findJSON('https://epg.nbcu-paint.io/13au/18-04-2019.json')[0])
    # searchVeraSeries('https://www.abc.net.au/tv/programs/vera/series-episode-index.json?_=1555488755177')
    # print()
    # print("===============================")
    # search13thStreet('https://epg.nbcu-paint.io/13au/')
    # print("===============================")
    # findInfo('https://www.bbcaustralia.com/tv-guide/')
    # print("===============================")
    # searchFreeToAir('https://epg.abctv.net.au/processed/Sydney_')
    # print("===============================")
    # searchBBCChannels('https://www.bbcaustralia.com/tv-guide/')

    # shows = [
    #     'Vera',
    #     'Endeavour',
    #     'Lewis',
    #     'Maigret',
    #     'Unforgotten',
    #     'Death in Paradise',
    #     'Death In Paradise',
    #     'Shetland',
    #     'NCIS',
    #     'NCIS: Los Angeles',
    #     'Mock The Week',
    #     'No Offence',
    #     'Mad As Hell',
    #     'Grantchester',
    #     'Doctor Who',
    #     'Transformers',
    #     'Inspector Morse',
    # ]
    # websites = ['https://epg.nbcu-paint.io/13au/']
    cli()

    # add_show_to_list('Baptiste')
    # delete_latest_entry()

    # send_message(websites, False)
    # search_free_to_air()

    # get_date_from_latest_email()
    # compare_dates()

    # {"id": "content_wrapper_inner"}
