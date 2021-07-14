from pymongo import MongoClient, errors
from datetime import date
import json
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

def get_all_recorded_shows():
    all_recored_shows = []
    for recorded_show in recorded_shows_collection().find():
        all_recored_shows.append(recorded_show)
    return all_recored_shows

def get_one_recorded_show(show):
    recorded_shows = get_all_recorded_shows()
    for recorded_show in recorded_shows:
        if show == recorded_show['show']:
            return {'status': True, 'show': recorded_show}
    return {'status': False, 'message': 'It does not look like this show has been recorded. Are you sure the show given is correct and is being recorded?'}

def insert_new_recorded_show(new_show):

    # check if insert is successful
    
    recorded_show_document = {
        'show': new_show['title'],
        'seasons': []
    }
    season_object = {
        'season number': 'Unknown',
        'episodes': [
            {
                'episode number': '',
                'episode title': '',
                'channels': [new_show['channel']],
                'first air date': date.today().strftime('%d-%m-%Y'),
                'repeat': False
            }
        ]
    }
    if 'series_num' in new_show.keys():
        season_object['season number'] = new_show['series_num']
        season_object['episodes'][0]['episode number'] = new_show['episode_num']
    if 'episode_title' in new_show.keys():
        season_object['episodes'][0]['episode title'] = new_show['episode_title']
    
    recorded_show_document['seasons'].append(season_object)
    print(recorded_show_document)
    recorded_shows_collection().insert_one(recorded_show_document)

def insert_new_season(show):
    season_object = {
        'season number': 'Unknown',
        'episodes': [
            {
                'episode number': '',
                'episode title': '',
                'channels': [show['channel']],
                'first air date': date.today().strftime('%d-%m-%Y'),
                'repeat': False
            }
        ]
    }
    if 'series_num' in show.keys():
        season_object['season number'] = show['series_num']
        season_object['episodes'][0]['episode number'] = show['episode_num']
    if 'episode_title' in show.keys():
        season_object['episodes'][0]['episode title'] = show['episode_title']

    recorded_shows_collection().update({'show': show['title']}, {'$push': {'seasons': season_object}})


# Handlers for the reminders

def reminder_collection():
    reminders = database().Reminders
    return reminders