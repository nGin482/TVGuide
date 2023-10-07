from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from database.DatabaseService import DatabaseService
from database.mongo import mongo_client

load_dotenv('.env')

database_service = DatabaseService(mongo_client().get_database('tvguide'))
scheduler = AsyncIOScheduler()
