
from pymongo import MongoClient
from connection.config import settings


def get_db_conn() -> MongoClient:
    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB]
   