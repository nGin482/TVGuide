from apscheduler.triggers.cron import CronTrigger
from discord import TextChannel
from os import getenv

from config import scheduler
from services.hermes.hermes import hermes

async def send_message(message: str):
    await hermes.wait_until_ready()
    tvguide_channel: TextChannel = hermes.get_channel(int(getenv('TVGUIDE_CHANNEL')))
    tvguide_channel.send(message)


if __name__ == '__main__':
    scheduler.add_job(send_message, CronTrigger(hour='17', minute='49'), ['This is a test of APScheduler'])
    scheduler.start()
    hermes.run(getenv('HERMES'))