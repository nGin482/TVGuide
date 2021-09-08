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
    mongo_client = client()
    if mongo_client is not None:
        db = mongo_client.tvguide
        return db
    else:
        return None