from pymongo import MongoClient
mongo_client = MongoClient()
db = mongo_client.destiny
coll = db.users
