from discord.ext.commands import Bot, DefaultHelpCommand
from dotenv import load_dotenv

load_dotenv('.env')
hermes = Bot(command_prefix='$', help_command=DefaultHelpCommand())


from services.hermes import events
from services.hermes import commands
