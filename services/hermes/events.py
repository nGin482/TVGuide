from discord import File

from services.hermes.hermes import hermes
from services.hermes.utilities import send_message

@hermes.event
async def on_ready():
    print('Logged in as', hermes.user)

@hermes.event
async def on_db_rollback():
    await send_message('The RecordedShows collection has been rolled back.')

@hermes.event
async def on_show_not_processed(show: str, err: Exception):
    message = f'A GuideShow object was not able to be processed.\nGuideShow: {show}.\nError: {type(err)} {str(err)}'
    await send_message(message)

@hermes.event
async def on_episode_not_updated(show: str, season_number: int, episode_number: int = 0, episode_title: str = ''):
    episode = episode_title if not episode_number else f'{episode_number}, {episode_title}'
    message = f'Season {season_number}, Episode {episode} of {show} was not updated'
    await send_message(message)    

@hermes.event
async def on_db_not_connected(err: str):
    message = f'Having trouble connecting to the database.\nError: {err}'
    await send_message(message)

@hermes.event
async def on_guide_data_fetch_failed(error: str):
    await send_message(f'There was a problem fetching the guide data.\n Error: {error}')


@hermes.event
async def on_shows_collected():
    file = File("backup/shows.json", "All Shows.json")

    await send_message("The list of shows collected", file)