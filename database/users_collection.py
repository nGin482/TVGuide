from pymongo import errors, ReturnDocument
from database.mongo import database
from aux_methods.helper_methods import get_today_date
import bcrypt
import uuid
import json
import os

def users_collection():
    """
    Return the `Collection` object to query registered users\n
    Return an empty `list` if the database is None 
    """
    db = database()
    if db is not None:
        return db.get_collection('Users')
    else:
        return []

def get_all_users() -> list:
    """Return a list of all registered users"""
    
    if type(users_collection()) is list:
        return []
    users_list = []
    for record in users_collection().find():
        del record['_id']
        users_list.append(record)
    return users_list

def get_user(username: str) -> dict:
    for user in get_all_users():
        if username == user['username']:
            return {'status': True, 'user': user}
    return {'status': False, 'message': 'This user does not exist.'}

def create_user(user_details: dict) -> dict:
    """
    Create a new user with the given details
    """
    
    user = {
        'userID': str(uuid.uuid4()),
        'username': user_details['username'],
        'password': bcrypt.hashpw(user_details['password'].encode(), bcrypt.gensalt(rounds=13)).decode(),
        'searchList': [],
        'reminders': [],
        'role': 'user'
    }

    try:
        inserted_user = users_collection().insert_one(user)
        if inserted_user.inserted_id:
            return {'status': True}
        else:
            return {'status': False, 'message': 'The server encountered difficulties in registering a new user. Try again.'}   
    except AttributeError:
        return {'status': False, 'message': 'The server encountered difficulties in registering a new user. Try again.'}
    except errors.ServerSelectionTimeoutError as e:
        print(e)
        return {'status': False, 'message': 'Server Selection Timeout Error'}

def check_user_credentials(creds: dict) -> dict:
    
    user = get_user(creds['username'])
    if user['status']:
        user = user['user']
        if bcrypt.checkpw(creds['password'].encode(), user['password'].encode()):
            return {'status': True, 'user': user}
    return {'status': False}

def change_password(user: str, new_password: str) -> dict:
    """
    Change the given user's password to the new one given
    """
    try:
        updated_user_password: dict = users_collection().find_one_and_update(
            {'username': user},
            {'$set': {'password': bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=13)).decode()}},
            return_document=ReturnDocument.AFTER
        )
        return {'status': True, 'message': 'Your password was changed.'}
    except errors.PyMongoError as e:
        return {'status': False, 'message': 'Your password was not changed.'}

def get_user_shows(user: str) -> dict:
    """
    If the user exists, return a `list` of show IDs that the user is interested in.\n
    If not, return the `dict` from the user check
    """

    user_exists = get_user(user) # Check if the user exists
    if user_exists['status']:
        return {'status': True, 'searchList': user_exists['user']['searchList']}
    return user_exists

def get_tvguide_for_user(user: str) -> list:
    """
    Search the TV Guide for the shows that a given user is interested in
    """

    user_search_list = get_user_shows(user) # Find what shows the user is interested in
    if user_search_list['status']:
        try:
            with open('today_guide/' + get_today_date('string') + '.json') as fd:
                guide = json.load(fd)
            
            user_shows = [show for show in guide['FTA'] if show['title'] in user_search_list['searchList']]
            user_shows.extend([show for show in guide['BBC'] if show['title'] in user_search_list['searchList']])
            
            return user_shows
        except FileNotFoundError:
            return []
    else:
        return user_search_list

def add_show_for_user(user: str, show: str) -> dict:
    """
    Add a show to search for a given user
    """
    
    user_show = users_collection().find_one_and_update(
        {'username': user},
        {'$push': {'searchList': show}},
        return_document=ReturnDocument.AFTER
    )
    print(user_show)
    try: 
        if show in user_show['searchList']:
            return {'status': True, 'message': '%s has been added to your list.' % show}
        else:
            return {'status': False, 'message': '%s was unable to be added to your search list.' %show}
    except errors.WriteError:
        return {'status': False, 'message': '%s was unable to be added to your search list.' %show, 'error': 'The server is currently having trouble updating the database.'}
    except TypeError:
        if user_show is None:
            return {'status': False, 'message': 'No user could be found with the given username.'}

def remove_show_for_user(user: str, show: str) -> dict:
    """
    Remove a given show from the user's search list.
    """
    
    user_show = users_collection().find_one_and_update(
        {'username': user},
        {'$pull': {'searchList': show}},
        return_document=ReturnDocument.AFTER
    )
    print(user_show)
    try: 
        if show not in user_show['searchList']:
            return {'status': True, 'message': '%s has been removed from your search list.' % show, 'updated_searchList': user_show['searchList']}
        else:
            return {'status': False, 'message': '%s was unable to be added to your search list.' %show}
    except errors.WriteError:
        return {'status': False, 'message': '%s was unable to be added to your search list.' %show, 'error': 'The server is currently having trouble updating the database.'}
    except TypeError:
        if user_show is None:
            return {'status': False, 'message': 'No user could be found with the given username.'}

def add_reminder_for_user(user: str, reminderID: str) -> dict:
    """
    Allocate the `reminderID` generated from creating a `Reminder` document to the given user.\n
    Return the status of the insert.
    """
    # TODO: It is possible to allocate a duplicate Reminder for the same show without a reasonable check
    
    add_reminder = users_collection().find_one_and_update(
        {'username': user},
        {'$push': {'reminders': reminderID}},
        return_document=ReturnDocument.AFTER
    )
    if add_reminder:
        return {'status': True, 'message': 'The specified reminder has been allocated to the given user.'}
    else:
        return {'status': False, 'message': 'The user could not be found.'}

def remove_reminder_for_user(user: str, reminderID: str) -> dict:
    """
    Remove a `Reminder` by the given `ID` from the list of `Reminder`s attached to the given `User`
    """
    remove_reminder: dict = users_collection().find_one_and_update(
        {'username': user},
        {'$pull': {'reminders': reminderID}},
        return_document=ReturnDocument.AFTER
    )

    if remove_reminder:
        return {'status': True, 'message': 'The reminder has been removed.'}
    else:
        return {'status': False, 'message': 'The user could not be found.'}