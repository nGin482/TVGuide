from database import insert_into_showlist_collection, remove_show_from_list
from aux_methods import show_list_for_message, get_today_date
from log import compare_dates
from discord.ext import tasks
import discord
import json
import os

class Hermes(discord.Client):
    async def on_ready(self):
        print('Logged in as', self.user)
        status = compare_dates()
        print(status)
        
        with open('today_guide/' + get_today_date() + '.json') as guide_file:
            guide_data = json.load(guide_file)
        
        guide_message = compose_guide_message(guide_data['FTA'], guide_data['BBC'])

        if status:
            self.send_guide(guide_message)

    async def send_message_to_ngin(self, message):
        """
        Send a given message to user nGin via Direct Message
        """
        ngin = await self.fetch_user(int(os.getenv('NGIN')))

        await ngin.send(message)
    
    async def send_guide(self, guide):
        """
        Send today's guide via the TVGuide channel
        """
        await self.wait_until_ready()
        tvguide_channel = self.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
        try:
            await tvguide_channel.send(guide)
        except AttributeError:
            await self.send_message_to_ngin('The channel resolved to NoneType so the message could not be sent')
        await self.close()
    
    async def on_message(self, message):
        if message.author == self.user:
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

def compose_guide_message(fta_shows, bbc_shows):
    """
    toString function that writes the shows, times, channels and episode information (if available) via natural language
    :return: the to-string message
    """
    from datetime import datetime
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
    message = weekdays[message_date.weekday()] + " " + get_today_date() + " TVGuide\n"

    # Free to Air
    message = message + "\nFree to Air:\n"
    if len(fta_shows) == 0:
        message = message + "Nothing on Free to Air today\n"
    else:
        for show in fta_shows:
            time = show['time']
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
            time = show['time']
            if show['episode_info']:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (Series " + show['series_num'] + ", Episode " + show['episode_num'] + ")\n\n"
            else:
                message = message + time + ": " + show['title'] + " is on " + show['channel'] + \
                          " (" + show['episode_title'] + ")\n\n"
            if show['repeat']:
                message = message[:-2] + "(Repeat)\n\n"

    return message