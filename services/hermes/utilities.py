from discord import TextChannel
import os

from services.hermes.hermes import hermes

async def send_message(message: str):
    tvguide_channel: TextChannel = hermes.get_channel(int(os.getenv('TVGUIDE_CHANNEL')))
    await hermes.wait_until_ready()
    if tvguide_channel is not None:
        await tvguide_channel.send(message)
    else:
        ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
        await ngin.send(f'{message}\nHermes was also unable to send this message through the TVGuide channel')