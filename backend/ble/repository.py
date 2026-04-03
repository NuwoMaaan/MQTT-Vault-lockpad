from ble.schemas import BleToken
from pymongo.collection import Collection

def get_token(collection: Collection, local_name: str) -> BleToken | None:
    cursor = collection.find_one({"local_name": local_name}, {"_id": 0})
    if cursor:
        return BleToken(**cursor)
    
    return None

def store_token(collection: Collection, token: BleToken) -> None:
    collection.update_one({"local_name": token.local_name}, {"$set": token.model_dump()}, upsert=True)
