from pymongo.collection import Collection
from pymongo.database import Database
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus
import datetime



def fetch_logs(collection: Collection,start: datetime,end: datetime
               ) -> list[VaultPadlockStatus] | list[VaultPadlockEvents] | list[VaultPadlockMetrics]:
    
    logs = collection.find({"timestamp": {"$gte": start, "$lte": end}}, {"_id": False})
    return list(logs)




### Testing
def all_logs(collection: Collection) -> list[VaultPadlockStatus] | list[VaultPadlockEvents] | list[VaultPadlockMetrics]:
    
    logs = collection.find({"_id": False})
    return list(logs)


# def fetch_metric_logs(collection, start, end):
#     pass

# def fetch_status_logs(collection, start, end):
#     pass

# def fetch_event_logs(collection, start, end):
#     pass