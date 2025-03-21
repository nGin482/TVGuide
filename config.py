from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os

load_dotenv('.env')

from database import engine



database = os.getenv('DATABASE_NAME')
database_connection = os.getenv('TVGUIDE_DB')

scheduler = AsyncIOScheduler()
if os.getenv("DB_URL"):
    jobstore = SQLAlchemyJobStore(
        engine=engine,
        tablename='Jobs',
        tableschema=os.getenv('DB_SCHEMA')
    )
    scheduler.add_jobstore(jobstore)
else:
    print("No database connection string to create JobStore")
scheduler.start() # table is created when the scheduler is started

session = Session(engine, expire_on_commit=False)
