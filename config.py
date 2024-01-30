from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os

from database.DatabaseService import DatabaseService
from database.mongo import mongo_client

load_dotenv('.env')


environment = os.getenv('PYTHON_ENV')
database = 'tvguide' if environment == 'production' else 'development'

database_service = DatabaseService('production', database)
scheduler = AsyncIOScheduler()
