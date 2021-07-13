from pymongo import MongoClient, errors
import os


# Connection to MongoDB database/Cluster

def client():
    client = MongoClient(os.getenv('TVGUIDE_DB'))
    return client

def database():
    db = client().tvguide
    return db


# Handlers for the Show List collection - All shows being searched for

def showlist_collection():
    showlist = database().ShowList
    return showlist

def get_showlist():
    list_of_shows = []
    for show in showlist_collection().find():
        list_of_shows.append(show['show'])
    return list_of_shows

def find_show(show_to_find):
    list_of_shows = get_showlist()
    for show in list_of_shows:
        if show_to_find in show:
            return {'status': True, 'show': show}
    return {'status': False, 'message': 'The show given could not be found in the database.'}

def insert_into_showlist_collection(show):
    try:
        show_document = {
            "show": show
        }
        showlist_collection().insert_one(show_document)
        return {'status': True, 'message': show + ' has been added to the show list.'}
    except errors.PyMongoError as e:
        return {'status': False, 'message': ' There was a problem adding ' + show + ' to the show list.', 'error': e}

def remove_show_from_list(show_to_remove):
    try:
        showlist_collection().delete_one({'show': show_to_remove})
        return {'status': True, 'message': show_to_remove + ' has been removed from the show list.'}
    except errors.PyMongoError as e:
        return {'status': False, 'message': ' There was a problem removing ' + show_to_remove + ' from the show list.', 'error': e}


# Handlers for all recorded data for each show

def recorded_shows_collection():
    recorded_shows = database().RecordedShows
    return recorded_shows


# Handlers for the reminders

def reminder_collection():
    reminders = database().Reminders
    return reminders