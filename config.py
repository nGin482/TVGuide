from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from dotenv import load_dotenv
import os

from database.DatabaseService import DatabaseService

load_dotenv('.env')


environment = os.getenv('PYTHON_ENV')

database = 'tvguide' if environment == 'production' else 'development'
database_connection = os.getenv('LOCAL_DB') if environment == 'development' else os.getenv('TVGUIDE_DB')
database_service = DatabaseService(database_connection, database)

scheduler = AsyncIOScheduler()
mongo_jobstore = MongoDBJobStore(database=database, collection='Jobs', client=mongo_client())
scheduler.add_jobstore(mongo_jobstore)
