from database.DatabaseService import DatabaseService
from database.mongo import mongo_client
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')

database_service = DatabaseService(mongo_client().get_database('tvguide'))
