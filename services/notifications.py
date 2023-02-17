from datetime import datetime
from discord import Message
from discord.ext.commands import Bot, Context, DefaultHelpCommand
from dotenv import load_dotenv

from aux_methods.helper_methods import show_list_message, parse_date_from_command
from exceptions.DatabaseError import DatabaseError, SearchItemAlreadyExistsError, SearchItemNotFoundError
from config import database_service
from log import get_date_from_tvguide_message
from guide import compose_message, revert_database_tvguide

load_dotenv('.env')
hermes = Bot(command_prefix='$', help_command=DefaultHelpCommand())


@hermes.event
async def on_ready():
    print('Logged in as', hermes.user)


@hermes.command()
async def show_list(ctx: Context):
    await ctx.send(show_list_message(database_service.get_search_list()))

@hermes.command()
async def add_show(ctx: Context, show: str):
    try:
        database_service.insert_into_showlist_collection(show)
        reply = f'{show} has been added to the SearchList. The list now includes:\n{show_list_message(database_service.get_search_list())}'
    except SearchItemAlreadyExistsError | DatabaseError as err:
        reply = f'Error: {str(err)}. The SearchList has not been modified.'
    await ctx.send(reply)

@hermes.command()
async def remove_show(ctx: Context, show: str):
    try:
        database_service.remove_show_from_list(show)
        reply = f'{show} has been removed from the SearchList. The list now includes:\n{show_list_message(database_service.get_search_list())}'
    except DatabaseError | SearchItemNotFoundError as err:
        reply = f'Error: {str(err)}. The list remains as:\n{show_list_message(database_service.get_search_list())}'
    await ctx.send(reply)

@hermes.command()
async def send_guide_record(ctx: Context, date_to_send: str):
    convert_date = parse_date_from_command(date_to_send).strftime('%d/%m/%Y')
    guide = database_service.get_guide_date(convert_date)
    if guide is not None:
        guide_message = compose_message(guide.fta_shows, guide.bbc_shows, guide.date)
        await ctx.send(guide_message)
    else:
        await ctx.send(f'A Guide record for {convert_date} could not be found.')

@hermes.command()
async def revert_tvguide(ctx: Context, date_to_delete: str = None):
    # if provided, find and delete that message
    # else, search for today's date
    # if none found, send message "could not find TVGuide message"
    
    revert_database_tvguide(database_service)
    message_to_delete = None
    messages: list[Message] = await ctx.history(limit=5).flatten()
    for message in messages:
        message_date = get_date_from_tvguide_message(message.content)
        if message_date is not None and date_to_delete is not None:
            parsed_date_given = parse_date_from_command(date_to_delete)
            if message_date == parsed_date_given:
                message_to_delete = message
                break
        elif message_date is not None and date_to_delete is None:
            if message_date.day == datetime.today().day:
                message_to_delete = message
                break
    if message_to_delete is not None:
        await message_to_delete.delete()
    else:
        await ctx.send('The message to delete could not be found')
    await ctx.send('The TVGuide has been reverted.')
