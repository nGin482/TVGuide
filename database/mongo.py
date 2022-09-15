from pymongo import MongoClient, errors
import os

def client() -> MongoClient:
    try:
        client = MongoClient(os.getenv('TVGUIDE_DB'))
        return client
    except errors.ConfigurationError as e:
        print('Having trouble connecting to the database.')
        print(e)
        

def database():
    mongo_client = client()
    if mongo_client is not None:
        return mongo_client.get_database('tvguide')
    else:
        return None

def showlist_collection():
    db = database()
    if db is not None:
        showlist = db.get_collection('ShowList')
        return showlist
    else:
        return []

def recorded_shows_collection():
    db = database()
    if db is not None:
        recorded_shows = db.get_collection('RecordedShows')
        return recorded_shows
    else:
        return []

def reminders_collection():
    db = database()
    if db is not None:
        reminders = db.get_collection('Reminders')
        return reminders
    else:
        return []