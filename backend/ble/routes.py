from fastapi import APIRouter, Query, Depends
from connection.database import get_db_conn
from ble.schemas import BleToken
from ble.repository import store_token, get_token
from auth.security.dependencies import require_token
from datetime import datetime
    
COLLECTION = "ble token"
router = APIRouter()

@router.get("/token", dependencies=[Depends(require_token)], response_model=[BleToken])
def get_tokens(local_name: str = Query(..., description="local name of the BLE device")):
    db = get_db_conn()
    collection = db[COLLECTION]

    return get_token(collection, local_name)

@router.post("/token", dependencies=[Depends(require_token)])
def store_tokens(payload: BleToken):
    db = get_db_conn()
    collection = db[COLLECTION]

    return store_token(collection, payload)


# class StoreToken(BaseModel):
#     id: str
#     token: str
#     UUID: str
#     localname: str
#     timestamp: datetime