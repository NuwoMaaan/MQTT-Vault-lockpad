from ble.schemas import BleData
from pymongo.collection import Collection

def get_data(collection: Collection) -> BleData | None:
    cursor = collection.find_one({}, { "_id": 0 })
    if cursor:
        return BleData(**cursor)
    
    return None

def store_data(collection: Collection, ble_data: BleData) -> None:
    collection.update_one({"uuid": ble_data.UUID}, {"$set": ble_data.model_dump(mode="json")}, upsert=True)