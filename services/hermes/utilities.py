from datetime import datetime
from discord import TextChannel, File
import os
import re

from services.hermes.hermes import hermes

async def send_channel_message(message: str, file: File = None):
    if os.getenv('PYTHON_ENV') == 'development' or os.getenv('PYTHON_ENV') == 'testing':
        channel_id = int(os.getenv('DEV_CHANNEL'))
    else:
        channel_id = int(os.getenv('TVGUIDE_CHANNEL'))
    await hermes.wait_until_ready()
    channel: TextChannel = hermes.get_channel(channel_id)
    if channel is not None:
        if file:
            await channel.send(message, file=file)
        else:
            await channel.send(message)
    else:
        ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
        await ngin.send(f'{message}\nHermes was also unable to send this message through the TVGuide channel')

async def send_ngin_message(message: str, file: File = None):
    ngin_id = int(os.getenv("NGIN"))
    ngin = await hermes.fetch_user(ngin_id)
    
    if file:
        await ngin.send(message, file=file)
    else:
        await ngin.send(message)

def parse_date_from_command(date: str):
    if re.search(r'\d{1,2}(-|\/)\d{1,2}(-|\/)\d{2,4}', date) is not None:
        if '-' in date:
            try:
                return datetime.strptime(date, '%d-%m-%Y')
            except ValueError:
                date_values = date.split('-')
                date_formatted = f'{date_values[0]}-{date_values[1]}-20{date_values[2]}'
                return datetime.strptime(date_formatted, '%d-%m-%Y')
        else:
            try:
                return datetime.strptime(date, '%d/%m/%Y')
            except ValueError:
                date_values = date.split('/')
                date_formatted = f'{date_values[0]}/{date_values[1]}/20{date_values[2]}'
                return datetime.strptime(date_formatted, '%d/%m/%Y')
    else:
        date_search = re.search(r'\d{1,2}(-|\/| )(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)(-|\/| )\d{2,4}', date)
        print(date_search)
        if date_search is not None:
            if '-' in date:
                date_values = date_search.group().split('-')
            elif '/' in date:
                date_values = date_search.group().split('/')
            else:
                date_values = date_search.group().split(' ')
            if len(date_values[1]) == 3:
                month = datetime.strptime(date_values[1], '%b').month
            else:
                month = datetime.strptime(date_values[1], '%B').month
            if len(date_values[2]) == 2:
                year = f'20{date_values[2]}'
            else:
                year = date_values[2]
            return datetime(int(year), month, int(date_values[0]))
        else:
            raise ValueError('The date provided was not in a valid format.')

def get_date_from_tvguide_message(message: str):
    """
    Get the date that TVGuide message was sent. Receives the message as a parameter.
    Returns `None` if the date could not be found in the message
    """
    message_header_search = re.search(r'\d{2}-\d{2}-\d{4} TVGuide', message)
    if message_header_search is not None:
        message_date_search = re.findall(r'\d+', message_header_search.group())
        datetime_values = [int(value) for value in message_date_search]
        date_of_latest_message = datetime(datetime_values[2], datetime_values[1], datetime_values[0])
        return date_of_latest_message
    else:
        return None