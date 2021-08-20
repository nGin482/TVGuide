from pymongo import MongoClient, errors
import os

def client():
    try:
        client = MongoClient(os.getenv('TVGUIDE_DB'))
        return client
    except errors.ConfigurationError as e:
        print('Having trouble connecting to the database.')
        print(e)
        

def database():
    if client() is not None:
        db = client().tvguide
        return db
    else:
        return None