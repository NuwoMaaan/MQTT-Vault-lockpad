from pymongo.collection import Collection
from pymongo.database import Database
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus
import datetime
from typing import TypeVar, Type


T = TypeVar("T", VaultPadlockStatus, VaultPadlockEvents, VaultPadlockMetrics)

def fetch_logs(schema: Type[T], collection: Collection, start: datetime,end: datetime) -> list[T]:
    
    cursor = collection.find({"timestamp": {"$gte": start, "$lte": end}}, {"_id": False})
    return [schema(**doc) for doc in cursor]

# def fetch_metric_logs(collection, start, end):
#     pass

# def fetch_status_logs(collection, start, end):
#     pass

# def fetch_event_logs(collection, start, end):
#     pass