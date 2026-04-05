
from fastapi import APIRouter, Depends, HTTPException, status
from connection.database import get_db_conn
from ble.schemas import BleData
from ble.repository import store_data, get_data
from auth.security.dependencies import require_token
    
COLLECTION = "BleData"
router = APIRouter()

# Future implementation: have a different Dependency function that checks for specific service permissions instead of generic token

@router.get("/token", dependencies=[Depends(require_token)], response_model=BleData)
def get_ble_data():
    db = get_db_conn()
    collection = db[COLLECTION]

    data = get_data(collection)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BLE data not found")
    
    return data

@router.post("/token", dependencies=[Depends(require_token)])
def store_ble_data(payload: BleData):
    db = get_db_conn()
    collection = db[COLLECTION]
    return store_data(collection, payload)
