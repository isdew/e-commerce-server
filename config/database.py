import certifi
from pymongo import MongoClient

mongo_uri = "mongodb+srv://admin:admin@cluster0.halsd3t.mongodb.net/"

client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

db = client["E-commerce"]

collection_names = ["user","product","cart"]

collections = {name: db[name] for name in collection_names}
