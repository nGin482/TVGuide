from discord import Message, File
from discord.ext.commands import Context
from discord.errors import HTTPException
from sqlalchemy.orm import Session
import os

from aux_methods.helper_methods import parse_date_from_command, split_message_by_time
from config import scheduler
from data_validation.validation import Validation
from database import engine
from database.models.GuideModel import Guide
from database.models.ReminderModel import Reminder
from database.models.SearchItemModel import SearchItem
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from exceptions.DatabaseError import DatabaseError, SearchItemAlreadyExistsError
from log import get_date_from_tvguide_message
from services.hermes.hermes import hermes
from services.tvmaze import tvmaze_api


@hermes.command()
async def migrate(ctx: Context):
    from database.migration import db_migrate
    await ctx.send("Migration started")
    db_migrate()
    await ctx.send("Migration complete")

@hermes.command()
async def show_list(ctx: Context):
    session = Session(engine)

    all_search_items = [search_item.show for search_item in SearchItem.get_active_searches(session)]
    show_list = '\n'.join([all_search_items])
    await ctx.send(f"The Search List includes:\n{show_list}")
    session.close()

@hermes.command()
async def add_show(
    ctx: Context,
    show: str,
    season_start: int = 0,
    season_end: int = 0,
    include_specials: bool = False
):
    session = Session(engine)
    
    try:
        tvmaze_data = tvmaze_api.get_show(show)
        show_details = ShowDetails(
            tvmaze_data['name'],
            tvmaze_data['summary'],
            str(tvmaze_data['id']), 
            tvmaze_data['genres'],
            tvmaze_data['image']['original']
        )
        show_details.add_show(session)

        show_episodes = tvmaze_api.get_show_episodes(
            str(tvmaze_data['id']),
            season_start,
            include_specials=include_specials
        )
        show_episodes = [
            ShowEpisode(
                episode['show'],
                episode['season_number'],
                episode['episode_number'],
                episode['episode_title'],
                episode['summary'],
                show_id=show_details.id
            )
            for episode in show_episodes
        ]
        ShowEpisode.add_all_episodes(show_episodes, session)

        conditions = {}
        if season_start > 0:
            conditions['min_season_number'] = season_start
        if season_end > 0:
            conditions['max_season_number'] = season_end
        max_season_number = max([int(episode.season_number) for episode in show_episodes])
        search_item = SearchItem(tvmaze_data['name'], False, max_season_number, conditions, show_details.id)
        search_item.add_search_item(session)
        all_search_items = [search_item.show for search_item in SearchItem.get_active_searches(session)]
        show_list = '\n'.join([all_search_items])
        reply = f'{show} has been added to the SearchList. The list now includes:\n{show_list}'
    except (SearchItemAlreadyExistsError, DatabaseError) as err:
        reply = f'Error: {str(err)}. The SearchList has not been modified.'
    await ctx.send(reply)
    session.close()

@hermes.command()
async def remove_show(ctx: Context, show: str):
    session = Session(engine)

    search_item = SearchItem.get_search_item(show, session)
    if search_item:
        search_item.delete_search(session)
        all_search_items = [search_item.show for search_item in SearchItem.get_active_searches(session)]
        show_list = '\n'.join([all_search_items])
        reply = f'{show} has been removed from the SearchList. The list now includes:\n{show_list}'
    else:
        reply = f"A search item for '{show}' could not be found"    
    await ctx.send(reply)
    session.close()

@hermes.command()
async def send_guide(ctx: Context, date: str = None):
    guide_date = Validation.get_current_date() if date is None else parse_date_from_command(date)
    session = Session(engine, expire_on_commit=False)
    
    guide = Guide(guide_date, session)
    guide.create_new_guide(scheduler)
    guide_message, reminders_message, events_message = (
        guide.compose_message(),
        guide.compose_reminder_message(),
        guide.compose_events_message()
    )
    ngin = await hermes.fetch_user(int(os.getenv('NGIN')))
    try:
        await ctx.send(guide_message)
    except HTTPException as error:
        if 'In content: Must be 2000 or fewer in length' in error.text:
            bbc_index = guide_message.find('\nBBC:\n')
            fta_message = guide_message[0:bbc_index]
            bbc_message = guide_message[bbc_index:]

            if len(fta_message) > 2000:
                fta_am_message, fta_pm_message = split_message_by_time(fta_message)
                await ctx.send(fta_am_message)
                await ctx.send(fta_pm_message)
            else:
                await ctx.send(fta_message)

            if len(bbc_message) > 2000:
                bbc_am_message, bbc_pm_message = split_message_by_time(bbc_message)
                await ctx.send(bbc_am_message)
                await ctx.send(bbc_pm_message)
            else:
                await ctx.send(bbc_message)
    finally:
        await ctx.send(reminders_message)
        await ngin.send(events_message)
        session.close()

