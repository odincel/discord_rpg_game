import pymongo
import os

def get_database():
    client = pymongo.MongoClient(os.environ("DB_TOKEN"))
    return client