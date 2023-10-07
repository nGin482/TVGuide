from services.hermes.hermes import hermes
from services.hermes.utilities import send_message

@hermes.event
async def on_ready():
    print('Logged in as', hermes.user)

@hermes.event
async def on_db_rollback():
    send_message('The RecordedShows collection has been rolled back.')

@hermes.event
async def on_show_not_processed(show: str, err: str):
    message = f'A GuideShow object was not able to be processed.\nGuideShow: {show}.\nError: {err}'
    send_message(message)

@hermes.event
async def on_db_not_connected(err: str):
    message = f'Having trouble connecting to the database.\nError: {err}'
    send_message(message)