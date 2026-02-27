import time
from pymongo import MongoClient, errors
from config import settings

URI = settings.URI
DB = settings.DB
COLLECTION = settings.COLLECTION

def connect_mongo(uri, max_retries=3, delay=10) -> MongoClient:
    retries = 0
    while True:
        try:
            print("Trying to connect to MongoDB...")
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("Connected to MongoDB!")
            return client
        except (errors.ServerSelectionTimeoutError, errors.ConnectionFailure) as e:  
            retries += 1
            print(f"MongoDB connection error: {e}. Retrying in {delay} seconds...")
            if max_retries and retries >= max_retries:
                raise Exception("Max retries reached, could not connect to MongoDB.")
            time.sleep(delay)

def get_db_conn() -> MongoClient:
    try:
        mongo_client = connect_mongo(settings.URI)
        return mongo_client["VaultPadlock"]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

