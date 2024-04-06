from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from dotenv import load_dotenv
import os

from database.DatabaseService import DatabaseService

if os.environ['PYTHON_ENV'] == 'testing':
    load_dotenv('.env.local.test')
elif os.environ['PYTHON_ENV'] == 'development':
    load_dotenv('.env.local.dev')
else:
    load_dotenv('.env')


database = os.getenv('DATABASE_NAME')
database_connection = os.getenv('TVGUIDE_DB')
database_service = DatabaseService(database_connection, database)

scheduler = AsyncIOScheduler()
mongo_jobstore = MongoDBJobStore(database=database, collection='Jobs', client=database_service._mongo_connection)
scheduler.add_jobstore(mongo_jobstore)
