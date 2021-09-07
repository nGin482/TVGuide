from pymongo import errors, ReturnDocument
from database.mongo import database
import bcrypt
import uuid
import os

def users_collection():
    """
    Return the `Collection` object to query registered users\n
    Return an empty `list` if the database is None 
    """
    db = database()
    if db is not None:
        return db.Users
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
        'accessLevel': 'user'
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

def get_user_shows(user:str) -> list | dict:
    """
    Return a list of show IDs that the user is interested in.
    """

    user_exists = get_user(user) # Check if the user exists
    if user_exists['status']:
        return user_exists['user']['searchList']
    return user_exists

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