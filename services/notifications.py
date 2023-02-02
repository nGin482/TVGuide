from discord.ext.commands import Bot, Context
from dotenv import load_dotenv

from aux_methods.helper_methods import show_list_message
from exceptions.DatabaseError import DatabaseError, SearchItemAlreadyExistsError, SearchItemNotFoundError
from config import database_service

load_dotenv('.env')
hermes = Bot(command_prefix='$')


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
        reply = f'{show} has been added to the list. The list now includes:\n{show_list_message(database_service.get_search_list())}'
    except SearchItemAlreadyExistsError | DatabaseError as err:
        reply = f'Error: {str(err)}. The List has not been modified.'
    await ctx.send(reply)

@hermes.command()
async def remove_show(ctx: Context, show: str):
    try:
        database_service.remove_show_from_list(show)
        reply = f'{show} has been removed from the SearchList. The list now includes:\n' + show_list_message(database_service.get_search_list())
    except DatabaseError | SearchItemNotFoundError as err:
        reply = f'{str(err)}. The list remains as:\n' + show_list_message(database_service.get_search_list())
    await ctx.send(reply)
