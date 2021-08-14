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
        self.close()
    
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

