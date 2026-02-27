from fastapi import APIRouter, HTTPException
from connection.database import get_db_conn
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus
    

router = APIRouter()


@router.get("/metrics", response_model=VaultPadlockMetrics)
def get_metrics_logs():
    db = get_db_conn
    collection = db["metrics"]
    pass


@router.get("/status", response_model=VaultPadlockStatus)
def get_status_logs():
    db = get_db_conn()
    collection = db["status"]
    pass

@router.get("/events", response_model=VaultPadlockEvents)
def get_status_logs():
    db = get_db_conn()
    collection = db["events"]
    pass
