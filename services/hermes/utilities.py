from discord import TextChannel
import os

from services.hermes.hermes import hermes

async def send_message(message: str):
    if os.getenv('PYTHON_ENV') == 'development' or os.getenv('PYTHON_ENV') == 'testing':
        channel_id = int(os.getenv('DEV_CHANNEL'))
    else:
        channel_id = int(os.getenv('TVGUIDE_CHANNEL'))
    await hermes.wait_until_ready()
    channel: TextChannel = hermes.get_channel(channel_id)
    if channel is not None:
        await channel.send(message)
    else:
        ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
        await ngin.send(f'{message}\nHermes was also unable to send this message through the TVGuide channel')