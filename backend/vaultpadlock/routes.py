from fastapi import APIRouter, Query, Depends
from auth.models.permissions import Scope
from connection.database import get_db_conn
from vaultpadlock.schemas import VaultPadlockEvents, VaultPadlockMetrics, VaultPadlockStatus, TopicEndpoints
from vaultpadlock.repository import fetch_logs
from auth.security.dependencies import require_scope
from datetime import datetime
from typing import List
    

router = APIRouter()

RequireStatusRead = Depends(require_scope(Scope.VAULT_STATUS_READ))
RequireMetricsRead = Depends(require_scope(Scope.VAULT_METRICS_READ))
RequireEventsRead = Depends(require_scope(Scope.VAULT_EVENTS_READ))

@router.get("/metrics", dependencies=[RequireMetricsRead], response_model=List[VaultPadlockMetrics])
def get_metrics_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.metrics]

    return fetch_logs(VaultPadlockMetrics, collection, start, end)


@router.get("/status", dependencies=[RequireStatusRead], response_model=List[VaultPadlockStatus])
def get_status_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.status]

    return fetch_logs(VaultPadlockStatus, collection, start, end)


@router.get("/events", dependencies=[RequireEventsRead], response_model=List[VaultPadlockEvents])
def get_event_logs(
    start: datetime = Query(..., description="Start time (ISO format)"),
    end: datetime = Query(..., description="End time (ISO format)")
):
    db = get_db_conn()
    collection = db[TopicEndpoints.events]

    return fetch_logs(VaultPadlockEvents, collection, start, end)

