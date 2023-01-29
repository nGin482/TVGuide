from pymongo import MongoClient, errors
import os

def mongo_client():
    try:
        return MongoClient(os.getenv('TVGUIDE_DB'))
    except errors.ConfigurationError as e:
        print('Having trouble connecting to the database.')
        print(e)
        

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