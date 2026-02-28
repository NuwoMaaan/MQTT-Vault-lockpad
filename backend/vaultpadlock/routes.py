from fastapi import APIRouter, Query
from connection.database import get_db_conn
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus, TopicEndpoints
from vaultpadlock.repository import fetch_logs

from datetime import datetime
from typing import List
    

router = APIRouter()


@router.get("/metrics", response_model=List[VaultPadlockMetrics])
def get_metrics_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.metrics]

    return fetch_logs(VaultPadlockMetrics, collection, start, end)


@router.get("/status", response_model=List[VaultPadlockStatus])
def get_status_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.status]

    return fetch_logs(VaultPadlockStatus, collection, start, end)


@router.get("/events", response_model=List[VaultPadlockEvents])
def get_status_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.events]

    return fetch_logs(VaultPadlockEvents, collection, start, end)

