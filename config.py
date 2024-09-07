from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
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
jobstore = SQLAlchemyJobStore(url=os.getenv('DB_URL'), tablename='Jobs', tableschema=os.getenv('DB_SCHEMA'))
scheduler.add_jobstore(jobstore)
scheduler.start() # table is created when the scheduler is started
