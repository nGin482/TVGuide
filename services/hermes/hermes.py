from discord.ext.commands import Bot, DefaultHelpCommand
from dotenv import load_dotenv
import os

if os.environ['PYTHON_ENV'] == 'production':
    load_dotenv('.env')
else:
    load_dotenv('.env.local.dev')
hermes = Bot(command_prefix='$', help_command=DefaultHelpCommand())


from services.hermes import events
from services.hermes import commands
