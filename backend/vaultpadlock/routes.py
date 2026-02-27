from fastapi import APIRouter, Query
from connection.database import get_db_conn
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus
from vaultpadlock.repository import fetch_logs, all_logs

from datetime import datetime
from typing import List
    

router = APIRouter()


@router.get("/metrics", response_model=List[VaultPadlockMetrics])
def get_metrics_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db["metrics"]
    return fetch_logs(collection, start, end)


@router.get("/status", response_model=List[VaultPadlockStatus])
def get_status_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db["status"]
    return fetch_logs(collection, start, end)

@router.get("/events", response_model=List[VaultPadlockEvents])
def get_status_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db["events"]
    return fetch_logs(collection, start, end)



### Testing
@router.get("/all", response_model=List[VaultPadlockEvents])
def get_all_logs():
    db = get_db_conn()
    collection = db["events"]
    return all_logs(collection)
