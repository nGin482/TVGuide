from discord.ext.commands import Bot, DefaultHelpCommand

hermes = Bot(command_prefix='$', help_command=DefaultHelpCommand())


from services.hermes import events
from services.hermes import commands
