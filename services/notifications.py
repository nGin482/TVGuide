from datetime import datetime
from discord import Message
from discord.ext.commands import Bot, Context, DefaultHelpCommand
from dotenv import load_dotenv

from aux_methods.helper_methods import show_list_message, parse_date_from_command
from database.models.Reminders import Reminder
from exceptions.DatabaseError import DatabaseError, ReminderNotFoundError, SearchItemAlreadyExistsError, SearchItemNotFoundError, ShowNotFoundError
from config import database_service
from log import get_date_from_tvguide_message
from guide import compose_message, revert_database_tvguide
from data_validation.validation import Validation

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

@hermes.command()
async def recorded_show(ctx: Context, show: str):
    try:
        show_record = database_service.get_one_recorded_show(show)
        await ctx.send(show_record.message_format())
    except ShowNotFoundError as err:
        await ctx.send(f'Error: {str(err)}')

@hermes.command()
async def season_details(ctx: Context, show: str, season: str):
    try:
        show_record = database_service.get_one_recorded_show(show)
        season_record = show_record.find_season(season)
        if season_record is not None:
            await ctx.send(season_record.message_format())
        else:
            if season == 'Unknown':
                await ctx.send(f'{show} does not have an {season} season')
            else:
                await ctx.send(f'{show} does not have {season} seasons')
    except ShowNotFoundError as err:
        await ctx.send(f'Error: {str(err)}')

@hermes.command()
async def create_reminder(ctx: Context, show: str, reminder_alert: str = 'Before', warning_time: str = '3', occassions: str = 'All'):
    try:
        reminder_exists = database_service.get_one_reminder(show)
        if reminder_exists is not None:
            await ctx.send(f'A reminder already exists for {show}')
    except ReminderNotFoundError:
        if show in database_service.get_search_list():
            reminder = Reminder.from_values(show, reminder_alert, int(warning_time), occassions)
            database_service.insert_new_reminder(reminder)
        else:
            await ctx.send(f'A reminder cannot be created for {show} as it is not being searched for.')
        await ctx.send(f'A reminder has been created for {show}')

@hermes.command()
async def view_reminder(ctx: Context, show: str):
    try:
        reminder = database_service.get_one_reminder(show)
        await ctx.send(reminder.message_format())
    except ReminderNotFoundError as err:
        await ctx.send(f'Error: {err}')

@hermes.command()
async def update_reminder(ctx: Context, show: str, attribute: str, value: str):
    try:
        reminder = database_service.get_one_reminder(show)
        if attribute in Validation.valid_reminder_fields():
            if attribute == 'warning_time':
                value = int(value)
            setattr(reminder, attribute, value)
            database_service.update_reminder(reminder)
            await ctx.send(f"The reminder for {show} has been updated. It's details are now:\n{reminder.message_format()}")
        else:
            await ctx.send(f'Error: {attribute} is not a valid property for a reminder')
    except ReminderNotFoundError as err:
        await ctx.send(f'Error: {str(err)}')

@hermes.command()
async def delete_reminder(ctx: Context, show: str):
    try:
        database_service.delete_reminder(show)
        await ctx.send(f'The Reminder for {show} has been removed')
    except ReminderNotFoundError as err:
        await ctx.send(f'Error: {str(err)}')