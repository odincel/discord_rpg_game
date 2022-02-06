import pymongo
import os

def get_database():
    client = pymongo.MongoClient("mongodb+srv://onurdincel:iJyXen8whyh6n6DX@cluster0.ogfmw.mongodb.net/Cluster0?retryWrites=true&w=majority")
    return client