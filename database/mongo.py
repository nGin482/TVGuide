from pymongo import MongoClient, errors
import sys
import os

def mongo_client(connection: str):
    try:
        return MongoClient(connection)
    except (errors.ConfigurationError, errors.ServerSelectionTimeoutError) as e:
        from services.hermes.hermes import hermes
        print('Having trouble connecting to the database.')
        print(e)
        hermes.dispatch('db_not_connected', str(e))
        
def db_connection_string():
    if len(sys.argv) > 1 and '--local-db' in sys.argv[1]:
        return os.getenv('LOCAL_DB')
    else:
        return os.getenv('TVGUIDE_DB')

def database():
    mongo = mongo_client()
    if mongo is not None:
        return mongo.get_database('tvguide')
    else:
        return None

def recorded_shows_collection():
    db = database()
    if db is not None:
        recorded_shows = db.get_collection('RecordedShows')
        return recorded_shows
    else:
        return []