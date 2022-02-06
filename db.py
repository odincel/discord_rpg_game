import pymongo
import os

def get_database():
    client = pymongo.MongoClient(os.getenv("DB_TOKEN"))
    return client
