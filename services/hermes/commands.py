from datetime import datetime
from discord import Message
from discord.ext.commands import Context
from sqlalchemy.orm import Session

from aux_methods.helper_methods import parse_date_from_command
from data_validation.validation import Validation
from database import engine
from database.models.GuideModel import Guide
from database.models.SearchItemModel import SearchItem
from database.models.ShowDetailsModel import ShowDetails
from database.models.ShowEpisodeModel import ShowEpisode
from exceptions.DatabaseError import DatabaseError, SearchItemAlreadyExistsError
from log import get_date_from_tvguide_message
from services.hermes.hermes import hermes
from services.hermes.ui_components.DropdownView import DropdownView
from services.tvmaze import tvmaze_api


@hermes.command()
async def show_list(ctx: Context):
    session = Session(engine)

    message = "The Search List includes:\n"
    for search_item in SearchItem.get_active_searches(session):
        message += f"* {search_item.show}\n"
    await ctx.send(message)
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
    from config import tvguide_scheduler

    guide_date = Validation.get_current_date() if date is None else parse_date_from_command(date)
    session = Session(engine, expire_on_commit=False)
    
    guide = Guide(guide_date, session)
    guide.create_new_guide(tvguide_scheduler)
    guide_message, reminders_message, events_message = (
        guide.compose_message(),
        guide.compose_reminder_message(),
        guide.compose_events_message()
    )
    await hermes.send_guide_message(guide_message, reminders_message, events_message)

@hermes.command()
async def send_guide_record(ctx: Context, date_to_send: str):
    session = Session(engine)

    convert_date = parse_date_from_command(date_to_send)
    
    guide = Guide.get_date(convert_date, session)

    if guide is not None:
        guide.get_shows(session)
        await ctx.send(guide.compose_message())
    else:
        await ctx.send(f"A Guide record for {convert_date.strftime('%d/%m/%Y')} could not be found.")
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

@hermes.command()
async def view_scheduled_reminders(ctx: Context):
    from config import tvguide_scheduler

    reminders_message = "## Reminders\n"

    scheduled_jobs = tvguide_scheduler.get_jobs()
    scheduled_reminders = [
        job
        for job in scheduled_jobs
        if job.id != "TVGuide Message"
    ]

    if len(scheduled_reminders) == 0:
        reminders_message += "* There are no reminders for today"
    else:
        for job in scheduled_reminders:
            (show_title, start_time) = tvguide_scheduler.parse_job_id(job.id)
            parsed_start_time = datetime.strptime(
                start_time,
                "%Y-%m-%d %H:%M:%S"
            )
            message = f"{show_title} is on at {parsed_start_time.strftime("%H:%M")}. "
            message += f"You will be reminded at {job.next_run_time.strftime("%H:%M")}"
            reminders_message += f"* {message}\n"

    await ctx.send(reminders_message)

@hermes.command()
async def create_scheduled_reminder(ctx: Context):
    from config import tvguide_scheduler

    session = Session(engine)
    current_date = Validation.get_current_date()
    
    guide = Guide.get_date(current_date, session)

    if not guide:
        await ctx.send(f"Unable to find a guide for {current_date}")
    else:
        guide.get_shows()
        view = DropdownView(
            tvguide_scheduler,
            "create_reminder",
            guide_episodes=guide.fta_shows,
            session=session
        )
        await ctx.send(view=view)

@hermes.command()
async def reschedule_reminder(ctx: Context):
    from config import tvguide_scheduler

    session = Session(engine)
    current_date = Validation.get_current_date()

    guide = Guide.get_date(current_date, session)
    if not guide:
        await ctx.send(f"Unable to find a guide for {current_date}")
    else:
        guide.get_shows()
        view = DropdownView(
            tvguide_scheduler,
            "reschedule_reminder",
            reminders=tvguide_scheduler.get_jobs(),
            guide_episodes=guide.fta_shows,
        )
        await ctx.send(view=view)

@hermes.command()
async def remove_scheduled_reminder(ctx: Context):
    from config import tvguide_scheduler

    scheduled_jobs = tvguide_scheduler.get_jobs()
    scheduled_reminders = [
        job
        for job in scheduled_jobs
        if job.id != "TVGuide Message"
    ]
    if len(scheduled_reminders) == 0:
        await ctx.send("There are no reminders scheduled today")
    else:
        view = DropdownView(
            tvguide_scheduler,
            "remove_reminder",
            reminders=scheduled_reminders
        )
        await ctx.send(view=view)

