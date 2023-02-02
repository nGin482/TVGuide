from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')
hermes = Bot(command_prefix='$')


@hermes.event
async def on_ready():
    print('Logged in as', hermes.user)
