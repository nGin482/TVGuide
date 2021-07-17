from pymongo import MongoClient, errors, ReturnDocument
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
    
    check_show = get_one_recorded_show(new['title'])
    if check_show['status']:
        return {'status': False, 'message': 'This show is already being recorded'}
    else:    
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

def insert_new_episode(show):
    episode_object = {
        'episode number': '',
        'episode title': '',
        'channels': [show['channel']],
        'first air date': date.today().strftime('%d-%m-%Y'),
        'repeat': False
    }

    if 'episode_num' in show.keys():
        episode_object['episode number'] = show['episode_num']
    if 'episode_title' in show.keys():
        episode_object['episode title'] = show['episode_title']

    try:
        if 'series_num' in show.keys():
            recorded_shows_collection().update({'show': show['title'], 'seasons.season number': show['series_num']}, {'$push': {'seasons.$.episodes': episode_object}})
        else:
            recorded_shows_collection().update({'show': show['title'], 'seasons': 'Unknown'}, {'$push': {'episodes': episode_object}})
        return {'status': True, 'message': 'The episode has been added to ' + show['title'] + "'s list of episodes."}
    except errors.WriteError as err:
        return {'status': False, 'message': 'An error occurred when trying to add this episode.', 'error': err}

def mark_as_repeat(show):
    
    try:
        if 'series_num' in show.keys():
            updated_show = recorded_shows_collection().find_one_and_update(
                {'show': show['title']},
                {'$set': {'seasons.$[season].episodes.$[episode].repeat': True}},
                upsert = False,
                array_filters = [
                    {'season.season number': show['series_num']},
                    {'episode.episode number': show['episode_num']}
                ],
                return_document = ReturnDocument.AFTER
            )
            
            updated_season = list(filter(lambda season: season['season number'] == show['series_num'], updated_show['seasons']))[0]
            updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], updated_season['episodes']))[0]
            
            if updated_episode['repeat']:
                return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': updated_episode}
            else:
                return {'status': False, 'message': 'The episode has not been marked as a repeat.'}
        else:
            updated_show = recorded_shows_collection().find_one_and_update(
                {'show': show['title']},
                {'$set': {'seasons.$[season].episodes.$[episode].repeat': True}},
                upsert = False,
                array_filters = [
                    {'season.season number': 'Unknown'},
                    {'episode.episode title': show['episode title']}
                ],
                return_document = ReturnDocument.AFTER
            )
            updated_season = list(filter(lambda season: season['season number'] == 'Unknown', updated_show['seasons']))[0]
            updated_episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], updated_season['episodes']))[0]
            
            if updated_episode['repeat']:
                return {'status': True, 'message': 'The episode has been marked as a repeat.', 'episode': updated_episode}
            else:
                return {'status': False, 'message': 'The episode has not been marked as a repeat.'}
    except errors.WriteError as err:
        return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err}
    except TypeError as err:
        return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err}

def add_channel(show):

    if not check_channel(show):
        try:
            if 'series_num' in show.keys():
                updated_show = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$push': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    upsert = True,
                    array_filters = [
                        {'season.season number': show['series_num']},
                        {'episode.episode number': show['episode_num']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
                
                updated_season = list(filter(lambda season: season['season number'] == show['series_num'], updated_show['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], updated_season['episodes']))[0]
                
                if show['channel'] in updated_episode['channels']:
                    return {'status': True, 'message': 'The channel has been added to the list for this episode.', 'episode': updated_episode}
                else:
                    return {'status': False, 'message': 'The channel has not been added.'}
            else:
                updated_show = recorded_shows_collection().find_one_and_update(
                    {'show': show['title']},
                    {'$push': {'seasons.$[season].episodes.$[episode].channels': show['channel']}},
                    upsert = True,
                    array_filters = [
                        {'season.season number': 'Unknown'},
                        {'episode.episode title': show['episode_title']}
                    ],
                    return_document = ReturnDocument.AFTER
                )
                updated_season = list(filter(lambda season: season['season number'] == 'Unknown', updated_show['seasons']))[0]
                updated_episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], updated_season['episodes']))[0]
                
                if show['channel'] in updated_episode['channels']:
                    return {'status': True, 'message': 'The channel has been added to the list for this episode.', 'episode': updated_episode}
                else:
                    return {'status': False, 'message': 'The channel has not been added.'}
        except errors.WriteError as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err}
        except errors.OperationFailure as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err}
        except TypeError as err:
            return {'status': False, 'message': 'An error occurred when trying to mark this episode as a repeat.', 'error': err}
    else:
        return {'status': False, 'message': 'The channel given is already listed.'}

def check_channel(show):
    recorded_show = get_one_recorded_show(show['title'])
    if recorded_show['status']:
        result = recorded_show['show']['seasons']
    
    if 'series_num' in show.keys():
        season = list(filter(lambda season: season['season number'] == show['series_num'], result))[0]
        episode = list(filter(lambda episode: episode['episode number'] == show['episode_num'], season['episodes']))[0]
    else:
        season = list(filter(lambda season: season['season number'] == 'Unknown', result))[0]
        episode = list(filter(lambda episode: episode['episode title'] == show['episode_title'], season['episodes']))[0]
    
    if show['channel'] in episode['channels']:
        return True
    else:
        return False


# Handlers for the reminders

def reminder_collection():
    reminders = database().Reminders
    return reminders