from pymongo import MongoClient, errors
import os

def client() -> MongoClient:
    try:
        client = MongoClient(os.getenv('TVGUIDE_DB'))
        return client
    except errors.ConfigurationError as e:
        print('Having trouble connecting to the database.')
        print(e)
        

def database():
    mongo_client = client()
    if mongo_client is not None:
        return mongo_client.get_database('tvguide')
    else:
        return None