from pymongo import MongoClient
import os

def client():
    client = MongoClient(os.getenv('TVGUIDE_DB'))
    return client

def database():
    db = client().tvguide
    return db

def showlist_collection():
    showlist = database().ShowList
    return showlist

def insert_into_showlist_collection(show):
    show_document = {
        "show": show
    }
    showlist_collection().insert_one(show_document)

def recorded_shows_collection():
    recorded_shows = database().RecordedShows
    return recorded_shows

def reminder_collection():
    reminders = database().Reminders
    return reminders