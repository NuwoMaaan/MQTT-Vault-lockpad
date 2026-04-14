
from fastapi import APIRouter, Depends, HTTPException, status
from auth.models.permissions import Scope
from connection.database import get_db_conn
from ble.schemas import BleData
from ble.repository import store_data, get_data
from auth.security.dependencies import require_scope
    
COLLECTION = "BleData"
router = APIRouter()

RequireBleRead = Depends(require_scope(Scope.BLE_READ))
RequireBleWrite = Depends(require_scope(Scope.BLE_WRITE))

@router.get("/data", dependencies=[RequireBleRead], response_model=BleData)
def get_ble_data():
    db = get_db_conn()
    collection = db[COLLECTION]

    data = get_data(collection)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BLE data not found")
    
    return data

@router.post("/data", dependencies=[RequireBleWrite])
def store_ble_data(payload: BleData):
    db = get_db_conn()
    collection = db[COLLECTION]
    return store_data(collection, payload)
