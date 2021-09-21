from pymongo import MongoClient, errors
from database.mongo import database

# Handlers for the Show List collection - All shows being searched for

def showlist_collection():
    db = database()
    if db is not None:
        showlist = db.get_collection('ShowList')
        return showlist
    else:
        return []

def get_showlist() -> list:
    showlist_col = showlist_collection()
    if showlist_col == []:
        return []
    list_of_shows = []
    for show in showlist_col.find():
        del show['_id']
        list_of_shows.append(show)
    return list_of_shows

def search_list():
    showlist_col = showlist_collection()
    if showlist_col == []:
        return []
    return [show['show'] for show in showlist_col.find()]

def find_show(show_to_find):
    list_of_shows = search_list()
    for show in list_of_shows:
        if show_to_find in show:
            return {'status': True, 'show': show}
    return {'status': False, 'message': 'The show given could not be found in the database.'}

def insert_into_showlist_collection(show):
    check_show_exists = find_show(show)
    if check_show_exists['status']:
        return {'status': False, 'message': show + ' is already being searched for.'}
    else:
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