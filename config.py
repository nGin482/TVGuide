from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from dotenv import load_dotenv
import os

from database.DatabaseService import DatabaseService
from database.mongo import mongo_client

load_dotenv('.env')


environment = os.getenv('PYTHON_ENV')
database = 'tvguide' if environment == 'production' else 'development'

database_service = DatabaseService(mongo_client().get_database(database))
scheduler = AsyncIOScheduler()
mongo_jobstore = MongoDBJobStore(database=database, collection='Jobs', client=mongo_client())
scheduler.add_jobstore(mongo_jobstore)