@hermes.command()
async def send_guide_record(ctx: Context, date_to_send: str):
    session = Session(engine)

    convert_date = parse_date_from_command(date_to_send).strftime('%d/%m/%Y')
    
    guide = Guide(convert_date)
    guide.get_shows(session)
    if guide is not None:
        await ctx.send(guide.compose_message())
    else:
        await ctx.send(f'A Guide record for {convert_date} could not be found.')
    session.close()

@hermes.command()
async def revert_tvguide(ctx: Context, date_to_delete: str = None):
    # if provided, find and delete that message
    # else, search for today's date
    # if none found, send message "could not find TVGuide message"
    
    # revert_database_tvguide(database_service)
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
            if message_date.day == Validation.get_current_date().date().day:
                message_to_delete = message
                break
    if message_to_delete is not None:
        await message_to_delete.delete()
    else:
        await ctx.send('The message to delete could not be found')
    await ctx.send('The TVGuide has been reverted.')

# @hermes.command()
# async def recorded_show(ctx: Context, show: str):
#     show_record = database_service.get_one_recorded_show(show)
#     if show_record is not None:
#         await ctx.send(show_record.message_format())
#     else:
#         await ctx.send(f'{show} could not be found in the database')

# @hermes.command()
# async def season_details(ctx: Context, show: str, season: str):
#     show_record = database_service.get_one_recorded_show(show)
#     if show_record is not None:
#         season_record = show_record.find_season(season)
#         if season_record is not None:
#             await ctx.send(season_record.message_format())
#         else:
#             if season == 'Unknown':
#                 await ctx.send(f'{show} does not have an {season} season')
#             else:
#                 await ctx.send(f'{show} does not have {season} seasons')
#     else:
#         await ctx.send(f'{show} could not be found in the database')

@hermes.command()
async def create_reminder(
    ctx: Context,
    show: str,
    reminder_alert: str = 'Before',
    warning_time: str = '3', 
    occasions: str = 'All'
):
    session = Session(engine)

    show_details = ShowDetails.get_show_by_title(show, session)
    reminder_exists = Reminder.get_reminder_by_show(show, session)
    search_item_exists = SearchItem.get_search_item(show, session)
    if not reminder_exists:
        await ctx.send(f'A reminder already exists for {show}')
    elif not search_item_exists:
        await ctx.send(f'A reminder cannot be created for {show} as it is not being searched for.')
    else:
        reminder = Reminder(show, reminder_alert, int(warning_time), occasions, show_details.id)
        reminder.add_reminder(session)
        await ctx.send(f'A reminder has been created for {show}')
    session.close()

@hermes.command()
async def view_reminder(ctx: Context, show: str):
    session = Session(engine)

    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        await ctx.send(reminder.message_format())
    else:
        await ctx.send(f"A reminder for '{show}' could not be found")
    session.close()    

@hermes.command()
async def update_reminder(ctx: Context, show: str, attribute: str, value: str):
    session = Session(engine)

    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        if attribute == 'warning_time':
            value = int(value)
        reminder.update_reminder(attribute, value, session)
        await ctx.send(f"The reminder for '{show}' has been updated. It's details are now:\n{reminder.message_format()}")
    else:
        await ctx.send(f"A reminder for '{show}' could not be found")
    session.close()

@hermes.command()
async def delete_reminder(ctx: Context, show: str):
    session = Session(engine)

    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        reminder.delete_reminder(session)
        await ctx.send(f'The Reminder for {show} has been removed')
    else:
        await ctx.send(f'A Reminder for {show} could not be found')
    session.close()

# @hermes.command()
# async def backup_shows(ctx: Context):
#     database_service.backup_recorded_shows()
#     date = Validation.get_current_date()

#     os.mkdir('database/backups/zip')
#     with ZipFile('database/backups/zip/Shows-Archive.zip', 'w') as zip:
#         for file in os.listdir('database/backups/recorded_shows'):
#             zip.write(f'database/backups/recorded_shows/{file}', arcname=file)
#     shows_zip = File('database/backups/zip/Shows-Archive.zip', f'Shows Archive - {date.strftime("%d/%m/%Y")}.zip')
#     await ctx.send('A backup has been made of the Recorded Shows. This can be found attached.', file=shows_zip)
#     os.remove('database/backups/zip/Shows-Archive.zip')
#     os.rmdir('database/backups/zip')

# @hermes.command()
# async def restore_shows(ctx: Context):
#     os.makedirs('database/restore/recorded_shows')
#     message: Message = ctx.message
#     shows_attachment = message.attachments[0]
#     filename = shows_attachment.filename
#     await shows_attachment.save(f'database/restore/recorded_shows/{filename}')
#     with ZipFile(f'database/restore/recorded_shows/{filename}', 'r') as zip:
#         zip.extractall('database/restore/recorded_shows')

#     database_service.rollback_recorded_shows(directory='restore')

#     for file in os.listdir('database/restore/recorded_shows'):
#         os.remove(f'database/restore/recorded_shows/{file}')
#     os.rmdir('database/restore/recorded_shows')
#     os.removedirs('database/restore')
