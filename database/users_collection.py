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

def get_user(user_id: str):
    pass

def create_user(user_details: dict) -> dict:
    """
    Create a new user with the given details
    """
    
    user = {
        'userID': str(uuid.uuid4()),
        'username': user_details['username'],
        'password': bcrypt.hashpw(user_details['password'].encode(), bcrypt.gensalt(rounds=13)).decode(),
        'shows': [],
        'reminders': []
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