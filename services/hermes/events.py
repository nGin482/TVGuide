from datetime import datetime
from discord import Color, Embed, File
from discord.ext.commands import Context
import logging
import os
import traceback

from config import tvguide_scheduler
from services.hermes.hermes import hermes
from services.hermes.utilities import send_channel_message, send_ngin_message
from utils.LoggingFormatter import logging_handler
from utils.types import ShowData
import utils

logger = logging.getLogger("hermes_events")
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)

@hermes.event
async def on_ready():
    logger.info(f"Logged in as {hermes.user}")
    if not tvguide_scheduler.scheduler_initialised:
        tvguide_scheduler.initialise()
    if os.getenv("PYTHON_ENV") == "production":
        await hermes.schedule_guide_job(tvguide_scheduler)

@hermes.event
async def on_db_rollback():
    await send_channel_message('The RecordedShows collection has been rolled back.')

@hermes.event
async def on_show_not_processed(show: str, err: Exception):
    message = f'A GuideShow object was not able to be processed.\nGuideShow: {show}.\nError: {type(err)} {str(err)}'
    await send_channel_message(message)

@hermes.event
async def on_episode_not_updated(show: str, season_number: int, episode_number: int = 0, episode_title: str = ''):
    episode = episode_title if not episode_number else f'{episode_number}, {episode_title}'
    message = f'Season {season_number}, Episode {episode} of {show} was not updated'
    await send_channel_message(message)    

@hermes.event
async def on_db_not_connected(err: str):
    message = f'Having trouble connecting to the database.\nError: {err}'
    await send_ngin_message(message)

@hermes.event
async def on_guide_data_fetch_failed(error: str):
    await send_channel_message(f'There was a problem fetching the guide data.\n Error: {error}')

@hermes.event
async def on_show_details_not_found(shows_not_found: list[ShowData]):
    import copy
    import json
    import os

    shows_not_found_copy = copy.deepcopy(shows_not_found)
    for show in shows_not_found_copy:
        show['start_time'] = datetime.strftime(show['start_time'], "%d-%m-%Y %H:%M")
        show['end_time'] = datetime.strftime(show['end_time'], "%d-%m-%Y %H:%M")

    if not os.path.isdir("backup"):
        os.mkdir("backup")
    with open("backup/shows_not_found.json", "w+") as fd:
        json.dump(shows_not_found_copy, fd, indent="\t")

    current_date = utils.get_current_date()
    file_name = f"Shows not found - {current_date.strftime('%d-%m-%Y')}.json"
    file = File("backup/shows_not_found.json", file_name)

    await send_ngin_message("The details for these shows were not found", file)


@hermes.event
async def on_shows_collected():
    file = File("backup/shows.json", "All Shows.json")

    await send_ngin_message("The list of shows collected", file)

@hermes.listen()
async def on_command_error(ctx: Context, error: Exception):
    command_name = ctx.command.name
    logger.error(error)
    logger.error(
        f"Error running command '{command_name}'",
        exc_info=(type(error), error, error.__traceback__)
    )
    logger.error(f"Message content: {ctx.message.content}")

    error_message = f"An error occurred processing the command '{command_name}'"

    tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
    tb_text = ''.join(tb_lines)

    if len(tb_text) > 1000:
        tb_text = tb_text[:997] + "..."

    formatted_traceback = f"```py\n{tb_text}\n```"

    embed = Embed(
        title="Command Error!",
        description=error_message,
        color=Color.red(),
        timestamp=ctx.message.created_at
    )
    embed.add_field(name="Error", value=error)
    embed.add_field(name="Original Message", value=ctx.message.content)
    embed.add_field(name="Author", value=ctx.message.author)
    embed.add_field(name="Traceback", value=formatted_traceback, inline=False)

    ngin_id = os.getenv("NGIN")
    ngin = await hermes.fetch_user(ngin_id)

    await ctx.send(error_message)
    await ngin.send(embed=embed)

