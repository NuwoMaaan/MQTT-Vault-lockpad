from ble.schemas import BleData
from pymongo.collection import Collection

def get_data(collection: Collection) -> BleData | None:
    cursor = collection.find_one({}, { "_id": 0 })
    if cursor:
        return BleData(**cursor)
    
    return None

def store_data(collection: Collection, ble_data: BleData) -> None:
    doc = ble_data.model_dump(mode="json")
    collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)